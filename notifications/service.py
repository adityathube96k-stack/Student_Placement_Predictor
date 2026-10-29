"""High-level helpers: create in-app notifications from templates."""
import logging

from models.notification import Notification
from notifications.templates import render

log = logging.getLogger("spp")


def notify(user_id, key, category="info", link=None, **values):
    try:
        title, message = render(key, **values)
        Notification.create(user_id, title, message, category, link)
    except Exception as error:  # noqa: BLE001 - notifications must never break a request
        log.warning("Notification failed: %s", error)


def notify_many(user_ids, key, category="info", link=None, **values):
    for user_id in user_ids:
        notify(user_id, key, category, link, **values)
