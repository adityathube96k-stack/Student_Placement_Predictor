def generate_resume_recommendations(
    resume_score_result,
    extracted_skills=None
):
    """
    Generate personalized resume improvement
    recommendations.

    Args:
        resume_score_result (dict):
            Result returned by calculate_resume_score().

        extracted_skills (dict):
            Skills extracted from the resume.

    Returns:
        list: Resume improvement recommendations.
    """

    recommendations = []

    if not resume_score_result:
        return recommendations

    sections = resume_score_result.get(
        "sections",
        {}
    )

    overall_score = resume_score_result.get(
        "overall_score",
        0
    )

    skill_score = resume_score_result.get(
        "skill_score",
        0
    )

    length_score = resume_score_result.get(
        "length_score",
        0
    )

    # -------------------------------------------------
    # 1. Missing Resume Sections
    # -------------------------------------------------

    section_tips = {
        "Contact Information":
            "Add a professional email address and phone number.",

        "Education":
            "Add your degree, college/university, graduation year and relevant academic details.",

        "Skills":
            "Add a dedicated technical skills section with programming languages, tools and technologies.",

        "Projects":
            "Add 2-3 relevant projects with technologies used and your contribution.",

        "Experience":
            "Add internship, work experience or relevant practical experience.",

        "Certifications":
            "Add relevant technical certifications and completed courses.",

        "Achievements":
            "Add hackathons, coding achievements, awards or other measurable accomplishments."
    }

    for section, exists in sections.items():

        if not exists:
            recommendations.append({
                "category": "Resume Section",
                "priority": "High",
                "title": f"Add {section}",
                "description": section_tips.get(
                    section,
                    f"Add a clear {section} section to your resume."
                )
            })

    # -------------------------------------------------
    # 2. Skill Recommendations
    # -------------------------------------------------

    if skill_score < 50:

        recommendations.append({
            "category": "Technical Skills",
            "priority": "High",
            "title": "Improve your technical skills section",
            "description":
                "Add more relevant technical skills that match "
                "your target job roles."
        })

    elif skill_score < 70:

        recommendations.append({
            "category": "Technical Skills",
            "priority": "Medium",
            "title": "Expand your technical skills",
            "description":
                "Consider adding more relevant programming, "
                "database, development or AI/ML technologies."
        })

    # -------------------------------------------------
    # 3. Resume Length
    # -------------------------------------------------

    if length_score < 50:

        recommendations.append({
            "category": "Resume Content",
            "priority": "High",
            "title": "Add more meaningful content",
            "description":
                "Your resume appears to contain limited content. "
                "Add relevant projects, skills, internships, "
                "certifications and achievements."
        })

    elif length_score < 70:

        recommendations.append({
            "category": "Resume Content",
            "priority": "Medium",
            "title": "Strengthen your resume content",
            "description":
                "Add more measurable project achievements, "
                "technical experience and relevant accomplishments."
        })

    # -------------------------------------------------
    # 4. Projects
    # -------------------------------------------------

    if not sections.get("Projects", False):

        recommendations.append({
            "category": "Projects",
            "priority": "High",
            "title": "Add technical projects",
            "description":
                "Include projects related to your target role. "
                "Mention the problem, technologies used and "
                "your contribution."
        })

    # -------------------------------------------------
    # 5. Certifications
    # -------------------------------------------------

    if not sections.get("Certifications", False):

        recommendations.append({
            "category": "Certifications",
            "priority": "Medium",
            "title": "Add relevant certifications",
            "description":
                "Include certifications that demonstrate "
                "your knowledge in technologies relevant "
                "to your target career."
        })

    # -------------------------------------------------
    # 6. Experience
    # -------------------------------------------------

    if not sections.get("Experience", False):

        recommendations.append({
            "category": "Experience",
            "priority": "Medium",
            "title": "Add practical experience",
            "description":
                "Include internships, freelance work, "
                "industrial training or practical experience "
                "where applicable."
        })

    # -------------------------------------------------
    # 7. Overall Score
    # -------------------------------------------------

    if overall_score >= 80:

        recommendations.append({
            "category": "Overall",
            "priority": "Low",
            "title": "Maintain your resume quality",
            "description":
                "Your resume currently has a strong structure. "
                "Keep updating it with new projects, skills, "
                "certifications and achievements."
        })

    elif overall_score >= 65:

        recommendations.append({
            "category": "Overall",
            "priority": "Medium",
            "title": "Improve your resume further",
            "description":
                "Your resume has a good foundation. Focus on "
                "missing sections and strengthen measurable "
                "achievements."
        })

    else:

        recommendations.append({
            "category": "Overall",
            "priority": "High",
            "title": "Improve your resume structure",
            "description":
                "Focus on completing important sections, "
                "adding relevant technical skills and "
                "including practical projects."
        })

    # -------------------------------------------------
    # 8. Skill-specific suggestions
    # -------------------------------------------------

    if extracted_skills:

        total_skills = set()

        for skills in extracted_skills.values():
            total_skills.update(skills)

        if len(total_skills) < 5:

            recommendations.append({
                "category": "Skills",
                "priority": "High",
                "title": "Add more relevant skills",
                "description":
                    "Try to include at least a few relevant "
                    "technical skills that you actually know "
                    "and can demonstrate."
            })

    # -------------------------------------------------
    # Sort recommendations by priority
    # -------------------------------------------------

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    recommendations.sort(
        key=lambda item:
            priority_order.get(
                item["priority"],
                4
            )
    )

    return recommendations


if __name__ == "__main__":

    sample_result = {
        "overall_score": 62.5,
        "rating": "Average",
        "section_score": 71.43,
        "skill_score": 40,
        "length_score": 50,
        "sections": {
            "Contact Information": True,
            "Education": True,
            "Skills": True,
            "Projects": False,
            "Experience": False,
            "Certifications": False,
            "Achievements": False
        }
    }

    sample_skills = {
        "Programming Languages": [
            "Python"
        ],
        "Database": [
            "MySQL"
        ]
    }

    recommendations = generate_resume_recommendations(
        sample_result,
        sample_skills
    )

    print("==========================================")
    print("RESUME IMPROVEMENT RECOMMENDATIONS")
    print("==========================================")

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):
        print(
            f"\n{index}. "
            f"{recommendation['title']}"
        )

        print(
            f"Category : "
            f"{recommendation['category']}"
        )

        print(
            f"Priority : "
            f"{recommendation['priority']}"
        )

        print(
            f"Suggestion: "
            f"{recommendation['description']}"
        )

    print("\n==========================================")