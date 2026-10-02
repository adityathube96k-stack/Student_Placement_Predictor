# =====================================================
# PLACEMENT READINESS SCORE
# =====================================================

def validate_scores(
    cgpa,
    attendance,
    aptitude_score,
    coding_score,
    communication_score,
    technical_score
):
    """
    Validate student scores before calculating
    placement readiness.
    """

    values = [
        cgpa,
        attendance,
        aptitude_score,
        coding_score,
        communication_score,
        technical_score
    ]

    try:
        values = [float(value) for value in values]

    except (TypeError, ValueError):
        raise ValueError("All scores must be numeric.")

    if not 0 <= values[0] <= 10:
        raise ValueError("CGPA must be between 0 and 10.")

    for value in values[1:]:
        if not 0 <= value <= 100:
            raise ValueError(
                "Attendance and skill scores must be between 0 and 100."
            )

    return values


def calculate_readiness_score(
    cgpa,
    attendance,
    aptitude_score,
    coding_score,
    communication_score,
    technical_score
):
    """
    Calculate overall placement readiness score.

    Score is calculated on a scale of 0-100.
    """

    values = validate_scores(
        cgpa,
        attendance,
        aptitude_score,
        coding_score,
        communication_score,
        technical_score
    )

    (
        cgpa,
        attendance,
        aptitude_score,
        coding_score,
        communication_score,
        technical_score
    ) = values


    # =================================================
    # NORMALIZE CGPA
    # =================================================

    cgpa_score = (cgpa / 10) * 100


    # =================================================
    # WEIGHTS
    # =================================================

    weights = {
        "cgpa": 0.20,
        "attendance": 0.15,
        "aptitude": 0.15,
        "coding": 0.20,
        "communication": 0.15,
        "technical": 0.15
    }


    # =================================================
    # CALCULATE WEIGHTED SCORE
    # =================================================

    weighted_scores = {

        "cgpa": cgpa_score * weights["cgpa"],

        "attendance":
            attendance * weights["attendance"],

        "aptitude":
            aptitude_score * weights["aptitude"],

        "coding":
            coding_score * weights["coding"],

        "communication":
            communication_score * weights["communication"],

        "technical":
            technical_score * weights["technical"]
    }


    readiness_score = sum(weighted_scores.values())


    # Keep score between 0 and 100
    readiness_score = max(
        0,
        min(100, readiness_score)
    )


    # =================================================
    # READINESS LEVEL
    # =================================================

    if readiness_score >= 80:
        readiness_level = "Excellent"

    elif readiness_score >= 65:
        readiness_level = "Good"

    elif readiness_score >= 50:
        readiness_level = "Moderate"

    else:
        readiness_level = "Needs Improvement"


    return {

        "readiness_score":
            round(readiness_score, 2),

        "readiness_level":
            readiness_level,

        "breakdown": {

            "cgpa":
                round(cgpa_score, 2),

            "attendance":
                round(attendance, 2),

            "aptitude":
                round(aptitude_score, 2),

            "coding":
                round(coding_score, 2),

            "communication":
                round(communication_score, 2),

            "technical":
                round(technical_score, 2)
        },

        "weighted_scores": {

            "cgpa":
                round(weighted_scores["cgpa"], 2),

            "attendance":
                round(weighted_scores["attendance"], 2),

            "aptitude":
                round(weighted_scores["aptitude"], 2),

            "coding":
                round(weighted_scores["coding"], 2),

            "communication":
                round(weighted_scores["communication"], 2),

            "technical":
                round(weighted_scores["technical"], 2)
        }
    }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    try:

        result = calculate_readiness_score(
            cgpa=7.5,
            attendance=92,
            aptitude_score=75,
            coding_score=68,
            communication_score=61.84,
            technical_score=60.06
        )

        print("==========================================")
        print("PLACEMENT READINESS SCORE")
        print("==========================================")

        print(
            f"Readiness Score : "
            f"{result['readiness_score']}/100"
        )

        print(
            f"Readiness Level : "
            f"{result['readiness_level']}"
        )

        print("------------------------------------------")
        print("SKILL BREAKDOWN")
        print("------------------------------------------")

        for skill, score in result["breakdown"].items():

            print(
                f"{skill.capitalize():<15}: "
                f"{score}"
            )

        print("==========================================")

    except Exception as error:

        print(
            "Readiness Score Error:",
            error
        )