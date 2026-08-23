"""
F-026b — Tests for email utility and reminder cron logic.

RED-GREEN: these tests should fail against pre-F-026b code (no email.py,
no reminder_log table) and pass against the current implementation.
"""
import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock


# ─── Email Utility Tests ──────────────────────────────────────────────────────

class TestSendEmail:
    """Tests for app.services.email.send_email"""

    def test_send_email_returns_sent_on_success(self):
        """Valid SMTP config → returns {'status': 'sent'}."""
        from app.services.email import send_email

        smtp_env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
            "SMTP_FROM_ADDRESS": "alerts@example.com",
        }
        with patch.dict(os.environ, smtp_env, clear=False), \
             patch("app.services.email.smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = send_email(
                to="test@example.com",
                subject="Test",
                body="Hello",
            )
            assert result["status"] == "sent"
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()

    def test_send_email_returns_failed_on_error(self):
        """SMTP error → returns {'status': 'failed', 'detail': ...} with sanitized error."""
        from app.services.email import send_email

        smtp_env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
            "SMTP_FROM_ADDRESS": "alerts@example.com",
        }
        with patch.dict(os.environ, smtp_env, clear=False), \
             patch("app.services.email.smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
            mock_server.login.side_effect = Exception("Connection refused")

            result = send_email(
                to="test@example.com",
                subject="Test",
                body="Hello",
            )
            assert result["status"] == "failed"
            assert "detail" in result
            assert "Connection refused" in result["detail"]
            # No raw stack trace
            assert "Traceback" not in result["detail"]

    def test_send_email_returns_failed_when_config_incomplete(self):
        """Missing SMTP config → returns {'status': 'failed', 'detail': ...}."""
        from app.services.email import send_email

        with patch.dict(os.environ, {"SMTP_HOST": "", "SMTP_USER": "", "SMTP_PASSWORD": "", "SMTP_FROM_ADDRESS": ""}):
            result = send_email(
                to="test@example.com",
                subject="Test",
                body="Hello",
            )
            assert result["status"] == "failed"
            assert "SMTP configuration incomplete" in result["detail"]


class TestSendTestEmail:
    """Tests for app.services.email.send_test_email"""

    def test_send_test_email_calls_send_email(self):
        """send_test_email calls send_email with correct parameters."""
        from app.services.email import send_test_email

        with patch("app.services.email.send_email") as mock_send:
            mock_send.return_value = {"status": "sent"}
            result = send_test_email(to="test@example.com")
            assert result["status"] == "sent"
            mock_send.assert_called_once_with(
                to="test@example.com",
                subject="EPM Reminder Test — SMTP Configuration Verified",
                body="This is a test email from Estate Portfolio Manager.\n\n"
                     "If you received this, your SMTP configuration is working correctly.",
            )


# ─── Reminder Log Model Tests ────────────────────────────────────────────────

class TestReminderLog:
    """Tests for ReminderLog model constraints."""

    def test_reminder_log_check_constraints(self):
        """Verify check constraints are defined on the model."""
        from app.models import ReminderLog
        table_args = ReminderLog.__table_args__
        constraint_names = [c.name for c in table_args if hasattr(c, 'name')]
        assert "chk_reminder_type" in constraint_names
        assert "chk_delivery_status" in constraint_names
