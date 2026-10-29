"""SMS adapter. Posts JSON to SMS_WEBHOOK_URL (any provider gateway); otherwise logs."""
import json
import logging
import urllib.request

from config import Config

log = logging.getLogger("spp")


def send_sms(phone, text):
    if not Config.SMS_ENABLED or not Config.SMS_WEBHOOK_URL or not phone:
        log.info("SMS (not sent) to %s: %s", phone, text)
        return False
    request = urllib.request.Request(
        Config.SMS_WEBHOOK_URL, data=json.dumps({"to": phone, "message": text}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return 200 <= response.status < 300
    except Exception as error:  # noqa: BLE001
        log.error("SMS to %s failed: %s", phone, error)
        return False
