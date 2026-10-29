"""Company, drive and skills-demand analytics."""
from collections import Counter

from analytics.placement_analytics import _complete, _students
from company_eligibility.eligibility_checker import check_all_companies
from database.db import query_all
from models.company import Company
from utils.helpers import split_skills


def eligibility_matrix():
    """For each active company: how many students currently qualify."""
    companies = [Company.as_rule(c) for c in Company.all(active_only=True)]
    students = [s for s in _students() if _complete(s)]
    eligible_ids = {c["id"]: [] for c in companies}
    for s in students:
        for result in check_all_companies(
                s["cgpa"], s["attendance"], s["aptitude_score"], s["coding_score"],
                s["communication_score"], s["technical_score"], s.get("skills"),
                s.get("backlogs") or 0, companies):
            if result["eligible"]:
                eligible_ids[result["company_id"]].append(s["user_id"])
    rows = [{"company": c["name"], "company_id": c["id"], "package_lpa": c["package_lpa"],
             "eligible": len(eligible_ids[c["id"]]), "assessed": len(students)} for c in companies]
    return sorted(rows, key=lambda r: -r["eligible"])


def drive_funnel():
    counts = Counter(r["status"] for r in query_all("SELECT status FROM drive_applications"))
    order = ["Applied", "Shortlisted", "Selected", "Rejected"]
    return [{"stage": s, "count": counts.get(s, 0)} for s in order]


def skills_demand_vs_supply(limit=10):
    demand = Counter()
    for c in Company.all(active_only=True):
        for skill in split_skills(c.get("required_skills")):
            demand[skill.lower()] += 1
    supply = Counter()
    for s in _students():
        for skill in split_skills(s.get("skills")):
            supply[skill.lower()] += 1
    total = max(len(_students()), 1)
    rows = [{"skill": k.title() if len(k) > 3 else k.upper(), "companies": v,
             "students": supply.get(k, 0), "coverage": round(supply.get(k, 0) * 100 / total)}
            for k, v in demand.most_common(limit)]
    return rows
