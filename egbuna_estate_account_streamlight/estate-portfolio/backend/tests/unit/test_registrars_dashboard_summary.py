# backend/tests/unit/test_registrars_dashboard_summary.py
"""
F-026 — Unit tests for dashboard_summary completion counting (Part E1).

The endpoint function is called directly with a fake async session (the
pattern used by tests/unit/test_holdings_router.py); no database is touched.

The fake session compiles every statement it receives, so the tests PIN THE
QUERY SHAPE: completed_requirements must be
count(DISTINCT registrar_documents.registrar_requirement_id) — counting
documents inflates completion_pct above 100 when one requirement has several
completed documents (review finding Aud 7 / Rev 1).

Trace: # Spec: F-026-registrar-dashboard.md | AC-1 | Then counts and
completion_pct match the data.
"""
import asyncio
from types import SimpleNamespace

from sqlalchemy.dialects import postgresql

from app.routers.registrars import dashboard_summary


def _compile(stmt) -> str:
    """Render a SQLAlchemy statement as PostgreSQL SQL text for assertions."""
    return str(stmt.compile(dialect=postgresql.dialect()))


class _FakeResult:
    """Minimal result object: supports .scalars().all() and .all()."""

    def __init__(self, items=()):
        self._items = list(items)

    def scalars(self):
        return self

    def all(self):
        return self._items


class _FakeDashboardSession:
    """Canned responses for every query dashboard_summary issues.

    Records every scalar/execute statement so the test can assert on the
    compiled SQL. With empty requirement/registrar lists the per-row loops
    never run, so only two scalar calls happen:
      1. count(registrar_requirements.id)            -> total_requirements
      2. count(DISTINCT ...registrar_requirement_id) -> completed count
    """

    def __init__(self, total_requirements: int = 3, completed_docs_raw: int = 2):
        self.total_requirements = total_requirements
        self.completed_docs_raw = completed_docs_raw
        self.scalar_statements = []
        self.execute_statements = []

    async def scalar(self, stmt):
        self.scalar_statements.append(stmt)
        if "registrar_documents" in _compile(stmt):
            return self.completed_docs_raw
        return self.total_requirements

    async def execute(self, stmt):
        self.execute_statements.append(stmt)
        return _FakeResult()


def _run_summary(session) -> dict:
    payload = asyncio.run(
        dashboard_summary(session=session, current_user=SimpleNamespace(id=1))
    )
    assert payload["error"] is None
    return payload["data"]


# ===========================================================================
# AC-1 — completed_requirements counts distinct requirement ids (query shape)
# ===========================================================================

def test_completed_requirements_query_counts_distinct_requirement_ids():
    # Spec: F-026-registrar-dashboard.md | AC-1 | Then counts and
    # completion_pct match the data (one requirement with two completed
    # documents counts once — hence DISTINCT over registrar_requirement_id).
    session = _FakeDashboardSession(total_requirements=3, completed_docs_raw=2)
    data = _run_summary(session)

    doc_counts = [s for s in session.scalar_statements if "registrar_documents" in _compile(s)]
    assert len(doc_counts) == 1, "exactly one completed-document count query"
    sql = _compile(doc_counts[0])

    # The fix under test: count DISTINCT requirement ids, never documents.
    # SQLAlchemy renders func.count(func.distinct(col)) as count(distinct(col)).
    assert "count(distinct(registrar_documents.registrar_requirement_id))" in sql
    assert "count(registrar_documents.id)" not in sql
    # Soft-delete and status filters must remain in place.
    assert "registrar_documents.status" in sql
    assert "registrar_documents.deleted_at IS NULL" in sql

    assert data["total_requirements"] == 3
    assert data["completed_requirements"] == 2
    assert data["completion_pct"] == 66.7


def test_completed_requirements_never_exceed_total_and_pct_stays_at_100():
    # Spec: F-026-registrar-dashboard.md | AC-1 | Then counts and
    # completion_pct match the data — completed_requirements <=
    # total_requirements and completion_pct <= 100 even if the raw
    # document count is inflated (e.g. docs left behind by a
    # soft-deleted requirement).
    session = _FakeDashboardSession(total_requirements=3, completed_docs_raw=5)
    data = _run_summary(session)

    assert data["completed_requirements"] == 3
    assert data["completed_requirements"] <= data["total_requirements"]
    assert data["completion_pct"] == 100.0
    assert data["completion_pct"] <= 100


