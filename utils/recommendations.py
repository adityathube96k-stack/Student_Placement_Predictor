def generate_recommendations(skill_gaps):
    recommendations = []

    recommendation_map = {
        "Technical Skills": (
            "Improve technical skills through hands-on projects, "
            "technical courses, and core subject practice."
        ),
        "Coding": (
            "Practice Data Structures and Algorithms regularly "
            "and solve coding problems on programming platforms."
        ),
        "Aptitude": (
            "Practice quantitative aptitude, logical reasoning, "
            "and verbal ability questions."
        ),
        "Communication": (
            "Improve communication through presentations, "
            "group discussions, mock interviews, and speaking practice."
        )
    }

    for gap in skill_gaps:

        skill = gap["skill"]

        if skill in recommendation_map:

            recommendations.append({
                "category": skill,
                "recommendation": recommendation_map[skill],
                "priority": gap["priority"]
            })

    return recommendations