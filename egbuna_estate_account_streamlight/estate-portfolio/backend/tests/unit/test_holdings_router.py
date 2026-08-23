# backend/tests/unit/test_holdings_router.py
"""
Holdings router unit tests against the current holdings implementation
(Phase 2B/3C async queries). Endpoint functions are called directly with
mocked sessions.

NOTE: rewritten from the legacy version, which asserted statuses like
"LIVE"/"DRAFT" that the current list_holdings no longer emits — the
response now carries holding_type ("active"/"claim") plus computed fields.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routers.holdings import (
    list_holdings,
    publish_holding,
    soft_delete_holding,
)


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class FakeGetResult:
    def __init__(self, holding):
        self._holding = holding

    def scalar_one_or_none(self):
        return self._holding


class FakeSession:
    def __init__(self, holdings, single=None):
        self._holdings = holdings
        self._single = single
        self.commit_called = False

    async def execute(self, *_args, **_kwargs):
        if self._single is not None:
            return FakeGetResult(self._single)
        return FakeScalarResult(self._holdings)

    async def commit(self):
        self.commit_called = True


def make_holding(**overrides):
    fields = dict(
        id=1,
        holding_type="active",
        num_shares=100,
        average_cost_basis=10.0,
        total_cost=1000.0,
        current_value=1500.0,
        cost_basis_override=None,
        deleted_at=None,
        company=SimpleNamespace(
            ticker="DANGCEM",
            name="Dangote Cement",
            sector="Industrials",
            current_price=15.0,
        ),
        claim_records=[],
    )
    fields.update(overrides)
    return SimpleNamespace(**fields)


def test_admin_list_holdings_returns_serialized_holding():
    holding = make_holding()
    payload = __run(list_holdings("all", None, FakeSession([holding]), SimpleNamespace(role="admin")))
    data = payload["data"]
    assert len(data) == 1
    row = data[0]
    assert row["holding_type"] == "active"
    assert row["ticker"] == "DANGCEM"
    assert row["shares"] == 100.0
    assert row["return_pct"] == 50.0  # (1500 - 1000) / 1000


def test_readonly_list_holdings_includes_claim_serialization():
    claim = SimpleNamespace(
        updated_at=datetime.now(timezone.utc),
        claim_status="approved",
        expected_payout=500.0,
        actual_payout=None,
    )
    holding = make_holding(holding_type="claim", claim_records=[claim])
    payload = __run(list_holdings("claim", None, FakeSession([holding]), SimpleNamespace(role="readonly")))
    row = payload["data"][0]
    assert row["holding_type"] == "claim"
    assert row["return_pct"] is None
    assert row["claim_summary"]["claim_count"] == 1
    assert row["claim_summary"]["latest_status"] == "approved"
    assert row["claim_summary"]["expected_payout"] == "500.0"


def test_list_holdings_empty_returns_empty_data():
    payload = __run(list_holdings("all", None, FakeSession([]), SimpleNamespace(role="admin")))
    assert payload["data"] == []


def test_publish_holding_flips_holding_type_to_active():
    holding = make_holding(holding_type="draft")
    session = FakeSession([], single=holding)
    payload = __run(publish_holding(1, session, SimpleNamespace(role="admin")))
    assert payload["data"]["holding_type"] == "active"
    assert holding.holding_type == "active"
    assert session.commit_called is True


def test_soft_delete_holding_sets_deleted_at():
    holding = make_holding()
    session = FakeSession([], single=holding)
    payload = __run(soft_delete_holding(1, session, SimpleNamespace(role="admin")))
    assert payload["data"]["message"] == "Deleted"
    assert holding.deleted_at is not None
    assert session.commit_called is True


def __run(coro):
    import asyncio
    return asyncio.run(coro)