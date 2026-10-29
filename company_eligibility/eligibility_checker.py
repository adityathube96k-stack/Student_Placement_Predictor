"""Company-wise eligibility: score thresholds, backlogs and required skills."""
from company_eligibility.company_rules import get_all_companies
from utils.helpers import split_skills


def to_float(value):
    return 0.0 if value is None else float(value)


def normalize_skills(skills):
    if isinstance(skills, str):
        skills = split_skills(skills)
    return {str(s).strip().lower() for s in (skills or []) if s and str(s).strip()}


_SCORE_RULES = [
    ("CGPA", "cgpa", "min_cgpa"),
    ("Attendance", "attendance", "min_attendance"),
    ("Aptitude Score", "aptitude_score", "min_aptitude"),
    ("Coding Score", "coding_score", "min_coding"),
    ("Communication Score", "communication_score", "min_communication"),
    ("Technical Score", "technical_score", "min_technical"),
]


def check_eligibility(company, cgpa, attendance, aptitude_score, coding_score,
                      communication_score, technical_score, student_skills=None, backlogs=0):
    student = {
        "cgpa": to_float(cgpa), "attendance": to_float(attendance),
        "aptitude_score": to_float(aptitude_score), "coding_score": to_float(coding_score),
        "communication_score": to_float(communication_score),
        "technical_score": to_float(technical_score),
    }
    missing_requirements, checks_total, checks_met = [], 0, 0
    for label, key, rule in _SCORE_RULES:
        required = to_float(company.get(rule))
        checks_total += 1
        if student[key] < required:
            missing_requirements.append({
                "requirement": label, "student_score": round(student[key], 2),
                "required_score": round(required, 2), "gap": round(required - student[key], 2)})
        else:
            checks_met += 1

    max_backlogs = int(company.get("max_backlogs") or 0)
    backlogs = int(backlogs or 0)
    checks_total += 1
    if backlogs > max_backlogs:
        missing_requirements.append({
            "requirement": "Active backlogs", "student_score": backlogs,
            "required_score": max_backlogs, "gap": backlogs - max_backlogs})
    else:
        checks_met += 1

    required_skills = company.get("required_skills", []) or []
    have = normalize_skills(student_skills)
    missing_skills = [s for s in required_skills if str(s).strip().lower() not in have]
    checks_total += len(required_skills)
    checks_met += len(required_skills) - len(missing_skills)

    return {
        "company": company["name"], "company_id": company.get("id"),
        "industry": company.get("industry"), "location": company.get("location"),
        "package_lpa": company.get("package_lpa"),
        "eligible": not missing_requirements and not missing_skills,
        "match_percent": round(checks_met * 100 / checks_total) if checks_total else 100,
        "missing_requirements": missing_requirements,
        "required_skills": required_skills,
        "missing_skills": missing_skills,
    }


def check_all_companies(cgpa, attendance, aptitude_score, coding_score, communication_score,
                        technical_score, student_skills=None, backlogs=0, companies=None):
    results = []
    for company in (companies if companies is not None else get_all_companies()):
        result = check_eligibility(
            company, cgpa, attendance, aptitude_score, coding_score,
            communication_score, technical_score, student_skills, backlogs)
        result["requirements"] = {
            "cgpa": to_float(company.get("min_cgpa")),
            "attendance": to_float(company.get("min_attendance")),
            "aptitude_score": to_float(company.get("min_aptitude")),
            "coding_score": to_float(company.get("min_coding")),
            "communication_score": to_float(company.get("min_communication")),
            "technical_score": to_float(company.get("min_technical")),
            "max_backlogs": int(company.get("max_backlogs") or 0),
        }
        results.append(result)
    results.sort(key=lambda r: (not r["eligible"], -r["match_percent"]))
    return results


def check_student(student, companies=None):
    """Convenience wrapper taking a student row (dict)."""
    return check_all_companies(
        student["cgpa"], student["attendance"], student["aptitude_score"],
        student["coding_score"], student["communication_score"], student["technical_score"],
        student.get("skills"), student.get("backlogs") or 0, companies)


def get_eligible_companies(results):
    return [r for r in results if r["eligible"]]


def get_non_eligible_companies(results):
    return [r for r in results if not r["eligible"]]
