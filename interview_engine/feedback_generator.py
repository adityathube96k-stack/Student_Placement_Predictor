# interview_engine/feedback_generator.py


def generate_feedback(evaluation_results, interview_score):
    """
    Generate overall feedback for a mock interview.
    """

    feedback = []

    if interview_score >= 80:
        feedback.append(
            "Excellent interview performance. "
            "Your answers demonstrate strong understanding."
        )

    elif interview_score >= 65:
        feedback.append(
            "Good interview performance. "
            "You have a solid foundation, but some areas can be improved."
        )

    elif interview_score >= 50:
        feedback.append(
            "Average interview performance. "
            "Focus on improving your technical and communication skills."
        )

    else:
        feedback.append(
            "Your interview performance needs improvement. "
            "Practice regularly and strengthen your fundamentals."
        )

    total_questions = len(evaluation_results)

    if total_questions > 0:
        excellent_answers = sum(
            1
            for result in evaluation_results
            if result["evaluation"]["score"] >= 80
        )

        weak_answers = sum(
            1
            for result in evaluation_results
            if result["evaluation"]["score"] < 40
        )

        if excellent_answers > 0:
            feedback.append(
                f"You performed strongly on "
                f"{excellent_answers} question(s)."
            )

        if weak_answers > 0:
            feedback.append(
                f"{weak_answers} question(s) need more practice."
            )

    feedback.append(
        "Review the missing keywords from your answers "
        "and practice explaining concepts clearly."
    )

    return feedback


if __name__ == "__main__":
    sample_results = [
        {
            "question": "What is Python?",
            "evaluation": {
                "score": 80,
                "status": "Excellent",
                "matched_keywords": ["language", "programming"],
                "missing_keywords": []
            }
        }
    ]

    sample_feedback = generate_feedback(
        sample_results,
        80
    )

    for item in sample_feedback:
        print("-", item)