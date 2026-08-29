#!/usr/bin/env python3
"""
EPM — One-shot NAV History Backfill (F-007, spec §8).

Iterates from the earliest usable price date to yesterday, calculates NAV
for each weekday, and upserts into nav_history with notes='backfill'.

Usage:
  python scripts/backfill_nav.py

Logs to: scripts/backfill_nav_{timestamp}.log
"""
import asyncio
import logging
import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import NavHistory
from app.services.nav import calculate_nav

# ── Logging ──────────────────────────────────────────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(__file__))
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, f"backfill_nav_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _get_earliest_date(session: AsyncSession) -> date:
    """Determine the first date worth backfilling from."""
    r = await session.execute(sa_text("SELECT MIN(price_date) FROM price_history"))
    earliest_price = r.scalar()
    if earliest_price is None:
        logger.error("No price data found — cannot backfill")
        sys.exit(1)
    logger.info("Earliest price date: %s", earliest_price)

    r = await session.execute(sa_text("SELECT MIN(transaction_date) FROM transactions"))
    earliest_tx = r.scalar()
    logger.info("Earliest transaction date: %s", earliest_tx)

    r = await session.execute(sa_text("SELECT MIN(purchase_date) FROM holdings"))
    earliest_purchase = r.scalar()
    logger.info("Earliest holding purchase_date: %s", earliest_purchase)

    start = min(d for d in [earliest_price, earliest_tx, earliest_purchase] if d is not None)
    logger.info("Chosen start date: %s", start)
    return start


async def _has_any_price_on_date(session: AsyncSession, target: date) -> bool:
    """Check whether at least one price entry exists on or before target."""
    r = await session.execute(
        sa_text("SELECT 1 FROM price_history WHERE price_date <= :d LIMIT 1"),
        {"d": target},
    )
    return r.scalar() is not None


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    logger.info("=" * 60)
    logger.info("NAV History Backfill — started %s", datetime.now(timezone.utc).isoformat())
    logger.info("=" * 60)

    async with AsyncSessionLocal() as session:
        start_date = await _get_earliest_date(session)
        yesterday = date.today() - timedelta(days=1)

        if start_date > yesterday:
            logger.info("Start date %s is after yesterday %s — nothing to do.", start_date, yesterday)
            return

        current = start_date
        total = 0
        skipped_weekend = 0
        skipped_no_price = 0

        while current <= yesterday:
            if current.weekday() >= 5:
                skipped_weekend += 1
                current += timedelta(days=1)
                continue

            has_price = await _has_any_price_on_date(session, current)
            if not has_price:
                skipped_no_price += 1
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

            total += 1

            if total % 50 == 0:
                logger.info("Progress: %d rows processed (at %s)", total, current)
                await session.commit()

            current += timedelta(days=1)

        await session.commit()

    logger.info("=" * 60)
    logger.info("Backfill complete.")
    logger.info("  Date range:  %s  to  %s", start_date, yesterday)
    logger.info("  Rows created/updated: %d", total)
    logger.info("  Weekends skipped:    %d", skipped_weekend)
    logger.info("  No-price days skipped: %d", skipped_no_price)
    logger.info("  Log file: %s", log_path)
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
