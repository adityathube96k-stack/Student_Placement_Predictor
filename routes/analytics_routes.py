from flask import Blueprint, render_template

from analytics.student_analytics import improvement, progress_timeline, skill_radar
from routes._common import get_student, user_id
from utils.decorators import student_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/student")


@analytics_bp.route("/analytics")
@student_required
def student_analytics():
    student = get_student()
    timeline = progress_timeline(user_id())
    return render_template("student/analytics.html", student=student, timeline=timeline,
                           radar=skill_radar(student),
                           changes={k: improvement(v) for k, v in timeline.items()})
