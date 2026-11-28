#!/usr/bin/env python3
"""
EPM — Daily NAV Snapshot (cron).

Opens its own DB session, calculates today's NAV using the same logic as
the snapshot endpoint, upserts into nav_history with notes='cron_auto',
and writes an admin_audit entry with performed_by=NULL.

Usage:
  python scripts/daily_nav_snapshot.py

Expected cron schedule: daily at 17:00 UTC (18:00 WAT) after NGX closes.
Exit code 0 = success, non-zero = failure.
"""
import asyncio
import logging
import os
import sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import NavHistory, AdminAudit
from app.services.nav import calculate_nav

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("daily_nav_snapshot")


async def main() -> int:
    today = date.today()
    logger.info("Daily NAV snapshot — started for %s", today)

    try:
        async with AsyncSessionLocal() as session:
            result = await calculate_nav(today, session)

            existing = await session.execute(
                select(NavHistory).where(NavHistory.snapshot_date == today)
            )
            row = existing.scalar_one_or_none()

            if row is None:
                row = NavHistory(
                    snapshot_date=today,
                    total_value=result.total_value,
                    total_cost=result.total_cost,
                    gain_loss=result.gain_loss,
                    notes="cron_auto",
                )
                session.add(row)
                logger.info("Created new NAV row for %s", today)
            else:
                row.total_value = result.total_value
                row.total_cost = result.total_cost
                row.gain_loss = result.gain_loss
                row.notes = "cron_auto"
                logger.info("Updated existing NAV row for %s", today)

            audit = AdminAudit(
                action="nav_snapshot_auto",
                entity_type="nav_history",
                entity_id=str(today),
                performed_by=None,
                details=f"Daily cron NAV snapshot for {today}",
                new_value=str(result.total_value),
            )
            session.add(audit)

            await session.commit()

        logger.info("NAV snapshot complete: value=%s, cost=%s, gain=%s",
                    result.total_value, result.total_cost, result.gain_loss)
        return 0

    except Exception:
        logger.exception("NAV snapshot failed for %s", today)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
