import asyncio
from types import SimpleNamespace

from app.routers.holdings import list_holdings, publish_holding, soft_delete_holding


def test_readonly_user_sees_only_live_holdings():
    payload = asyncio.run(list_holdings(SimpleNamespace(role="readonly")))
    statuses = {item["status"] for item in payload["data"]}
    assert statuses == {"LIVE"}


def test_admin_user_sees_live_and_draft_holdings():
    payload = asyncio.run(list_holdings(SimpleNamespace(role="admin")))
    statuses = {item["status"] for item in payload["data"]}
    assert "LIVE" in statuses
    assert "DRAFT" in statuses


def test_publish_holding_returns_live_status():
    payload = asyncio.run(publish_holding(12, SimpleNamespace(role="admin")))
    assert payload["data"]["id"] == 12
    assert payload["data"]["status"] == "LIVE"


def test_soft_delete_holding_returns_deleted_message():
    payload = asyncio.run(soft_delete_holding(12, SimpleNamespace(role="admin")))
    assert payload["data"]["message"] == "Deleted"
