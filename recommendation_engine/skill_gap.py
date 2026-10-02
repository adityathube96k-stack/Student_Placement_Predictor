# =====================================================
# SKILL GAP ANALYSIS
# =====================================================

def calculate_skill_gap(
    aptitude_score,
    coding_score,
    communication_score,
    technical_score
):
    """
    Analyze student's skills and identify
    areas that need improvement.
    """

    # =================================================
    # VALIDATE INPUTS
    # =================================================

    scores = {
        "Aptitude": aptitude_score,
        "Coding": coding_score,
        "Communication": communication_score,
        "Technical": technical_score
    }

    try:
        scores = {
            skill: float(score)
            for skill, score in scores.items()
        }

    except (TypeError, ValueError):
        raise ValueError(
            "All skill scores must be numeric."
        )

    for skill, score in scores.items():

        if not 0 <= score <= 100:
            raise ValueError(
                f"{skill} score must be between 0 and 100."
            )

    # =================================================
    # TARGET SCORES
    # =================================================

    target_scores = {
        "Aptitude": 75,
        "Coding": 75,
        "Communication": 70,
        "Technical": 75
    }

    # =================================================
    # CALCULATE GAP
    # =================================================

    skill_analysis = {}

    for skill in scores:

        current_score = scores[skill]
        target_score = target_scores[skill]

        gap = max(
            0,
            target_score - current_score
        )

        if gap == 0:
            status = "Strong"

        elif gap <= 10:
            status = "Needs Improvement"

        else:
            status = "High Priority"

        skill_analysis[skill] = {
            "current_score": round(
                current_score, 2
            ),
            "target_score": target_score,
            "gap": round(
                gap, 2
            ),
            "status": status
        }

    # =================================================
    # FIND PRIORITY SKILLS
    # =================================================

    priority_skills = sorted(
        skill_analysis.items(),
        key=lambda item: item[1]["gap"],
        reverse=True
    )

    priority_skills = [
        skill
        for skill, data in priority_skills
        if data["gap"] > 0
    ]

    # =================================================
    # OVERALL SKILL STATUS
    # =================================================

    total_gap = sum(
        data["gap"]
        for data in skill_analysis.values()
    )

    if total_gap == 0:

        overall_status = "All Target Skills Achieved"

    elif total_gap <= 20:

        overall_status = "Minor Skill Gaps"

    elif total_gap <= 50:

        overall_status = "Moderate Skill Gaps"

    else:

        overall_status = "Significant Skill Gaps"

    # =================================================
    # RETURN RESULT
    # =================================================

    return {

        "skills": skill_analysis,

        "priority_skills":
            priority_skills,

        "total_gap":
            round(total_gap, 2),

        "overall_status":
            overall_status
    }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    try:

        result = calculate_skill_gap(

            aptitude_score=75,

            coding_score=68,

            communication_score=61.84,

            technical_score=60.06
        )

        print("==========================================")
        print("SKILL GAP ANALYSIS")
        print("==========================================")

        for skill, data in result["skills"].items():

            print(
                f"{skill:<15} "
                f"Current: {data['current_score']:<6} "
                f"Target: {data['target_score']:<6} "
                f"Gap: {data['gap']:<6} "
                f"Status: {data['status']}"
            )

        print("------------------------------------------")

        print(
            "Overall Status:",
            result["overall_status"]
        )

        print(
            "Priority Skills:",
            ", ".join(result["priority_skills"])
        )

        print(
            "Total Skill Gap:",
            result["total_gap"]
        )

        print("==========================================")

    except Exception as error:

        print(
            "Skill Gap Error:",
            error
        )