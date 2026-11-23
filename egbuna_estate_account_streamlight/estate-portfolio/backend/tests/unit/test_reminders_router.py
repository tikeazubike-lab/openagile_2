# backend/tests/unit/test_reminders_router.py
"""
F-026b — Router-level tests for the admin reminder endpoints (AC-5 / AC-6 / AC-8).

Covers the gaps left by the existing mock-only coverage:

  AC-5  POST /api/v1/admin/reminders/test-send, valid SMTP → 200 "sent",
        and the reminder_log audit trail is NOT polluted.
  AC-6  POST /api/v1/admin/reminders/test-send, invalid SMTP → 502 with a
        sanitized error (no raw stack trace in the body).
  AC-8  A non-admin user gets 403 on BOTH new endpoints.

All DB and SMTP calls are mocked — no real database or network is touched.
Follows the dependency_overrides pattern used in tests/unit/test_admin_users.py.
"""
import os
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.deps import create_access_token, get_current_user, get_session
from app.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_token(user_id: int = 1, role: str = "admin") -> str:
    return create_access_token(user_id=user_id, role=role)


def make_mock_user(user_id: int = 1, role: str = "admin") -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.username = "zubbyik" if role == "admin" else "reader"
    user.name = "Zubby"
    user.role = role
    user.is_active = True
    user.deleted_at = None
    return user


class _Overrides:
    """Install dependency overrides, then restore whatever was there before.

    Takes a dict because FastAPI keys ``dependency_overrides`` by the
    dependency *callable* — keyword arguments would stringify the keys.
    """

    def __init__(self, overrides: dict):
        self._new = overrides
        self._original = {}

    def __enter__(self):
        for dependency, replacement in self._new.items():
            self._original[dependency] = app.dependency_overrides.get(dependency)
            app.dependency_overrides[dependency] = replacement
        return self

    def __exit__(self, exc_type, exc, tb):
        for dependency, original in self._original.items():
            if original is not None:
                app.dependency_overrides[dependency] = original
            else:
                app.dependency_overrides.pop(dependency, None)
        return False


def _client(role: str = "admin") -> TestClient:
    """TestClient carrying a token; the role is enforced by the real require_admin."""
    client = TestClient(app)
    client.cookies.set("epm_token", make_token(role=role))
    return client


# ===========================================================================
# AC-5 — valid SMTP config: 200 "sent", no reminder_log write
# ===========================================================================

def test_test_send_success_returns_sent_and_writes_no_reminder_log():
    # Spec: F-026-email-reminder-infrastructure.md | AC-5 | Then the endpoint
    # returns 200 {"status": "sent", ...} and writes no reminder_log row.
    mock_user = make_mock_user(role="admin")
    mock_db = AsyncMock()

    with _Overrides({
        get_session: lambda: mock_db,
        get_current_user: lambda: mock_user,
    }), patch(
        "app.services.email.send_email",
        return_value={"status": "sent"},
    ) as mock_send:
        response = _client(role="admin").post("/api/v1/admin/reminders/test-send")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "sent"
    assert body["data"]["recipient"] == os.environ.get(
        "REMINDER_RECIPIENT_EMAIL", "zubbyik@gmail.com"
    )
    # The test-send tool must not touch the audit trail (spec §4).
    assert mock_db.add.call_count == 0
    mock_send.assert_called_once()


# ===========================================================================
# AC-6 — invalid SMTP config: 502, sanitized error, no traceback text
# ===========================================================================

def test_test_send_invalid_smtp_returns_502_without_traceback():
    # Spec: F-026-email-reminder-infrastructure.md | AC-6 | Then a 502 is
    # returned with a sanitized detail string and no raw stack trace exposed.
    mock_user = make_mock_user(role="admin")
    mock_db = AsyncMock()
    sanitized = (
        "SMTP configuration incomplete — check SMTP_HOST, SMTP_USER, "
        "SMTP_PASSWORD, SMTP_FROM_ADDRESS"
    )

    with _Overrides({
        get_session: lambda: mock_db,
        get_current_user: lambda: mock_user,
    }), patch(
        "app.services.email.send_email",
        return_value={"status": "failed", "detail": sanitized},
    ):
        response = _client(role="admin").post("/api/v1/admin/reminders/test-send")

    assert response.status_code == 502
    body = response.json()
    assert sanitized in body["detail"]
    # No leaked internals in the payload (AC-6 explicitly forbids this).
    assert "Traceback" not in response.text
    assert 'File "' not in response.text
    assert "smtplib" not in response.text
    assert mock_db.add.call_count == 0


# ===========================================================================
# AC-8 — non-admin user: 403 on both endpoints
# ===========================================================================

def test_test_send_forbidden_for_non_admin():
    # Spec: F-026-email-reminder-infrastructure.md | AC-8 | Then a non-admin
    # caller receives 403 on POST /admin/reminders/test-send.
    readonly_user = make_mock_user(user_id=2, role="readonly")
    mock_db = AsyncMock()

    with _Overrides({
        get_session: lambda: mock_db,
        get_current_user: lambda: readonly_user,
    }), patch("app.services.email.send_email") as mock_send:
        response = _client(role="readonly").post("/api/v1/admin/reminders/test-send")

    assert response.status_code == 403
    mock_send.assert_not_called()


def test_reminder_log_forbidden_for_non_admin():
    # Spec: F-026-email-reminder-infrastructure.md | AC-8 | Then a non-admin
    # caller receives 403 on GET /admin/reminders/log.
    readonly_user = make_mock_user(user_id=2, role="readonly")
    mock_db = AsyncMock()

    with _Overrides({
        get_session: lambda: mock_db,
        get_current_user: lambda: readonly_user,
    }):
        response = _client(role="readonly").get("/api/v1/admin/reminders/log")

    assert response.status_code == 403
    # The guard rejected the request before the handler queried the DB.
    mock_db.execute.assert_not_called()
