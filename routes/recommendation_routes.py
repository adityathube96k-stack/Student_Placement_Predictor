from collections import Counter

from flask import Blueprint, render_template

from models.recommendation import Recommendation

from company_eligibility.eligibility_checker import check_student
from recommendation_engine.career_roadmap import build_roadmap, suggest_roles
from recommendation_engine.certification_recommender import recommend_certifications
from recommendation_engine.course_recommender import recommend_courses
from recommendation_engine.learning_path import build_learning_path
from recommendation_engine.skill_gap import calculate_skill_gap
from recommendation_engine.skill_recommendation import generate_skill_recommendations
from routes._common import get_student, need_scores
from utils.decorators import student_required
from utils.helpers import split_skills

recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/student")


def _context(student):
    return Recommendation.context(student)


@recommendation_bp.route("/recommendations")
@student_required
def recommendations():
    student = get_student()
    blocked = need_scores(student)
    if blocked:
        return blocked
    gap, missing = _context(student)
    return render_template(
        "student/recommendations.html", student=student, skill_gap=gap,
        recommendations=generate_skill_recommendations(gap["skills"]),
        courses=recommend_courses(gap["skills"], student.get("skills"), missing),
        path=build_learning_path(gap["skills"]), roles=suggest_roles(student.get("skills")),
        student_skills=split_skills(student.get("skills")), missing_skills=missing)


@recommendation_bp.route("/roadmap")
@student_required
def roadmap():
    student = get_student()
    blocked = need_scores(student)
    if blocked:
        return blocked
    gap, _ = _context(student)
    return render_template("student/roadmap.html", student=student, skill_gap=gap,
                           roadmap=build_roadmap(gap, student.get("skills")))


@recommendation_bp.route("/certifications")
@student_required
def certifications():
    student = get_student()
    blocked = need_scores(student)
    if blocked:
        return blocked
    _, missing = _context(student)
    return render_template("student/certifications.html", student=student, missing_skills=missing,
                           certifications=recommend_certifications(student.get("skills"), missing))
