REQUIRED_SECTIONS = {
    "Contact Information": [
        "email",
        "phone",
        "mobile"
    ],
    "Education": [
        "education",
        "academic"
    ],
    "Skills": [
        "skills",
        "technical skills"
    ],
    "Projects": [
        "projects",
        "project"
    ],
    "Experience": [
        "experience",
        "internship",
        "work experience"
    ],
    "Certifications": [
        "certifications",
        "certification",
        "courses"
    ],
    "Achievements": [
        "achievements",
        "awards"
    ]
}


def normalize_text(text):
    """
    Convert resume text to lowercase for analysis.
    """

    if not text:
        return ""

    return " ".join(text.lower().split())


def check_sections(resume_text):
    """
    Check important sections available in the resume.
    """

    text = normalize_text(resume_text)

    sections = {}

    for section, keywords in REQUIRED_SECTIONS.items():

        found = False

        for keyword in keywords:
            if keyword in text:
                found = True
                break

        sections[section] = found

    return sections


def calculate_section_score(sections):
    """
    Calculate score based on important resume sections.
    """

    if not sections:
        return 0

    total_sections = len(sections)
    completed_sections = sum(
        1 for exists in sections.values()
        if exists
    )

    score = (
        completed_sections / total_sections
    ) * 100

    return round(score, 2)


def calculate_skill_score(extracted_skills):
    """
    Calculate score based on number of technical skills.
    """

    if not extracted_skills:
        return 0

    total_skills = set()

    for skills in extracted_skills.values():
        total_skills.update(skills)

    skill_count = len(total_skills)

    if skill_count >= 15:
        return 100

    if skill_count >= 10:
        return 85

    if skill_count >= 7:
        return 70

    if skill_count >= 5:
        return 55

    if skill_count >= 3:
        return 40

    return 20


def calculate_length_score(resume_text):
    """
    Calculate score based on resume text length.
    """

    word_count = len(
        normalize_text(resume_text).split()
    )

    if word_count >= 300:
        return 100

    if word_count >= 200:
        return 85

    if word_count >= 100:
        return 70

    if word_count >= 50:
        return 50

    return 25


def calculate_resume_score(
    resume_text,
    extracted_skills=None
):
    """
    Calculate overall resume score.

    Components:
        Section Score  = 50%
        Skill Score    = 30%
        Length Score   = 20%
    """

    if not resume_text:
        raise ValueError(
            "Resume text cannot be empty."
        )

    sections = check_sections(resume_text)

    section_score = calculate_section_score(
        sections
    )

    skill_score = calculate_skill_score(
        extracted_skills
    )

    length_score = calculate_length_score(
        resume_text
    )

    overall_score = (
        section_score * 0.50
        + skill_score * 0.30
        + length_score * 0.20
    )

    overall_score = round(
        max(0, min(100, overall_score)),
        2
    )

    if overall_score >= 80:
        rating = "Excellent"
    elif overall_score >= 65:
        rating = "Good"
    elif overall_score >= 50:
        rating = "Average"
    else:
        rating = "Needs Improvement"

    return {
        "overall_score": overall_score,
        "rating": rating,
        "section_score": round(
            section_score,
            2
        ),
        "skill_score": round(
            skill_score,
            2
        ),
        "length_score": round(
            length_score,
            2
        ),
        "sections": sections
    }


if __name__ == "__main__":

    sample_resume = """
    Aditya Thube

    Email: aditya@example.com
    Phone: 9876543210

    Education:
    Bachelor of Technology in Information Technology

    Skills:
    Python, Java, C++, HTML, CSS, JavaScript,
    Flask, MySQL, Git, GitHub, Machine Learning,
    Pandas, NumPy, Scikit-learn

    Projects:
    Student Placement Predictor
    Real-Time Fraud Detection System

    Internship:
    Web Development Intern

    Certifications:
    Python Certification
    Machine Learning Certification

    Achievements:
    Hackathon Participant
    """

    sample_skills = {
        "Programming Languages": [
            "Python",
            "Java",
            "C++"
        ],
        "Web Technologies": [
            "HTML",
            "CSS",
            "JavaScript",
            "Flask"
        ],
        "Database": [
            "MySQL"
        ],
        "Data Science & AI": [
            "Machine Learning",
            "Pandas",
            "NumPy",
            "Scikit-learn"
        ],
        "Cloud & DevOps": [
            "Git",
            "GitHub"
        ]
    }

    result = calculate_resume_score(
        sample_resume,
        sample_skills
    )

    print("==========================================")
    print("RESUME SCORE ANALYZER")
    print("==========================================")

    print(
        f"Overall Score : "
        f"{result['overall_score']}%"
    )

    print(
        f"Rating        : "
        f"{result['rating']}"
    )

    print(
        f"Section Score : "
        f"{result['section_score']}%"
    )

    print(
        f"Skill Score   : "
        f"{result['skill_score']}%"
    )

    print(
        f"Length Score  : "
        f"{result['length_score']}%"
    )

    print("\nSections:")

    for section, found in result["sections"].items():
        status = "Found" if found else "Missing"
        print(f"- {section}: {status}")

    print("==========================================")