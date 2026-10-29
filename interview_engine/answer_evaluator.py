# interview_engine/answer_evaluator.py


def evaluate_answer(answer, keywords):
    """
    Evaluate an interview answer using keyword matching.

    Returns:
        dict: score, matched keywords, missing keywords,
        and evaluation status.
    """

    if not answer or not answer.strip():
        return {
            "word_count": 0,
            "score": 0,
            "matched_keywords": [],
            "missing_keywords": keywords,
            "status": "No Answer"
        }

    answer_text = answer.lower().strip()

    matched_keywords = []
    missing_keywords = []

    for keyword in keywords:
        keyword_text = str(keyword).lower().strip()

        if keyword_text and keyword_text in answer_text:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    total_keywords = len(keywords)

    if total_keywords == 0:
        score = 0
    else:
        score = (
            len(matched_keywords) / total_keywords
        ) * 100

    score = round(score, 2)

    if score >= 80:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    elif score >= 40:
        status = "Average"
    else:
        status = "Needs Improvement"

    words = len(answer_text.split())
    if words < 12:  # one-liners cannot earn a full score
        score = min(score, 60.0)
        status = "Needs Improvement" if score < 40 else "Average"
    return {
        "word_count": words,
        "score": score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "status": status
    }