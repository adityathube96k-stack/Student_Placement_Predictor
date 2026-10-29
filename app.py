"""Application factory."""
import os

from flask import Flask, jsonify, render_template, request, session

from config import Config
from database.db import check_connection
from utils import csrf
from utils.helpers import format_date, initials, time_ago
from utils.logger import setup_logging


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    logger = setup_logging(app)

    for directory in (app.config["RESUME_UPLOAD_DIR"], app.config["DATASET_UPLOAD_DIR"],
                      app.config["MODEL_DIR"], app.config["LOG_DIR"]):
        os.makedirs(directory, exist_ok=True)

    if app.config["AUTO_INIT_DB"]:
        from database.init_db import init_database
        info = init_database(seed=app.config["SEED_DEMO_DATA"])
        if info["seeded"]:
            logger.info("Demo data created. Use the demo account buttons on the login page to sign in.")

    register_blueprints(app)
    register_hooks(app)
    register_errors(app)
    return app


def register_blueprints(app):
    from routes.admin_routes import admin_bp
    from routes.analytics_routes import analytics_bp
    from routes.auth_routes import auth_bp
    from routes.company_routes import company_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.interview_routes import interview_bp
    from routes.main_routes import main_bp
    from routes.notification_routes import notification_bp
    from routes.prediction_routes import prediction_bp
    from routes.readiness_routes import readiness_bp
    from routes.recommendation_routes import recommendation_bp
    from routes.report_routes import report_bp
    from routes.resume_routes import resume_bp
    from routes.skill_gap_routes import skill_gap_bp
    from routes.tpo_routes import tpo_bp
    for blueprint in (main_bp, auth_bp, dashboard_bp, prediction_bp, readiness_bp, skill_gap_bp,
                      recommendation_bp, resume_bp, company_bp, interview_bp, analytics_bp,
                      notification_bp, report_bp, admin_bp, tpo_bp):
        app.register_blueprint(blueprint)


def _dial_ticks():
    """Tick marks for the 270-degree readiness dial (viewBox 200x200)."""
    import math
    ticks = []
    for i in range(21):
        angle = math.radians(135 + 13.5 * i)
        major = i % 5 == 0
        r1, r2 = (86, 95) if major else (89, 94)
        ticks.append({"x1": round(100 + r1 * math.cos(angle), 2), "y1": round(100 + r1 * math.sin(angle), 2),
                      "x2": round(100 + r2 * math.cos(angle), 2), "y2": round(100 + r2 * math.sin(angle), 2),
                      "major": major})
    return ticks


def register_hooks(app):
    app.jinja_env.filters.update(time_ago=time_ago, fmt_date=format_date, initials=initials)
    app.jinja_env.filters["num"] = lambda v, d=1: (f"{float(v):.{d}f}".rstrip("0").rstrip(".")
                                                   if v not in (None, "") else "-")
    app.jinja_env.globals["csrf_token"] = csrf.generate_token
    from utils import chart_specs
    chart_specs.register(app.jinja_env)
    app.jinja_env.globals["DIAL_TICKS"] = _dial_ticks()
    app.jinja_env.globals["SHOW_DEMO_LOGINS"] = app.config.get("SEED_DEMO_DATA", False) and not app.config.get("IS_PRODUCTION", False)

    @app.before_request
    def _protect():
        session.permanent = True
        csrf.protect()

    @app.context_processor
    def _inject():
        user = None
        unread, recent = 0, []
        if "user_id" in session:
            user = {"id": session["user_id"], "name": session.get("full_name", ""),
                    "email": session.get("email", ""), "role": session.get("role", "")}
            try:
                from models.notification import Notification
                unread = Notification.unread_count(user["id"])
                recent = Notification.recent(user["id"], 6)
            except Exception:  # noqa: BLE001 - chrome must never break a page
                pass
        from datetime import datetime
        return {"now_year": datetime.now().year, "current_user": user, "unread_count": unread, "recent_notifications": recent,
                "app_name": app.config["APP_NAME"]}

    @app.after_request
    def _headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        if "user_id" in session and not request.path.startswith("/static"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.route("/health")
    def health():
        ok, message = check_connection()
        from ml.model_loader import get_metadata
        try:
            model = get_metadata()["version"]
        except Exception as error:  # noqa: BLE001
            model = f"error: {error}"
        return jsonify(status="ok" if ok else "degraded", database=message, model=model), \
            (200 if ok else 503)


def register_errors(app):
    def page(code, title, message):
        def handler(error):
            if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
                return jsonify(error=title), code
            description = getattr(error, "description", None)
            if code == 400 and description:
                message_text = description
            else:
                message_text = message
            return render_template("errors/error.html", code=code, title=title,
                                   message=message_text), code
        return handler

    app.register_error_handler(400, page(400, "Request could not be verified",
                                         "Reload the page and try again."))
    app.register_error_handler(403, page(403, "Access denied", "You do not have permission to view this page."))
    app.register_error_handler(404, page(404, "Page not found", "The page you are looking for does not exist or was moved."))
    app.register_error_handler(413, page(413, "File too large", "Uploads are limited to 16 MB."))
    app.register_error_handler(500, page(500, "Something went wrong",
                                         "An unexpected error occurred. It has been logged."))
