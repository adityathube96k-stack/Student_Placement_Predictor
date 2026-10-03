# interview_engine/interview_score.py


def calculate_interview_score(evaluation_results):
    """
    Calculate the overall mock interview score.

    Each question contributes equally to the
    final interview score.
    """

    if not evaluation_results:
        return 0.0

    total_score = 0.0

    for result in evaluation_results:
        evaluation = result.get("evaluation", {})
        score = evaluation.get("score", 0)
        total_score += float(score)

    final_score = total_score / len(evaluation_results)

    return round(final_score, 2)


def get_score_level(score):
    """
    Convert interview score into a performance level.
    """

    score = float(score)

    if score >= 80:
        return "Excellent"

    if score >= 65:
        return "Good"

    if score >= 50:
        return "Average"

    return "Needs Improvement"


if __name__ == "__main__":

    sample_results = [
        {
            "question": "Question 1",
            "evaluation": {
                "score": 80
            }
        },
        {
            "question": "Question 2",
            "evaluation": {
                "score": 60
            }
        },
        {
            "question": "Question 3",
            "evaluation": {
                "score": 70
            }
        }
    ]

    score = calculate_interview_score(sample_results)
    level = get_score_level(score)

    print("Interview Score:", score)
    print("Performance Level:", level)