def test_dashboard_with_no_requirements_reports_zero_pct():
    # Spec: F-026-registrar-dashboard.md | AC-1 | Then counts and
    # completion_pct match the data — an empty dataset must not divide by
    # zero and must report 0, not an error.
    session = _FakeDashboardSession(total_requirements=0, completed_docs_raw=0)
    data = _run_summary(session)

    assert data["total_requirements"] == 0
    assert data["completed_requirements"] == 0
    assert data["completion_pct"] == 0


# ===========================================================================
# AC-1 — registrar_health: a registrar is complete only if EVERY requirement
# has a completed document (distinct-requirement counting, Part F2)
# ===========================================================================

class _FakeHealthSession:
    """Feeds dashboard_summary one registrar with N requirements.

    The top-level requirement list is empty (so the attention-item loop never
    runs) and only the registrar_health loop is exercised:

      scalar 1  count(registrar_requirements.id)                      -> 3 (total)
      scalar 2  count(DISTINCT ...registrar_requirement_id)           -> 2 (completed)
      scalar 3  count(registrar_requirements.id) WHERE registrar_id   -> reg_req_count
      scalar 4  count(DISTINCT ...registrar_requirement_id) in reg    -> reg_completed
    """

    def __init__(self, reg_req_count: int, reg_completed: int):
        self.reg_req_count = reg_req_count
        self.reg_completed = reg_completed
        self.scalar_statements = []
        self.execute_statements = []

    async def scalar(self, stmt):
        sql = _compile(stmt)
        self.scalar_statements.append(sql)
        if "registrar_documents" in sql:
            # Global completed count (no registrar scoping) vs per-registrar
            # count (restricted to this registrar's requirements via subquery).
            return self.reg_completed if "registrar_requirements.registrar_id" in sql else 2
        if "registrar_requirements.registrar_id" in sql:
            return self.reg_req_count
        return 3  # global total requirements

    async def execute(self, stmt):
        sql = _compile(stmt)
        self.execute_statements.append(sql)
        if sql.lstrip().startswith("SELECT registrars.id"):
            return _FakeResult([SimpleNamespace(id=7, name="Partial Registrar")])
        return _FakeResult()  # empty requirement list / unmapped-company lists


def test_registrar_health_counts_distinct_requirements_not_documents():
    # Spec: F-026-registrar-dashboard.md | AC-1 | Then ... the dashboard
    # reflects the data — a registrar is "complete" only when EVERY one of its
    # requirements has >= 1 completed, non-deleted document (Part F2).
    # Two completed docs on req A and none on req B => "attention", never
    # "complete", so the per-registrar count must be DISTINCT requirement ids.
    session = _FakeHealthSession(reg_req_count=2, reg_completed=1)
    data = _run_summary(session)

    health_queries = [
        s for s in session.scalar_statements
        if "registrar_documents" in s and "registrar_requirements.registrar_id" in s
    ]
    assert len(health_queries) == 1, "exactly one per-registrar document count"
    sql = health_queries[0]

    # The fix under test: distinct requirement ids, never raw document ids.
    assert "count(distinct(registrar_documents.registrar_requirement_id))" in sql
    assert "count(registrar_documents.id)" not in sql
    # Soft-delete, status and registrar scoping must remain in place.
    assert "registrar_documents.status" in sql
    assert "registrar_documents.deleted_at IS NULL" in sql
    assert "registrar_requirements.registrar_id" in sql

    # 1 of 2 requirements complete -> attention, not complete.
    assert data["registrar_health"] == {"complete": 0, "attention": 1, "no_data": 0}


def test_registrar_health_complete_when_all_requirements_covered():
    # Spec: F-026-registrar-dashboard.md | AC-1 | Then ... the dashboard
    # reflects the data — every requirement covered by a completed document
    # still classifies the registrar as "complete".
    session = _FakeHealthSession(reg_req_count=2, reg_completed=2)
    data = _run_summary(session)

    assert data["registrar_health"] == {"complete": 1, "attention": 0, "no_data": 0}
