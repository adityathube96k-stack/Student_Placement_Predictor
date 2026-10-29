from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from models.notification import Notification
from routes._common import user_id
from utils.decorators import login_required

notification_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notification_bp.route("")
@login_required
def inbox():
    return render_template("notifications.html", items=Notification.all(user_id()))


@notification_bp.route("/<int:notification_id>/open")
@login_required
def open_item(notification_id):
    Notification.mark_read(user_id(), notification_id)
    target = request.args.get("to", "")
    if target.startswith("/") and not target.startswith("//"):
        return redirect(target)
    return redirect(url_for("notifications.inbox"))


@notification_bp.route("/read-all", methods=["POST"])
@login_required
def read_all():
    Notification.mark_all_read(user_id())
    if request.headers.get("X-Requested-With") == "fetch":
        return jsonify(ok=True)
    return redirect(request.referrer or url_for("notifications.inbox"))


@notification_bp.route("/<int:notification_id>/delete", methods=["POST"])
@login_required
def delete_item(notification_id):
    Notification.delete(user_id(), notification_id)
    return redirect(url_for("notifications.inbox"))


@notification_bp.route("/unread-count")
@login_required
def unread_count():
    return jsonify(count=Notification.unread_count(user_id()))
