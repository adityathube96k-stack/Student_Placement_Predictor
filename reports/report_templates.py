"""Assemble the data dictionary consumed by the PDF generator."""
from database.db import query_one
from models.resume import Resume
from recommendation_engine.course_recommender import recommend_courses
from recommendation_engine.skill_gap import calculate_skill_gap
from recommendation_engine.skill_recommendation import generate_skill_recommendations
from utils.helpers import parse_json

NA = "Not Available"


def build_student_report_data(user_id, student):
    pred = query_one("SELECT prediction, placement_probability, not_placed_probability FROM prediction_history "
                     "WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    ready = query_one("SELECT readiness_score, readiness_level FROM readiness_history "
                      "WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    gap_row = query_one("SELECT total_gap, overall_status FROM skill_gap_history "
                        "WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    resume = Resume.latest(user_id)

    data = {"prediction": NA, "probability": NA, "readiness_score": NA, "readiness_level": NA,
            "skill_gap": NA, "skill_status": NA, "resume_score": NA, "resume_status": NA,
            "recommendations": []}
    if pred:
        data["prediction"] = pred["prediction"] or NA
        placed = str(pred["prediction"]).lower() == "placed"
        data["probability"] = pred["placement_probability"] if placed else pred["not_placed_probability"]
    if ready:
        data["readiness_score"], data["readiness_level"] = ready["readiness_score"], ready["readiness_level"]
    if gap_row:
        data["skill_gap"], data["skill_status"] = gap_row["total_gap"], gap_row["overall_status"]
    if resume:
        data["resume_score"], data["resume_status"] = resume["overall_score"], resume["rating"]

    recs = []
    if student and all(student.get(k) is not None for k in
                       ("aptitude_score", "coding_score", "communication_score", "technical_score")):
        gap = calculate_skill_gap(student["aptitude_score"], student["coding_score"],
                                  student["communication_score"], student["technical_score"])
        for item in generate_skill_recommendations(gap["skills"]):
            if item["status"] == "Needs Improvement" and item["actions"]:
                recs.append(f"{item['skill']} ({item['gap']:g} pts below target): {item['actions'][0]}")
        for course in recommend_courses(gap["skills"], student.get("skills"), limit=2):
            recs.append(f"Course: {course['title']} ({course['provider']})")
    for item in parse_json(resume["recommendations_json"], []) if resume else []:
        if item.get("priority") == "High":
            recs.append(f"Resume: {item['title']}")
    data["recommendations"] = recs[:8]
    return data
