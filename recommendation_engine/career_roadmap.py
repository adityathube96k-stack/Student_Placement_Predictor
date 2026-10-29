"""Month-by-month career roadmap."""
from utils.helpers import split_skills

ROLES = [
    ("Backend / Software Developer", {"python", "java", "sql", "data structures", "git"}),
    ("Web Developer", {"html", "css", "javascript", "react", "git"}),
    ("Data Analyst / Data Scientist", {"python", "sql", "machine learning", "data science"}),
    ("Cloud / DevOps Engineer", {"aws", "docker", "linux", "git", "python"}),
]

FOCUS_PLAN = {
    "Aptitude": ("Aptitude and reasoning", ["Complete one quantitative set a day", "Take two timed mocks"]),
    "Coding": ("Coding practice", ["Solve 60 DSA problems", "Finish one contest per week"]),
    "Communication": ("Communication", ["Practise 5 HR answers aloud", "Do 2 mock group discussions"]),
    "Technical": ("Core CS and projects", ["Revise DBMS, OS, networks", "Ship one deployable project"]),
}


def suggest_roles(student_skills, limit=3):
    have = {s.lower() for s in split_skills(student_skills)}
    scored = []
    for role, needed in ROLES:
        matched = sorted(needed & have)
        scored.append({"role": role, "match": round(len(matched) * 100 / len(needed)),
                       "matched": matched, "to_learn": sorted(needed - have)})
    scored.sort(key=lambda r: -r["match"])
    return scored[:limit]


def build_roadmap(skill_gap, student_skills=None, months=6):
    """skill_gap is the output of calculate_skill_gap()."""
    skills = skill_gap["skills"]
    order = sorted(skills, key=lambda s: -skills[s]["gap"])
    roles = suggest_roles(student_skills)
    top_role = roles[0] if roles else None
    plan = []
    for month in range(1, months + 1):
        area = order[(month - 1) % len(order)]
        title, tasks = FOCUS_PLAN[area]
        goals = list(tasks)
        milestone = f"Raise {area.lower()} score by {max(3, round(skills[area]['gap'] / 2))} points"
        if month == 1:
            goals.insert(0, "Update profile scores and upload your resume")
        if month == 2 and top_role and top_role["to_learn"]:
            goals.append("Learn " + ", ".join(top_role["to_learn"][:2]).title())
        if month == 3:
            goals.append("Take one full mock interview and review the feedback")
        if month == months - 1:
            goals.append("Apply to every drive you are eligible for")
            milestone = "Resume, projects and mock-interview scores all at target"
        if month == months:
            goals = ["Attend drives and interviews", "Review feedback after each round",
                     "Keep daily practice going"]
            milestone = "Placement outcome: offer in hand"
        plan.append({"month": month, "title": title if month < months else "Placement season",
                     "goals": goals, "milestone": milestone,
                     "hours": 40 if month < months else 25})
    return {"target_roles": roles, "months": plan, "priority_order": order,
            "summary": f"Start with {order[0].lower()} then {order[1].lower()}; "
                       f"your closest role match is {top_role['role'] if top_role else 'not clear yet'}."}
