import re


SKILL_CATEGORIES = {
    "Programming Languages": [
        "Python",
        "Java",
        "C",
        "C++",
        "C#",
        "JavaScript",
        "TypeScript",
        "PHP",
        "Go",
        "Ruby"
    ],

    "Web Technologies": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Angular",
        "Vue",
        "Node.js",
        "Express.js",
        "Flask",
        "Django"
    ],

    "Database": [
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQLite",
        "Oracle",
        "SQL",
        "Redis"
    ],

    "Data Science & AI": [
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Data Science",
        "NLP",
        "Natural Language Processing",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch"
    ],

    "Cloud & DevOps": [
        "AWS",
        "Azure",
        "Google Cloud",
        "Docker",
        "Kubernetes",
        "Git",
        "GitHub",
        "Jenkins"
    ],

    "Core Computer Science": [
        "Data Structures",
        "Algorithms",
        "DBMS",
        "Operating Systems",
        "Computer Networks",
        "Object Oriented Programming",
        "OOP"
    ],

    "Tools": [
        "VS Code",
        "Jupyter",
        "Postman",
        "Figma",
        "Linux"
    ]
}


def normalize_text(text):
    """
    Convert resume text into a normalized format.
    """

    if not text:
        return ""

    text = text.lower()

    # Replace multiple spaces/newlines with one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def skill_exists(text, skill):
    """
    Check whether a skill exists in resume text.
    """

    text = normalize_text(text)
    skill = skill.lower()

    # Special handling for symbols such as C++
    if skill in ["c++", "c#"]:
        return skill in text

    pattern = r"\b" + re.escape(skill) + r"\b"

    return re.search(pattern, text) is not None


def extract_skills(resume_text):
    """
    Extract technical skills from resume text.

    Returns:
        {
            "Programming Languages": [...],
            "Web Technologies": [...],
            ...
        }
    """

    if not resume_text:
        return {}

    extracted_skills = {}

    for category, skills in SKILL_CATEGORIES.items():

        found_skills = []

        for skill in skills:

            if skill_exists(resume_text, skill):
                found_skills.append(skill)

        if found_skills:
            extracted_skills[category] = found_skills

    return extracted_skills


def get_all_skills(extracted_skills):
    """
    Convert categorized skills into one list.
    """

    all_skills = []

    for skills in extracted_skills.values():
        all_skills.extend(skills)

    return sorted(set(all_skills))


def get_skill_count(extracted_skills):
    """
    Return total number of unique skills.
    """

    return len(get_all_skills(extracted_skills))


if __name__ == "__main__":

    sample_resume = """
    Aditya Thube is an Information Technology student.

    Skills:
    Python, Java, C++, HTML, CSS, JavaScript,
    Flask, MySQL, Git, GitHub, Machine Learning,
    Pandas, NumPy, Scikit-learn, DBMS and Data Structures.
    """

    print("==========================================")
    print("RESUME SKILL EXTRACTOR")
    print("==========================================")

    skills = extract_skills(sample_resume)

    for category, category_skills in skills.items():
        print(f"\n{category}:")
        for skill in category_skills:
            print(f"  - {skill}")

    print("\n==========================================")
    print(f"Total Skills: {get_skill_count(skills)}")
    print("==========================================")