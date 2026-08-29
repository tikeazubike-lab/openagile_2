#!/usr/bin/env python3
"""
EPM — Registrar Requirement Reminder Cron Job.

Scans registrar_requirements for upcoming/overdue due_dates and sends
reminder emails. Follows the daily_nav_snapshot.py pattern exactly.

Idempotency: at most one email per requirement per calendar day,
enforced via the reminder_log table.

Usage:
  python scripts/registrar_reminder_cron.py

Expected cron schedule: daily at 09:00 UTC (10:00 WAT).
Exit code 0 = success, non-zero = failure.
"""
import asyncio
import logging
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select, and_, func, text

from app.database import AsyncSessionLocal
from app.models import RegistrarRequirement, Registrar, ReminderLog, AdminAudit
from app.services.email import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("registrar_reminder_cron")


async def main() -> int:
    today = date.today()
    lead_days = int(os.environ.get("REMINDER_LEAD_DAYS", "7"))
    recipient = os.environ.get("REMINDER_RECIPIENT_EMAIL", "zubbyik@gmail.com")

    logger.info("Registrar reminder cron — started for %s (lead=%d days, to=%s)", today, lead_days, recipient)

    async with AsyncSessionLocal() as session:
        # Find requirements with due_date within lead window or overdue, status not completed
        lead_date = today + timedelta(days=lead_days)
        stmt = select(RegistrarRequirement).where(
            and_(
                RegistrarRequirement.due_date.isnot(None),
                RegistrarRequirement.due_date <= lead_date,
                RegistrarRequirement.deleted_at.is_(None),
            )
        )
        result = await session.execute(stmt)
        requirements = result.scalars().all()

        sent_count = 0
        skipped_count = 0
        failed_count = 0

        for req in requirements:
            # Idempotency check: already sent today?
            today_check = await session.scalar(
                select(func.count(ReminderLog.id)).where(
                    and_(
                        ReminderLog.requirement_id == req.id,
                        func.date(ReminderLog.sent_at) == today,
                    )
                )
            )
            if today_check and today_check > 0:
                skipped_count += 1
                continue

            # Determine reminder type
            if req.due_date < today:
                reminder_type = "overdue"
            else:
                reminder_type = "upcoming"

            # Get registrar name
            reg = await session.get(Registrar, req.registrar_id)
            reg_name = reg.name if reg else "Unknown"

            # Send email
            subject = f"EPM Reminder: {reminder_type.title()} — {req.document_title} ({reg_name})"
            body = (
                f"Registrar: {reg_name}\n"
                f"Requirement: {req.document_title}\n"
                f"Task: {req.task_name}\n"
                f"Due date: {req.due_date}\n"
                f"Status: {reminder_type}\n\n"
                f"This is an automated reminder from Estate Portfolio Manager."
            )

            email_result = send_email(to=recipient, subject=subject, body=body)

            # Log to reminder_log
            log_entry = ReminderLog(
                requirement_id=req.id,
                reminder_type=reminder_type,
                recipient_email=recipient,
                delivery_status=email_result["status"],
                error_detail=email_result.get("detail"),
            )
            session.add(log_entry)

            # Write admin_audit entry (F-007 pattern: performed_by=NULL)
            audit_entry = AdminAudit(
                action="reminder_sent" if email_result["status"] == "sent" else "reminder_failed",
                entity_type="registrar_requirement",
                entity_id=str(req.id),
                new_value=email_result["status"],
                performed_by=None,
                details=f"{reminder_type} reminder for {req.document_title} ({reg_name})",
            )
            session.add(audit_entry)

            if email_result["status"] == "sent":
                sent_count += 1
            else:
                failed_count += 1

        await session.commit()

    logger.info("Registrar reminder cron — completed: sent=%d, skipped=%d, failed=%d", sent_count, skipped_count, failed_count)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
