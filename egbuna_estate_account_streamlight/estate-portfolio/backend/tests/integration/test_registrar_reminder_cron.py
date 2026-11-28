"""
F-026b — Integration tests for the registrar reminder cron (AC-3 / AC-4).

Exercises the REAL scripts/registrar_reminder_cron.main() against epm_test:
a requirement whose due_date falls inside the lead window must produce
exactly one reminder email and one reminder_log row, and a second run must
produce zero new reminder_log rows (idempotency, AC-4).

The SMTP call itself is mocked — the thing under test is the scheduling and
idempotency logic, not email delivery. Tests clean up every row they create.

The cron's AsyncSessionLocal is patched to a NullPool session factory so no
pooled asyncpg connections leak past the session-scoped event loop. This
replaces the two shallow unit tests (test_cron_script_imports and
test_idempotency_query_structure) that only checked imports / query syntax.
"""
import logging
import os
import re
from datetime import date, timedelta
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.models import AdminAudit, Registrar, RegistrarRequirement, ReminderLog

# Same DSN construction as tests/integration/conftest.py — isolated test database
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '5432')}"
    f"/{os.environ.get('DB_NAME', 'epm_test')}"
)


@pytest.fixture(scope="module")
def cron_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine


@pytest.fixture(scope="module")
def cron_session_factory(cron_engine):
    return async_sessionmaker(
        bind=cron_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture(scope="module")
def patched_cron_session_factory(cron_session_factory):
    """Point the cron's AsyncSessionLocal at the NullPool test session factory."""
    with patch(
        "scripts.registrar_reminder_cron.AsyncSessionLocal",
        new=cron_session_factory,
    ):
        yield cron_session_factory


@pytest_asyncio.fixture
async def reminder_requirement(cron_session_factory, patched_cron_session_factory):
    """Insert (and later clean up) a registrar + requirement in the lead window."""
    registrar = Registrar(name="Cron Test Registrar")
    requirement = RegistrarRequirement(
        task_name="Cron Test Task",
        document_title="Cron Test Document",
        is_required=True,
        sort_order=0,
        due_date=date.today() + timedelta(days=3),  # within default 7-day lead window
    )
    registrar.requirements.append(requirement)

    async with cron_session_factory() as session:
        session.add(registrar)
        await session.commit()
        await session.refresh(registrar)
        await session.refresh(requirement)
        reg_id, req_id = registrar.id, requirement.id

    try:
        yield reg_id, req_id
    finally:
        async with cron_session_factory() as session:
            await session.execute(
                delete(ReminderLog).where(ReminderLog.requirement_id == req_id)
            )
            await session.execute(
                delete(AdminAudit).where(
                    AdminAudit.entity_type == "registrar_requirement",
                    AdminAudit.entity_id == str(req_id),
                )
            )
            await session.execute(
                delete(RegistrarRequirement).where(RegistrarRequirement.id == req_id)
            )
            await session.execute(delete(Registrar).where(Registrar.id == reg_id))
            await session.commit()


@pytest_asyncio.fixture
async def overdue_requirement(cron_session_factory, patched_cron_session_factory):
    """Insert (and later clean up) a registrar + requirement whose due date has passed."""
    registrar = Registrar(name="Cron Test Overdue Registrar")
    requirement = RegistrarRequirement(
        task_name="Cron Test Overdue Task",
        document_title="Cron Test Overdue Document",
        is_required=True,
        sort_order=0,
        due_date=date.today() - timedelta(days=2),  # already past
    )
    registrar.requirements.append(requirement)

    async with cron_session_factory() as session:
        session.add(registrar)
        await session.commit()
        await session.refresh(registrar)
        await session.refresh(requirement)
        reg_id, req_id = registrar.id, requirement.id

    try:
        yield reg_id, req_id
    finally:
        async with cron_session_factory() as session:
            await session.execute(
                delete(ReminderLog).where(ReminderLog.requirement_id == req_id)
            )
            await session.execute(
                delete(AdminAudit).where(
                    AdminAudit.entity_type == "registrar_requirement",
                    AdminAudit.entity_id == str(req_id),
                )
            )
            await session.execute(
                delete(RegistrarRequirement).where(RegistrarRequirement.id == req_id)
            )
            await session.execute(delete(Registrar).where(Registrar.id == reg_id))
            await session.commit()


async def _count_reminder_logs(cron_session_factory, req_id: int) -> int:
    async with cron_session_factory() as session:
        count = await session.scalar(
            select(func.count(ReminderLog.id)).where(ReminderLog.requirement_id == req_id)
        )
    return count or 0


@pytest.mark.asyncio
async def test_cron_sends_and_logs_reminder_for_upcoming_requirement(
    reminder_requirement,
    cron_session_factory,
):
    """A requirement inside the lead window triggers one email + one log row."""
    reg_id, req_id = reminder_requirement

    from scripts.registrar_reminder_cron import main

    with patch(
        "scripts.registrar_reminder_cron.send_email",
        return_value={"status": "sent"},
    ) as mock_send:
        exit_code = await main()

    assert exit_code == 0
    assert mock_send.call_count == 1
    assert mock_send.call_args.kwargs.get("to") == os.environ.get("REMINDER_RECIPIENT_EMAIL", "zubbyik@gmail.com")
    # Exactly one reminder_log row was written
    assert await _count_reminder_logs(cron_session_factory, req_id) == 1

    # An admin_audit entry was written (F-007 pattern, performed_by=NULL)
    async with cron_session_factory() as session:
        audit_count = await session.scalar(
            select(func.count(AdminAudit.id)).where(
                AdminAudit.entity_type == "registrar_requirement",
                AdminAudit.entity_id == str(req_id),
            )
        )
    assert (audit_count or 0) == 1


@pytest.mark.asyncio
async def test_cron_idempotency_second_run_writes_zero_new_reminder_log_rows(
    reminder_requirement,
    cron_session_factory,
):
    """AC-4: running the reminder logic twice against the same requirement/day writes 0 new rows."""
    reg_id, req_id = reminder_requirement

    from scripts.registrar_reminder_cron import main

    with patch(
        "scripts.registrar_reminder_cron.send_email",
        return_value={"status": "sent"},
    ) as mock_send:
        first_run = await main()
        second_run = await main()

    assert first_run == 0
    assert second_run == 0
    # One email total — the second run must not re-send
    assert mock_send.call_count == 1
    # One reminder_log row total — the second run wrote zero new rows
    assert await _count_reminder_logs(cron_session_factory, req_id) == 1


@pytest.mark.asyncio
async def test_cron_with_missing_smtp_config_logs_failure_and_sends_nothing(
    reminder_requirement,
    cron_session_factory,
    caplog,
):
    """AC-1: a broken/incomplete SMTP configuration must never crash the job.

    The real ``send_email`` is exercised (only ``smtplib.SMTP`` is patched) so
    the config guard itself is under test, not a mock of it.
    """
    # Spec: F-026-email-reminder-infrastructure.md | AC-1 | Then the cron logs
    # the failure, exits cleanly, and transmits no email.
    reg_id, req_id = reminder_requirement

    from scripts.registrar_reminder_cron import main

    blank_smtp = {
        "SMTP_HOST": "",
        "SMTP_PORT": "587",
        "SMTP_USER": "",
        "SMTP_PASSWORD": "",
        "SMTP_FROM_ADDRESS": "",
    }

    with (
        patch.dict(os.environ, blank_smtp),
        patch("app.services.email.smtplib.SMTP") as mock_smtp,
        caplog.at_level(logging.INFO),
    ):
        exit_code = await main()

    # Does not crash — the cron contract is exit 0 for handled failures.
    assert exit_code == 0
    # Sends nothing: with incomplete config send_email bails before SMTP.
    mock_smtp.assert_not_called()
    # The failure is logged (summary line) rather than raised. Assert on the
    # LOGGED COUNT instead of the always-true substring "failed=" (Aud 3);
    # other due requirements in shared epm_test only raise this count, so
    # >= 1 is deterministic while "failed=" matched every run.
    summary = re.search(r"completed: sent=\d+, skipped=\d+, failed=(\d+)", caplog.text)
    assert summary, "cron completion summary line missing from logs"
    assert int(summary.group(1)) >= 1

    # The failed attempt is persisted for troubleshooting with the sanitized
    # reason — scoped to THIS fixture's requirement id, never a global count.
    async with cron_session_factory() as session:
        rows = (
            await session.execute(
                select(ReminderLog).where(ReminderLog.requirement_id == req_id)
            )
        ).scalars().all()
    assert len(rows) == 1
    assert rows[0].delivery_status == "failed"
    assert "SMTP configuration incomplete" in (rows[0].error_detail or "")


@pytest.mark.asyncio
async def test_cron_marks_past_due_requirement_as_overdue(
    overdue_requirement,
    cron_session_factory,
):
    """AC-3: a requirement whose due_date has already passed is sent as overdue."""
    # Spec: F-026-email-reminder-infrastructure.md | AC-3 | Then one email is
    # sent and the reminder_log row carries reminder_type='overdue'.
    reg_id, req_id = overdue_requirement

    from scripts.registrar_reminder_cron import main

    with patch(
        "scripts.registrar_reminder_cron.send_email",
        return_value={"status": "sent"},
    ) as mock_send:
        exit_code = await main()

    assert exit_code == 0
    # Scope the call assertions to THIS fixture's requirement (its subject
    # carries the fixture's document_title). epm_test is shared, so a global
    # call_count == 1 would break whenever another due requirement exists (Aud 2).
    fixture_title = "Cron Test Overdue Document"  # fixture's document_title
    fixture_calls = [
        c for c in mock_send.call_args_list
        if fixture_title in (c.kwargs.get("subject") or "")
    ]
    assert len(fixture_calls) == 1
    assert "Overdue" in fixture_calls[0].kwargs["subject"]

    # reminder_log rows for THIS fixture's requirement id only.
    async with cron_session_factory() as session:
        rows = (
            await session.execute(
                select(ReminderLog).where(ReminderLog.requirement_id == req_id)
            )
        ).scalars().all()

    assert len(rows) == 1
    assert rows[0].reminder_type == "overdue"
    assert rows[0].delivery_status == "sent"
