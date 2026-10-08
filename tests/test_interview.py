from interview_engine.question_generator import (
    get_all_questions,
    get_questions_by_category,
    get_questions_by_difficulty,
    get_question_by_id
)


def test_get_all_questions():
    questions = get_all_questions()

    assert questions is not None
    assert len(questions) == 15


def test_questions_have_required_fields():
    questions = get_all_questions()

    for question in questions:
        assert "id" in question
        assert "category" in question
        assert "difficulty" in question
        assert "question" in question
        assert "keywords" in question


def test_get_questions_by_category():
    technical_questions = get_questions_by_category("Technical")

    assert len(technical_questions) == 5

    for question in technical_questions:
        assert question["category"] == "Technical"


def test_get_questions_by_difficulty():
    medium_questions = get_questions_by_difficulty("Medium")

    assert len(medium_questions) > 0

    for question in medium_questions:
        assert question["difficulty"] == "Medium"


def test_get_question_by_id():
    question = get_question_by_id(1)

    assert question is not None
    assert question["id"] == 1
    assert question["category"] == "Technical"