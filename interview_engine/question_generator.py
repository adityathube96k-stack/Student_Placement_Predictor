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
    },
    {"id": 16, "category": "Technical", "difficulty": "Easy", "question": "What is the difference between a stack and a queue?", "keywords": ['stack', 'queue', 'lifo', 'fifo']},
    {"id": 17, "category": "Technical", "difficulty": "Medium", "question": "Explain what an API is and what REST means.", "keywords": ['api', 'rest', 'http', 'request', 'response']},
    {"id": 18, "category": "Technical", "difficulty": "Medium", "question": "What is normalization in databases and why is it used?", "keywords": ['normalization', 'redundancy', 'tables', 'anomaly']},
    {"id": 19, "category": "Technical", "difficulty": "Hard", "question": "What is the difference between a process and a thread?", "keywords": ['process', 'thread', 'memory', 'concurrency']},
    {"id": 20, "category": "Programming", "difficulty": "Easy", "question": "What is recursion? Give a simple example.", "keywords": ['function', 'calls itself', 'base case', 'factorial']},
    {"id": 21, "category": "Programming", "difficulty": "Medium", "question": "What is the time complexity of binary search and why?", "keywords": ['log n', 'sorted', 'half', 'divide']},
    {"id": 22, "category": "Programming", "difficulty": "Medium", "question": "Explain the difference between a shallow copy and a deep copy.", "keywords": ['copy', 'reference', 'nested', 'independent']},
    {"id": 23, "category": "Programming", "difficulty": "Hard", "question": "How would you detect a cycle in a linked list?", "keywords": ['slow', 'fast', 'pointer', 'floyd']},
    {"id": 24, "category": "Aptitude", "difficulty": "Easy", "question": "A train 120 m long passes a pole in 6 seconds. What is its speed in km/h?", "keywords": ['20', 'm/s', '72', 'km/h']},
    {"id": 25, "category": "Aptitude", "difficulty": "Easy", "question": "If 8 workers finish a job in 12 days, how many days will 12 workers need?", "keywords": ['8', '12', 'days', 'inverse']},
    {"id": 26, "category": "Aptitude", "difficulty": "Medium", "question": "What is the next number in the series 2, 6, 12, 20, 30, ...?", "keywords": ['42', 'difference', 'consecutive', 'n(n+1)']},
    {"id": 27, "category": "Aptitude", "difficulty": "Medium", "question": "A shopkeeper marks an item 20% above cost and gives 10% discount. What is the profit percent?", "keywords": ['8', 'profit', 'marked', 'discount']},
    {"id": 28, "category": "Aptitude", "difficulty": "Medium", "question": "Two pipes fill a tank in 10 and 15 hours. How long together?", "keywords": ['6', 'hours', 'rate', 'together']},
    {"id": 29, "category": "HR", "difficulty": "Easy", "question": "Why do you want to join our company?", "keywords": ['company', 'growth', 'skills', 'contribute', 'learn']},
    {"id": 30, "category": "HR", "difficulty": "Medium", "question": "Where do you see yourself in five years?", "keywords": ['goals', 'growth', 'career', 'learn', 'skills']},
    {"id": 31, "category": "HR", "difficulty": "Medium", "question": "Describe a time you worked in a team to solve a problem.", "keywords": ['team', 'role', 'problem', 'result', 'communication']},
    {"id": 32, "category": "Behavioral", "difficulty": "Medium", "question": "Tell me about a time you failed and what you learned.", "keywords": ['failure', 'learned', 'improve', 'situation', 'action']},
    {"id": 33, "category": "Behavioral", "difficulty": "Medium", "question": "How do you handle tight deadlines or pressure?", "keywords": ['prioritize', 'plan', 'deadline', 'communicate', 'focus']},
    {"id": 34, "category": "Behavioral", "difficulty": "Easy", "question": "How do you handle disagreement with a teammate?", "keywords": ['listen', 'respect', 'discuss', 'solution', 'compromise']},
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