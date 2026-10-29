"""Assembles the recommendation bundle for a student from the engine modules."""
from collections import Counter

from company_eligibility.eligibility_checker import check_student
from recommendation_engine.career_roadmap import build_roadmap, suggest_roles
from recommendation_engine.certification_recommender import recommend_certifications
from recommendation_engine.course_recommender import recommend_courses
from recommendation_engine.learning_path import build_learning_path
from recommendation_engine.skill_gap import calculate_skill_gap
from recommendation_engine.skill_recommendation import generate_skill_recommendations


class Recommendation:
    @staticmethod
    def context(student):
        """Skill gap plus the skills companies want that this student lacks."""
        gap = calculate_skill_gap(student["aptitude_score"], student["coding_score"],
                                  student["communication_score"], student["technical_score"])
        missing = Counter(s for r in check_student(student) if not r["eligible"] for s in r["missing_skills"])
        return gap, [skill for skill, _ in missing.most_common(6)]

    @staticmethod
    def bundle(student):
        gap, missing = Recommendation.context(student)
        return {
            "skill_gap": gap, "missing_skills": missing,
            "recommendations": generate_skill_recommendations(gap["skills"]),
            "courses": recommend_courses(gap["skills"], student.get("skills"), missing),
            "certifications": recommend_certifications(student.get("skills"), missing),
            "path": build_learning_path(gap["skills"]),
            "roles": suggest_roles(student.get("skills")),
            "roadmap": build_roadmap(gap, student.get("skills")),
        }
