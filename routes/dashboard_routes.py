from flask import Blueprint, flash, redirect, render_template, request, url_for

from analytics.dashboard_stats import student_overview
from analytics.student_analytics import progress_timeline, skill_radar
from company_eligibility.eligibility_checker import check_student, get_eligible_companies
from models.company import Drive
from models.student import SCORE_FIELDS, Student
from models.user import User
from routes._common import get_student, parse_profile, user_id
from utils.constants import BRANCHES, SKILL_SUGGESTIONS, YEARS
from utils.decorators import student_required
from utils.helpers import split_skills
from utils.validators import validate_email, validate_name, validate_phone

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/student")


def _next_steps(student, overview, eligible, open_drives):
    steps = []
    if overview["completeness"] < 100:
        steps.append({"title": "Complete your profile", "text": f"{overview['completeness']}% done. Scores and skills power every analysis.",
                      "endpoint": "dashboard.profile", "icon": "user"})
    if Student.has_scores(student) and not overview["prediction"]:
        steps.append({"title": "Run your first prediction", "text": "See your placement probability and what drives it.",
                      "endpoint": "prediction.prediction", "icon": "target"})
    if not overview["resume"]:
        steps.append({"title": "Upload your resume", "text": "Get an ATS-style score and fix gaps before applying.",
                      "endpoint": "resume.resume_upload", "icon": "file"})
    if not overview["interview"]:
        steps.append({"title": "Take a mock interview", "text": "Practise with timed questions and instant feedback.",
                      "endpoint": "interview.mock_interview", "icon": "mic"})
    if eligible and open_drives:
        steps.append({"title": f"Apply to {len(open_drives)} open drive(s)", "text": "You meet the criteria for companies hiring now.",
                      "endpoint": "company.drives", "icon": "briefcase"})
    if Student.has_scores(student):
        steps.append({"title": "Review your skill gap", "text": "Find the weakest area and a plan to close it.",
                      "endpoint": "skill_gap.skill_gap", "icon": "layers"})
    return steps[:4]


@dashboard_bp.route("/dashboard")
@student_required
def dashboard():
    student = get_student()
    overview = student_overview(user_id(), student)
    eligible, open_drives = [], Drive.open_drives()[:3]
    if Student.has_scores(student):
        eligible = get_eligible_companies(check_student(student))
    return render_template(
        "student/dashboard.html", student=student, overview=overview,
        timeline=progress_timeline(user_id()), radar=skill_radar(student),
        eligible_count=len(eligible), eligible_preview=eligible[:4], open_drives=open_drives,
        next_steps=_next_steps(student, overview, eligible, open_drives))


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@student_required
def profile():
    student = get_student()
    if request.method == "POST":
        form = request.form
        try:
            user_fields, data = parse_profile(form, user_id())
        except ValueError as error:
            flash(str(error), "danger")
            merged = dict(student or {}, **form.to_dict())
            return render_template("student/profile.html", student=merged, branches=BRANCHES, years=YEARS,
                                   suggestions=SKILL_SUGGESTIONS, completeness=Student.completeness(student)), 400
        name, email = user_fields["full_name"], user_fields["email"]
        User.update_name_email(user_id(), name, email)
        Student.update_profile(user_id(), data)
        from flask import session
        session["full_name"], session["email"] = name, email
        flash("Profile saved.", "success")
        return redirect(url_for("dashboard.profile"))
    return render_template("student/profile.html", student=student, branches=BRANCHES, years=YEARS,
                           suggestions=SKILL_SUGGESTIONS, completeness=Student.completeness(student))
