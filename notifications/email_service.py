"""Email delivery over SMTP. When mail is disabled, messages are written to
logs/outbox.log so flows (such as password reset) stay testable offline."""
import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from config import Config

log = logging.getLogger("spp")


def send_email(to_address, subject, body):
    """Returns True if delivered over SMTP, False if only logged or failed."""
    if not Config.MAIL_ENABLED or not Config.MAIL_USERNAME:
        _outbox(to_address, subject, body)
        return False
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = Config.MAIL_FROM, to_address, subject
    message.set_content(body)
    try:
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT, timeout=15) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(message)
        return True
    except Exception as error:  # noqa: BLE001
        log.error("Email to %s failed: %s", to_address, error)
        _outbox(to_address, subject, body)
        return False


def _outbox(to_address, subject, body):
    try:
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        with open(os.path.join(Config.LOG_DIR, "outbox.log"), "a", encoding="utf-8") as handle:
            handle.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S} to={to_address}\n"
                         f"Subject: {subject}\n{body}\n\n")
    except OSError:
        pass
