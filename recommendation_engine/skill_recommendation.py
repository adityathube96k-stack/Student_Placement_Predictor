# =====================================================
# PERSONALIZED SKILL RECOMMENDATIONS
# =====================================================


def generate_skill_recommendations(skill_analysis):
    """
    Generate personalized learning recommendations
    based on the student's current skill level.

    Recommendations are generated even when the
    student has no skill gap.
    """

    recommendations = []

    learning_resources = {

        "Aptitude": {

            "topics": [
                "Quantitative Aptitude",
                "Logical Reasoning",
                "Data Interpretation",
                "Probability and Statistics"
            ],

            "actions": [
                "Practice aptitude questions daily",
                "Take timed aptitude mock tests",
                "Practice company placement aptitude papers",
                "Improve speed and accuracy"
            ],

            "advanced_actions": [
                "Solve advanced aptitude problems",
                "Practice placement-level mock tests",
                "Focus on time management"
            ]
        },

        "Coding": {

            "topics": [
                "Data Structures & Algorithms",
                "Problem Solving",
                "Competitive Programming",
                "Advanced Algorithms"
            ],

            "actions": [
                "Solve 2-3 coding problems daily",
                "Practice problems on coding platforms",
                "Revise important data structures",
                "Analyze time and space complexity"
            ],

            "advanced_actions": [
                "Solve medium and hard DSA problems",
                "Participate in coding contests",
                "Build real-world software projects",
                "Practice company-specific coding questions"
            ]
        },

        "Communication": {

            "topics": [
                "English Communication",
                "Public Speaking",
                "Interview Communication",
                "Technical Communication"
            ],

            "actions": [
                "Practice speaking for 15 minutes daily",
                "Practice HR interview questions",
                "Improve technical explanation skills",
                "Practice group discussions"
            ],

            "advanced_actions": [
                "Practice mock interviews",
                "Give technical presentations",
                "Practice group discussions",
                "Improve professional communication"
            ]
        },

        "Technical": {

            "topics": [
                "Core Computer Science",
                "DBMS",
                "Operating Systems",
                "Computer Networks",
                "Programming Fundamentals",
                "System Design"
            ],

            "actions": [
                "Revise core CS concepts",
                "Practice technical interview questions",
                "Build practical projects",
                "Revise DBMS and SQL"
            ],

            "advanced_actions": [
                "Study System Design fundamentals",
                "Build production-style projects",
                "Practice advanced technical interviews",
                "Learn cloud and deployment fundamentals"
            ]
        }
    }

    # =================================================
    # ANALYZE EACH SKILL
    # =================================================

    for skill, data in skill_analysis.items():

        current_score = float(
            data.get("current_score", 0)
        )

        target_score = float(
            data.get("target_score", 0)
        )

        gap = float(
            data.get("gap", 0)
        )

        resource = learning_resources.get(
            skill,
            {}
        )

        # =================================================
        # DETERMINE STATUS
        # =================================================

        if current_score < target_score:

            if gap > 10:
                priority = "High"

            elif gap > 5:
                priority = "Medium"

            else:
                priority = "Low"

            status = "Needs Improvement"

            actions = resource.get(
                "actions",
                []
            )

        else:

            # Student has achieved target.
            # Continue with advanced recommendations.

            priority = "Maintain"

            status = "Target Achieved"

            actions = resource.get(
                "advanced_actions",
                resource.get("actions", [])
            )

        # =================================================
        # ADD RECOMMENDATION
        # =================================================

        recommendations.append({

            "skill": skill,

            "current_score": round(
                current_score,
                2
            ),

            "target_score": round(
                target_score,
                2
            ),

            "gap": round(
                max(gap, 0),
                2
            ),

            "priority": priority,

            "status": status,

            "topics": resource.get(
                "topics",
                []
            ),

            "actions": actions
        })

    # =================================================
    # PRIORITY ORDER
    # =================================================

    priority_order = {

        "High": 1,

        "Medium": 2,

        "Low": 3,

        "Maintain": 4
    }

    recommendations.sort(

        key=lambda item:
        priority_order.get(
            item["priority"],
            5
        )
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

    print(
        "=========================================="
    )

    print(
        "PERSONALIZED SKILL RECOMMENDATIONS"
    )

    print(
        "=========================================="
    )

    for recommendation in result:

        print(
            f"\nSkill: "
            f"{recommendation['skill']}"
        )

        print(
            f"Priority: "
            f"{recommendation['priority']}"
        )

        print(
            f"Status: "
            f"{recommendation['status']}"
        )

        print(
            f"Current Score: "
            f"{recommendation['current_score']}"
        )

        print(
            f"Target Score: "
            f"{recommendation['target_score']}"
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

    print(
        "\n=========================================="
    )