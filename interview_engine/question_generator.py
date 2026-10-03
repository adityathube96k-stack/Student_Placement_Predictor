# interview_engine/question_bank.py

INTERVIEW_QUESTIONS = [
    {
        "id": 1,
        "category": "Technical",
        "difficulty": "Easy",
        "question": "What is the difference between a list and a tuple in Python?",
        "keywords": [
            "list",
            "tuple",
            "mutable",
            "immutable"
        ]
    },
    {
        "id": 2,
        "category": "Technical",
        "difficulty": "Easy",
        "question": "What is OOP? Explain its main principles.",
        "keywords": [
            "object",
            "class",
            "encapsulation",
            "inheritance",
            "polymorphism",
            "abstraction"
        ]
    },
    {
        "id": 3,
        "category": "Technical",
        "difficulty": "Medium",
        "question": "What is the difference between SQL and NoSQL databases?",
        "keywords": [
            "sql",
            "nosql",
            "relational",
            "non relational",
            "tables",
            "documents"
        ]
    },
    {
        "id": 4,
        "category": "Technical",
        "difficulty": "Medium",
        "question": "What is a primary key in a database?",
        "keywords": [
            "primary key",
            "unique",
            "identify",
            "record",
            "row"
        ]
    },
    {
        "id": 5,
        "category": "Technical",
        "difficulty": "Medium",
        "question": "What is machine learning?",
        "keywords": [
            "machine learning",
            "data",
            "model",
            "training",
            "prediction"
        ]
    },
    {
        "id": 6,
        "category": "Programming",
        "difficulty": "Medium",
        "question": "What is the difference between == and = in Python?",
        "keywords": [
            "comparison",
            "assignment",
            "equal",
            "value"
        ]
    },
    {
        "id": 7,
        "category": "Programming",
        "difficulty": "Medium",
        "question": "What is a function in programming?",
        "keywords": [
            "function",
            "block",
            "code",
            "reuse",
            "parameter",
            "return"
        ]
    },
    {
        "id": 8,
        "category": "HR",
        "difficulty": "Easy",
        "question": "Tell me about yourself.",
        "keywords": [
            "education",
            "skills",
            "project",
            "experience",
            "career"
        ]
    },
    {
        "id": 9,
        "category": "HR",
        "difficulty": "Easy",
        "question": "What are your strengths?",
        "keywords": [
            "strength",
            "communication",
            "teamwork",
            "problem solving",
            "learning"
        ]
    },
    {
        "id": 10,
        "category": "HR",
        "difficulty": "Easy",
        "question": "What are your weaknesses?",
        "keywords": [
            "weakness",
            "improvement",
            "learning",
            "development"
        ]
    },
    {
        "id": 11,
        "category": "HR",
        "difficulty": "Medium",
        "question": "Why should we hire you?",
        "keywords": [
            "skills",
            "knowledge",
            "project",
            "contribution",
            "learning"
        ]
    },
    {
        "id": 12,
        "category": "HR",
        "difficulty": "Medium",
        "question": "Where do you see yourself in five years?",
        "keywords": [
            "career",
            "growth",
            "skills",
            "experience",
            "leadership"
        ]
    },
    {
        "id": 13,
        "category": "Behavioral",
        "difficulty": "Medium",
        "question": "Describe a challenging project you worked on.",
        "keywords": [
            "project",
            "challenge",
            "problem",
            "solution",
            "result"
        ]
    },
    {
        "id": 14,
        "category": "Behavioral",
        "difficulty": "Medium",
        "question": "How do you handle working in a team?",
        "keywords": [
            "team",
            "communication",
            "collaboration",
            "responsibility",
            "support"
        ]
    },
    {
        "id": 15,
        "category": "Behavioral",
        "difficulty": "Hard",
        "question": "How do you handle failure?",
        "keywords": [
            "failure",
            "mistake",
            "learning",
            "improvement",
            "experience"
        ]
    }
]


def get_all_questions():
    return INTERVIEW_QUESTIONS


def get_questions_by_category(category):
    return [
        question
        for question in INTERVIEW_QUESTIONS
        if question["category"].lower() == category.lower()
    ]


def get_questions_by_difficulty(difficulty):
    return [
        question
        for question in INTERVIEW_QUESTIONS
        if question["difficulty"].lower() == difficulty.lower()
    ]


def get_question_by_id(question_id):
    for question in INTERVIEW_QUESTIONS:
        if question["id"] == question_id:
            return question

    return None


if __name__ == "__main__":
    print("Total Questions:", len(get_all_questions()))

    for question in get_all_questions():
        print(
            f"{question['id']}. "
            f"[{question['category']}] "
            f"{question['question']}"
        )