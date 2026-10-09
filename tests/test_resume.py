from resume_analyzer.resume_score import calculate_resume_score


def test_resume_score_returns_result():
    result = calculate_resume_score(
        "Python, SQL, communication, projects, education"
    )

    assert result is not None


def test_resume_score_is_valid():
    result = calculate_resume_score(
        "Python, SQL, Flask, machine learning, projects, education"
    )

    assert isinstance(result, (int, float, dict))