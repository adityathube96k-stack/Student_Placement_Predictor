"""Course recommendations driven by skill gaps and missing company skills."""
from utils.helpers import split_skills

_C = lambda title, provider, level, hours, url, free=True: {  # noqa: E731
    "title": title, "provider": provider, "level": level, "hours": hours, "url": url, "free": free}

NPTEL, COURSERA, GFG = "https://nptel.ac.in", "https://www.coursera.org", "https://www.geeksforgeeks.org"

CATALOG = {
    "Aptitude": [
        _C("Quantitative aptitude practice sets", "IndiaBIX", "Beginner", 20, "https://www.indiabix.com"),
        _C("Logical reasoning and data interpretation", "GeeksforGeeks", "Intermediate", 25, GFG),
        _C("Timed aptitude mock tests", "PrepInsta", "Intermediate", 15, "https://prepinsta.com"),
    ],
    "Coding": [
        _C("Data structures and algorithms in Python", "NPTEL", "Intermediate", 40, NPTEL),
        _C("Problem solving track", "LeetCode", "Intermediate", 60, "https://leetcode.com"),
        _C("Competitive programming basics", "HackerRank", "Beginner", 30, "https://www.hackerrank.com"),
    ],
    "Communication": [
        _C("English communication for professionals", "Coursera", "Beginner", 18, COURSERA, False),
        _C("Group discussion and interview skills", "NPTEL", "Beginner", 15, NPTEL),
        _C("Presentation and public speaking", "edX", "Intermediate", 20, "https://www.edx.org", False),
    ],
    "Technical": [
        _C("Database management systems", "NPTEL", "Intermediate", 35, NPTEL),
        _C("Operating systems and networks", "GeeksforGeeks", "Intermediate", 30, GFG),
        _C("Software engineering fundamentals", "Coursera", "Intermediate", 25, COURSERA, False),
    ],
}

BY_SKILL = {
    "python": _C("Python for everybody", "Coursera", "Beginner", 30, COURSERA, False),
    "java": _C("Java programming and OOP", "NPTEL", "Beginner", 40, NPTEL),
    "sql": _C("SQL for data work", "Kaggle Learn", "Beginner", 8, "https://www.kaggle.com/learn"),
    "data structures": _C("Data structures masterclass", "GeeksforGeeks", "Intermediate", 35, GFG),
    "algorithms": _C("Algorithms specialisation", "Coursera", "Intermediate", 45, COURSERA, False),
    "machine learning": _C("Machine learning crash course", "Kaggle Learn", "Intermediate", 20, "https://www.kaggle.com/learn"),
    "data science": _C("Data science with Python", "NPTEL", "Intermediate", 40, NPTEL),
    "html": _C("Responsive web design", "freeCodeCamp", "Beginner", 25, "https://www.freecodecamp.org"),
    "css": _C("CSS layout and Flexbox/Grid", "MDN Web Docs", "Beginner", 12, "https://developer.mozilla.org"),
    "javascript": _C("JavaScript algorithms and data structures", "freeCodeCamp", "Beginner", 40, "https://www.freecodecamp.org"),
    "react": _C("Front-end libraries with React", "freeCodeCamp", "Intermediate", 30, "https://www.freecodecamp.org"),
    "aws": _C("AWS cloud practitioner essentials", "AWS Skill Builder", "Beginner", 12, "https://skillbuilder.aws"),
    "docker": _C("Docker and containers", "roadmap.sh", "Beginner", 10, "https://roadmap.sh"),
    "git": _C("Git and GitHub essentials", "GitHub Skills", "Beginner", 6, "https://skills.github.com"),
    "linux": _C("Linux command line basics", "NPTEL", "Beginner", 15, NPTEL),
    "communication": _C("Business communication", "Coursera", "Beginner", 15, COURSERA, False),
    "problem solving": _C("Problem solving with code", "HackerRank", "Beginner", 25, "https://www.hackerrank.com"),
}


def recommend_courses(skill_analysis, student_skills=None, missing_skills=None, limit=8):
    """Return a prioritised course list: weakest areas first, then missing skills."""
    courses, seen = [], set()

    def add(course, reason, priority):
        if course["title"] not in seen:
            seen.add(course["title"])
            courses.append(dict(course, reason=reason, priority=priority))

    ordered = sorted((skill_analysis or {}).items(), key=lambda kv: -kv[1].get("gap", 0))
    for area, data in ordered:
        gap = data.get("gap", 0)
        if gap <= 0:
            continue
        priority = "High" if gap > 10 else "Medium"
        for course in CATALOG.get(area, [])[:2]:
            add(course, f"{area} is {gap:g} points below target", priority)

    have = {s.lower() for s in split_skills(student_skills) if s} if isinstance(student_skills, str) \
        else {str(s).lower() for s in (student_skills or [])}
    for skill in missing_skills or []:
        course = BY_SKILL.get(str(skill).lower())
        if course and str(skill).lower() not in have:
            add(course, f"Required by companies you are targeting: {skill}", "Medium")

    if not courses:
        for area in CATALOG:
            add(CATALOG[area][0], f"Keep your {area.lower()} sharp", "Maintain")
    return courses[:limit]
