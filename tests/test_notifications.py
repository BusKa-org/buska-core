from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from buska_core.notifications import send_email


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config.update(
        MAIL_SERVER="smtp.example.com",
        MAIL_USERNAME="noreply@example.com",
        MAIL_PASSWORD="super-secret",
    )
    return app


def test_skips_send_when_unconfigured(caplog):
    app = Flask(__name__)
    with app.app_context(), patch("buska_core.notifications.smtplib.SMTP") as smtp:
        send_email("user@example.com", "Hi", "body")
    smtp.assert_not_called()
    assert "not configured" in caplog.text.lower()


def test_sends_via_smtp_with_tls(app):
    with app.app_context(), patch("buska_core.notifications.smtplib.SMTP") as smtp_cls:
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server

        send_email("user@example.com", "Hi", "plain body", "<p>html body</p>")

        smtp_cls.assert_called_once_with("smtp.example.com", 587)
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("noreply@example.com", "super-secret")
        assert server.sendmail.call_count == 1
        to_addr = server.sendmail.call_args[0][1]
        assert to_addr == "user@example.com"


def test_skips_tls_when_disabled(app):
    app.config["MAIL_USE_TLS"] = False
    with app.app_context(), patch("buska_core.notifications.smtplib.SMTP") as smtp_cls:
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server

        send_email("user@example.com", "Hi", "body")

        server.starttls.assert_not_called()


def test_password_never_logged(app, caplog):
    with app.app_context(), patch("buska_core.notifications.smtplib.SMTP") as smtp_cls:
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server
        send_email("user@example.com", "Hi", "body")

    assert "super-secret" not in caplog.text


def test_reraises_and_logs_on_smtp_failure(app, caplog):
    with app.app_context(), patch("buska_core.notifications.smtplib.SMTP") as smtp_cls:
        smtp_cls.return_value.__enter__.side_effect = OSError("connection refused")
        with pytest.raises(OSError, match="connection refused"):
            send_email("user@example.com", "Hi", "body")
    assert "Failed to send email" in caplog.text
