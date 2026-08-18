"""
EPM — Reusable email-sending utility.

Provider-agnostic: talks plain SMTP-over-TLS. Swapping providers
(e.g. Mailgun → SES) means changing four env vars, not application code.

Environment variables required:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_ADDRESS
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger("email")


def send_email(
    to: str,
    subject: str,
    body: str,
    html: bool = False,
) -> dict:
    """
    Send an email via SMTP. Returns {"status": "sent"} or
    {"status": "failed", "detail": "..."}.
    """
    host = os.environ.get("SMTP_HOST", "")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    from_addr = os.environ.get("SMTP_FROM_ADDRESS", "")

    if not all([host, user, password, from_addr]):
        return {"status": "failed", "detail": "SMTP configuration incomplete — check SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_ADDRESS"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = from_addr
        msg["To"] = to
        msg["Subject"] = subject

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.sendmail(from_addr, [to], msg.as_string())

        logger.info("Email sent to %s: %s", to, subject)
        return {"status": "sent"}

    except Exception as e:
        error_msg = str(e)[:200]  # Sanitize — no raw stack traces
        logger.error("Email send failed: %s", error_msg)
        return {"status": "failed", "detail": error_msg}


def send_test_email(to: str) -> dict:
    """Send a test email to validate SMTP configuration."""
    return send_email(
        to=to,
        subject="EPM Reminder Test — SMTP Configuration Verified",
        body="This is a test email from Estate Portfolio Manager.\n\n"
             "If you received this, your SMTP configuration is working correctly.",
    )
