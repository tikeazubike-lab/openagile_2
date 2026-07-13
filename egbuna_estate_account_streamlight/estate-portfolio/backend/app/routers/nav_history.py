"""
EPM — NAV History router (F-007).

Endpoints:
  POST /api/v1/nav-history/snapshot   — single-date NAV upsert (admin-only)
  POST /api/v1/nav-history/recalculate — range recalculation (admin-only)
  GET  /api/v1/nav-history             — list NAV history with filters
  GET  /api/v1/nav                     — latest NAV convenience
"""
import logging
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session, get_current_user, require_admin
from app.models import NavHistory, AdminAudit, User
from app.services.nav import calculate_nav

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nav-history", tags=["nav-history"])


def _envelope(data, meta=None):
    return {"data": data, "meta": meta if meta is not None else {}, "error": None}


# ─── Pydantic Schemas ──────────────────────────────────────────────────────────

class SnapshotPayload(BaseModel):
    snapshot_date: date | None = None


class RecalculatePayload(BaseModel):
    from_date: date
    to_date: date


# ─── Helpers ───────────────────────────────────────────────────────────────────

async def _record_audit(
    session: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: str | None,
    performed_by: int,
    details: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
) -> AdminAudit:
    audit = AdminAudit(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        performed_by=performed_by,
        details=details,
        old_value=old_value,
        new_value=new_value,
    )
    session.add(audit)
    await session.flush()
    return audit


def _nav_to_dict(row: NavHistory) -> dict:
    return {
        "snapshot_date": str(row.snapshot_date),
        "total_value": str(row.total_value),
        "total_cost": str(row.total_cost),
        "gain_loss": str(row.gain_loss),
        "notes": row.notes,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def _compute_summary(rows: list[NavHistory]) -> dict | None:
    """Compute 7D, 30D, YTD changes from a list of nav rows (sorted asc)."""
    if not rows:
        return None

    current = rows[-1]
    current_val = Decimal(str(current.total_value))

    today = date.today()
    ref_7d = today - timedelta(days=7)
    ref_30d = today - timedelta(days=30)
    ref_ytd = date(today.year, 1, 1)

    def pct_change(reference_date: date) -> str:
        ref_row = None
        for r in reversed(rows):
            if r.snapshot_date <= reference_date:
                ref_row = r
                break
        if ref_row is None or Decimal(str(ref_row.total_value)) == Decimal("0"):
            return "0.00"
        ref_val = Decimal(str(ref_row.total_value))
        pct = (current_val - ref_val) / ref_val * Decimal("100")
        return str(round(pct, 2))

    return {
        "current_nav": str(current_val),
        "change_7d": pct_change(ref_7d),
        "change_30d": pct_change(ref_30d),
        "change_ytd": pct_change(ref_ytd),
        "first_nav_date": str(rows[0].snapshot_date),
    }


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/snapshot")
async def post_nav_snapshot(
    payload: SnapshotPayload,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
):
    target_date = payload.snapshot_date or date.today()

    result = await calculate_nav(target_date, session)

    existing = await session.execute(
        select(NavHistory).where(NavHistory.snapshot_date == target_date)
    )
    row = existing.scalar_one_or_none()
    is_new = row is None

    if is_new:
        row = NavHistory(
            snapshot_date=target_date,
            total_value=result.total_value,
            total_cost=result.total_cost,
            gain_loss=result.gain_loss,
        )
        session.add(row)
    else:
        row.total_value = result.total_value
        row.total_cost = result.total_cost
        row.gain_loss = result.gain_loss

    await session.flush()

    await _record_audit(
        session,
        action="nav_snapshot",
        entity_type="nav_history",
        entity_id=str(target_date),
        performed_by=admin.id,
        details=f"NAV snapshot {'created' if is_new else 'updated'} for {target_date}",
        new_value=str(result.total_value),
    )

    await session.commit()
    await session.refresh(row)

    return _envelope(_nav_to_dict(row))


@router.post("/recalculate")
async def post_nav_recalculate(
    payload: RecalculatePayload,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(require_admin),
):
    if payload.from_date > payload.to_date:
        raise HTTPException(status_code=400, detail="from_date must be before to_date")

    processed = 0
    current = payload.from_date
    while current <= payload.to_date:
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue

        try:
            result = await calculate_nav(current, session)
        except Exception:
            logger.exception("NAV calculation failed for %s — skipping", current)
            current += timedelta(days=1)
            continue

        existing = await session.execute(
            select(NavHistory).where(NavHistory.snapshot_date == current)
        )
        row = existing.scalar_one_or_none()

        if row is None:
            row = NavHistory(
                snapshot_date=current,
                total_value=result.total_value,
                total_cost=result.total_cost,
                gain_loss=result.gain_loss,
                notes="backfill",
            )
            session.add(row)
        else:
            row.total_value = result.total_value
            row.total_cost = result.total_cost
            row.gain_loss = result.gain_loss
            row.notes = "backfill"

        processed += 1
        current += timedelta(days=1)

    await session.flush()

    await _record_audit(
        session,
        action="nav_recalculate",
        entity_type="nav_history",
        entity_id=None,
        performed_by=admin.id,
        details=f"NAV recalculation range {payload.from_date} to {payload.to_date}: {processed} days processed",
    )

    await session.commit()

    return _envelope({
        "from_date": str(payload.from_date),
        "to_date": str(payload.to_date),
        "days_processed": processed,
    })


@router.get("")
async def get_nav_history(
    start_date: date | None = Query(None, alias="start_date"),
    end_date: date | None = Query(None, alias="end_date"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(NavHistory).order_by(NavHistory.snapshot_date.asc())

    if start_date:
        stmt = stmt.where(NavHistory.snapshot_date >= start_date)
    if end_date:
        stmt = stmt.where(NavHistory.snapshot_date <= end_date)

    result = await session.execute(stmt)
    rows = list(result.scalars().all())

    summary = _compute_summary(rows)
    data = [_nav_to_dict(r) for r in rows]

    return _envelope(
        data={"data_points": data, "summary": summary},
        meta={"total": len(data)},
    )


# ─── Latest NAV convenience — mounted at /api/v1/nav ──────────────────────────

_latest_router = APIRouter(tags=["nav"])


@_latest_router.get("/nav")
async def get_latest_nav(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(NavHistory).order_by(NavHistory.snapshot_date.desc()).limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None:
        return _envelope(None)
    return _envelope(_nav_to_dict(row))
