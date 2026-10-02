# =====================================================
# PERSONALIZED SKILL RECOMMENDATIONS
# =====================================================

def generate_skill_recommendations(skill_analysis):
    """
    Generate personalized learning recommendations
    based on the student's skill gaps.
    """

    recommendations = []

    learning_resources = {

        "Aptitude": {
            "topics": [
                "Quantitative Aptitude",
                "Logical Reasoning",
                "Data Interpretation"
            ],
            "actions": [
                "Practice aptitude questions daily",
                "Take timed aptitude mock tests"
            ]
        },

        "Coding": {
            "topics": [
                "Data Structures & Algorithms",
                "Problem Solving",
                "Competitive Programming"
            ],
            "actions": [
                "Solve 2-3 coding problems daily",
                "Practice problems on coding platforms"
            ]
        },

        "Communication": {
            "topics": [
                "English Communication",
                "Public Speaking",
                "Interview Communication"
            ],
            "actions": [
                "Practice speaking for 15 minutes daily",
                "Practice HR interview questions",
                "Improve technical explanation skills"
            ]
        },

        "Technical": {
            "topics": [
                "Core Computer Science",
                "DBMS",
                "Operating Systems",
                "Computer Networks",
                "Programming Fundamentals"
            ],
            "actions": [
                "Revise core CS concepts",
                "Practice technical interview questions",
                "Build practical projects"
            ]
        }
    }

    # =================================================
    # ANALYZE EACH SKILL
    # =================================================

    for skill, data in skill_analysis.items():

        gap = data["gap"]

        if gap <= 0:
            continue

        if gap > 10:
            priority = "High"

        elif gap > 5:
            priority = "Medium"

        else:
            priority = "Low"

        resource = learning_resources.get(
            skill,
            {}
        )

        recommendations.append({

            "skill": skill,

            "current_score":
                data["current_score"],

            "target_score":
                data["target_score"],

            "gap":
                data["gap"],

            "priority":
                priority,

            "topics":
                resource.get("topics", []),

            "actions":
                resource.get("actions", [])
        })

    # =================================================
    # SORT BY PRIORITY
    # =================================================

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    recommendations.sort(
        key=lambda item:
        priority_order[item["priority"]]
    )

    # =================================================
    # RETURN RESULT
    # =================================================

    return recommendations


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    sample_skill_analysis = {

        "Aptitude": {
            "current_score": 80,
            "target_score": 75,
            "gap": 0,
            "status": "Strong"
        },

        "Coding": {
            "current_score": 85,
            "target_score": 75,
            "gap": 0,
            "status": "Strong"
        },

        "Communication": {
            "current_score": 60,
            "target_score": 70,
            "gap": 10,
            "status": "Needs Improvement"
        },

        "Technical": {
            "current_score": 65,
            "target_score": 75,
            "gap": 10,
            "status": "Needs Improvement"
        }
    }

    result = generate_skill_recommendations(
        sample_skill_analysis
    )

    print("==========================================")
    print("PERSONALIZED SKILL RECOMMENDATIONS")
    print("==========================================")

    for recommendation in result:

        print(
            f"\nSkill: {recommendation['skill']}"
        )

        print(
            f"Priority: {recommendation['priority']}"
        )

        print(
            f"Current Score: "
            f"{recommendation['current_score']}"
        )

        print(
            f"Skill Gap: "
            f"{recommendation['gap']}"
        )

        print("Topics:")

        for topic in recommendation["topics"]:

            print(
                f"  - {topic}"
            )

        print("Actions:")

        for action in recommendation["actions"]:

            print(
                f"  - {action}"
            )

    print("\n==========================================")