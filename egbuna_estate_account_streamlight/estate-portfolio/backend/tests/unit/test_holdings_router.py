import asyncio
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace

from app.routers.holdings import list_holdings, publish_holding, soft_delete_holding


def _mock_session(execute_result=None):
    """Create a fake session that returns execute_result from scalar_one_or_none()."""
    session = MagicMock()
    session.execute = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=execute_result)
    result.scalars = MagicMock()
    result.scalars.return_value.all = MagicMock(return_value=execute_result or [])
    session.execute.return_value = result
    session.commit = AsyncMock()
    return session


def test_readonly_user_sees_only_live_holdings():
    mock_session = _mock_session(execute_result=[])
    payload = asyncio.run(list_holdings(
        holding_type="all",
        company_id=None,
        session=mock_session,
        current_user=SimpleNamespace(role="readonly"),
    ))
    assert payload["meta"] == {}


def test_admin_user_sees_live_and_draft_holdings():
    from decimal import Decimal
    draft = MagicMock()
    draft.holding_type = "draft"
    draft.num_shares = Decimal("50")
    draft.average_cost_basis = Decimal("200")
    draft.total_cost = Decimal("10000")
    draft.current_value = None
    draft.deleted_at = None
    draft.company = MagicMock()
    draft.company.ticker = "DRAFTCO"
    draft.company.name = "Draft Co"
    draft.company.sector = "Consumer"
    draft.company.current_price = None
    draft.claim_records = []
    draft.cost_basis_override = None

    active = MagicMock()
    active.holding_type = "active"
    active.num_shares = Decimal("100")
    active.average_cost_basis = Decimal("450")
    active.total_cost = Decimal("45000")
    active.current_value = Decimal("50000")
    active.deleted_at = None
    active.company = MagicMock()
    active.company.ticker = "TESTCO"
    active.company.name = "Test Co"
    active.company.sector = "Banking"
    active.company.current_price = Decimal("500")
    active.claim_records = []
    active.cost_basis_override = None

    mock_session = _mock_session(execute_result=[draft, active])
    payload = asyncio.run(list_holdings(
        holding_type="all",
        company_id=None,
        session=mock_session,
        current_user=SimpleNamespace(role="admin"),
    ))
    types = {item["holding_type"] for item in payload["data"]}
    assert "active" in types
    assert "draft" in types


def test_publish_holding_returns_live_status():
    holding = MagicMock()
    holding.id = 12
    holding.holding_type = "draft"
    mock_session = _mock_session(execute_result=holding)
    payload = asyncio.run(publish_holding(
        holding_id=12,
        session=mock_session,
        _=SimpleNamespace(role="admin"),
    ))
    assert payload["data"]["id"] == 12
    assert payload["data"]["holding_type"] == "active"


def test_soft_delete_holding_returns_deleted_message():
    holding = MagicMock()
    holding.id = 12
    mock_session = _mock_session(execute_result=holding)
    payload = asyncio.run(soft_delete_holding(
        holding_id=12,
        session=mock_session,
        _=SimpleNamespace(role="admin"),
    ))
    assert payload["data"]["message"] == "Deleted"
