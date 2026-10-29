from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from database.db import execute, scalar
from models.notification import Notification
from models.user import User
from notifications.service import notify_many
from utils.decorators import home_for
from utils.validators import validate_email

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    stats = {
        "students": scalar("SELECT COUNT(*) FROM students"),
        "companies": scalar("SELECT COUNT(*) FROM companies WHERE is_active = 1"),
        "predictions": scalar("SELECT COUNT(*) FROM prediction_history"),
    }
    try:
        from ml.model_loader import get_metadata
        model = get_metadata()
    except Exception:  # noqa: BLE001 - landing page must always render
        model = None
    return render_template("index.html", stats=stats, model=model)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        subject = request.form.get("subject", "").strip()[:150] or "General enquiry"
        message = request.form.get("message", "").strip()
        if len(name) < 2 or not validate_email(email) or len(message) < 10:
            flash("Please enter your name, a valid email and a message of at least 10 characters.", "danger")
            return render_template("contact.html", form=request.form), 400
        execute("INSERT INTO contact_messages (name, email, subject, message) VALUES (%s,%s,%s,%s)",
                (name, email, subject, message[:3000]))
        notify_many(User.ids_by_role("admin"), "contact", "info", None,
                    name=name, subject=subject, message=message[:160])
        flash("Thanks. Your message has been sent and we will reply by email.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form={})
