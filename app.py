from flask import (
    Flask,
    render_template,
    jsonify
)

from config import Config
from database.db import check_connection

from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.prediction_routes import prediction_bp
from routes.readiness_routes import readiness_bp
from routes.skill_gap_routes import skill_gap_bp
from routes.recommendation_routes import recommendation_bp
from routes.resume_routes import resume_bp
from routes.company_routes import company_bp
from routes.interview_routes import interview_bp
from routes.admin_routes import admin_bp
from routes.tpo_routes import tpo_bp
from routes.report_routes import report_bp


# =====================================================
# FLASK APPLICATION
# =====================================================

app = Flask(__name__)

app.config.from_object(Config)


# =====================================================
# BLUEPRINT REGISTRATION
# =====================================================

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(readiness_bp)
app.register_blueprint(skill_gap_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(company_bp)
app.register_blueprint(interview_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(tpo_bp)
app.register_blueprint(report_bp)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "success",
        "message": (
            "Student_Placement_Predictor "
            "backend is running"
        )
    })


# =====================================================
# DATABASE TEST
# =====================================================

@app.route("/db-test")
def db_test():

    connected, message = check_connection()

    return jsonify({
        "database": (
            "connected"
            if connected
            else "not_connected"
        ),
        "message": message
    }), 200 if connected else 500


# =====================================================
# APPLICATION START
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )