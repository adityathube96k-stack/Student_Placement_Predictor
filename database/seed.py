"""Demo data for first run. Skipped automatically when users already exist."""
import json
import random
from datetime import date, datetime, timedelta

from company_eligibility.company_rules import COMPANIES
from company_eligibility.eligibility_checker import check_all_companies
from database.db import execute, query_one, scalar
from interview_engine.question_generator import get_all_questions
from ml.model_loader import get_metadata
from ml.predict import predict_placement
from models.company import Company, Drive
from models.user import User
from recommendation_engine.skill_gap import calculate_skill_gap
from utils.constants import BRANCHES, YEARS
from utils.security import hash_password
from utils.readiness import calculate_readiness_score

DEMO_ACCOUNTS = {
    "admin": ("Aditya Thube", "adityathube96k@gmail.com", "Aditya@123"),
    "tpo": ("Ganesh Marathe", "ganeshmarathe8232@gmail.com", "Ganesh@123"),
    "student": ("Satish Dhangar", "sdhangar811@gmail.com", "Satish@123"),
}
NAMES = ["Rohan Kulkarni", "Sneha Joshi", "Aditya More", "Pooja Shinde", "Vikram Jadhav",
         "Neha Pawar", "Siddharth Deshmukh", "Isha Kale", "Omkar Gaikwad", "Tanvi Bhosale",
         "Karan Mehta", "Ananya Iyer", "Rahul Sharma", "Kavya Nair", "Yash Thakur",
         "Shruti Chavan", "Mihir Patel", "Riya Singh", "Aman Verma", "Divya Reddy",
         "Harsh Gupta", "Meera Kapoor", "Nikhil Rao", "Sakshi Bansal", "Tejas Wagh",
         "Pranav Salunkhe", "Aishwarya Dange", "Chinmay Raut", "Gauri Nikam", "Sahil Ansari",
         "Payal Mane", "Varun Naik", "Komal Patil", "Abhishek Sawant", "Rutuja Bhise",
         "Dhruv Malhotra"]
SKILL_POOL = ["Python", "Java", "SQL", "C++", "JavaScript", "HTML", "CSS", "React", "Flask",
              "Git", "Docker", "AWS", "Machine Learning", "Data Science", "Data Structures",
              "Algorithms", "Linux", "Problem Solving", "Communication"]


_HASHES = {}  # hash each demo password once (scrypt is deliberately slow)


def _hash_once(password):
    if password not in _HASHES:
        _HASHES[password] = hash_password(password)
    return _HASHES[password]


def _clip(v, lo, hi):
    return max(lo, min(hi, v))


def _when(rng, days_back):
    return datetime.now() - timedelta(days=rng.randint(0, days_back), hours=rng.randint(0, 23),
                                      minutes=rng.randint(0, 59))


def _profile(rng, ability):
    return {
        "cgpa": round(_clip(7.0 + 0.95 * ability + rng.gauss(0, .5), 5.0, 9.8), 1),
        "attendance": round(_clip(76 + 8 * ability + rng.gauss(0, 5), 55, 99)),
        "aptitude_score": round(_clip(67 + 10 * ability + rng.gauss(0, 6), 40, 98)),
        "coding_score": round(_clip(70 + 11 * ability + rng.gauss(0, 6), 40, 98)),
        "communication_score": round(_clip(68 + 9 * ability + rng.gauss(0, 7), 40, 98)),
        "technical_score": round(_clip(72 + 10 * ability + rng.gauss(0, 6), 40, 98)),
        "projects": int(_clip(round(2 + ability + rng.gauss(0, 1)), 0, 7)),
        "internships": int(_clip(round(.8 + .7 * ability + rng.gauss(0, .7)), 0, 3)),
        "certifications": int(_clip(round(1.5 + ability + rng.gauss(0, 1)), 0, 6)),
        "backlogs": 0 if ability > -0.3 else rng.choice([0, 1, 1, 2, 3]),
    }


CORE = ["Python", "SQL", "Java", "Git", "Data Structures", "Problem Solving", "Communication"]


def _skills(rng, ability):
    """Stronger students know more skills; everyone is likely to know the core ones."""
    skills = [s for s in CORE if rng.random() < _clip(0.62 + 0.18 * ability, 0.25, 0.97)]
    extras = [s for s in SKILL_POOL if s not in CORE]
    k = int(_clip(round(3 + 1.6 * ability + rng.gauss(0, 1.2)), 0, 9))
    return ", ".join(skills + rng.sample(extras, min(k, len(extras))))


DEMO_STUDENT = {"cgpa": 7.4, "attendance": 79, "aptitude_score": 68, "coding_score": 71,
                "communication_score": 64, "technical_score": 70, "projects": 3, "internships": 1,
                "certifications": 2, "backlogs": 0}
DEMO_SKILLS = ("Python, SQL, Java, Git, Data Structures, Problem Solving, Communication, "
               "HTML, CSS, JavaScript, Machine Learning")


def _insert_student(rng, name, email, password, ability, idx, created, override=None, skills=None):
    user_id = User.create(name, email, password, password_hash=_hash_once(password))
    execute("UPDATE users SET created_at = %s WHERE id = %s", (created, user_id))
    p = _profile(rng, ability)
    if override:
        p.update(override)
    skills = skills or _skills(rng, ability)
    execute(
        "INSERT INTO students (user_id, enrollment_no, phone, branch, year, cgpa, attendance, backlogs, "
        "aptitude_score, coding_score, communication_score, technical_score, projects, internships, "
        "certifications, skills, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (user_id, f"2022{idx:04d}", f"98{rng.randint(10000000, 99999999)}", rng.choice(BRANCHES[:5]),
         rng.choice(YEARS[2:]), p["cgpa"], p["attendance"], p["backlogs"], p["aptitude_score"],
         p["coding_score"], p["communication_score"], p["technical_score"], p["projects"],
         p["internships"], p["certifications"], skills, created))
    p["skills"] = skills
    return user_id, p


def _history(rng, user_id, p, ability):
    """Predictions, readiness, skill gap and interviews with a gentle upward trend."""
    runs = rng.randint(2, 4)
    for i in range(runs):
        weeks_ago = (runs - i) * rng.randint(2, 5)
        when = datetime.now() - timedelta(days=weeks_ago * 7 - rng.randint(0, 3), hours=rng.randint(0, 12))
        f = 1 - (runs - 1 - i) * 0.03  # earlier runs slightly weaker
        v = {k: (p[k] * f if k in ("aptitude_score", "coding_score", "communication_score", "technical_score")
                 else p[k]) for k in p}
        r = predict_placement(v["cgpa"], v["attendance"], v["aptitude_score"], v["coding_score"],
                              v["communication_score"], v["technical_score"], v["projects"],
                              v["internships"], v["certifications"])
        execute(
            "INSERT INTO prediction_history (user_id,cgpa,attendance,aptitude_score,coding_score,"
            "communication_score,technical_score,projects,internships,certifications,prediction,"
            "placement_probability,not_placed_probability,model_version,created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_id, v["cgpa"], v["attendance"], round(v["aptitude_score"]), round(v["coding_score"]),
             round(v["communication_score"]), round(v["technical_score"]), v["projects"], v["internships"],
             v["certifications"], r["result"], r["placement_probability"], r["not_placed_probability"],
             r["model_version"], when))
        rd = calculate_readiness_score(v["cgpa"], v["attendance"], v["aptitude_score"], v["coding_score"],
                                       v["communication_score"], v["technical_score"])
        execute(
            "INSERT INTO readiness_history (user_id,cgpa,attendance,aptitude_score,coding_score,"
            "communication_score,technical_score,readiness_score,readiness_level,created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_id, v["cgpa"], v["attendance"], round(v["aptitude_score"]), round(v["coding_score"]),
             round(v["communication_score"]), round(v["technical_score"]), rd["readiness_score"],
             rd["readiness_level"], when))
    gap = calculate_skill_gap(p["aptitude_score"], p["coding_score"], p["communication_score"], p["technical_score"])
    execute(
        "INSERT INTO skill_gap_history (user_id,cgpa,attendance,aptitude_score,coding_score,"
        "communication_score,technical_score,total_gap,overall_status,created_at) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (user_id, p["cgpa"], p["attendance"], p["aptitude_score"], p["coding_score"],
         p["communication_score"], p["technical_score"], gap["total_gap"], gap["overall_status"], _when(rng, 40)))
    questions = get_all_questions()
    for _ in range(rng.randint(1, 3)):
        category = rng.choice(["Technical", "HR", "Programming", "Behavioral"])
        pool = [q for q in questions if q["category"] == category][:5]
        score = round(_clip(62 + 9 * ability + rng.gauss(0, 8), 20, 98), 1)
        level = "Excellent" if score >= 80 else "Good" if score >= 65 else "Average" if score >= 50 else "Needs Improvement"
        results = [{"id": q["id"], "question": q["question"], "category": q["category"],
                    "difficulty": q["difficulty"], "answer": "",
                    "evaluation": {"score": round(_clip(score + rng.gauss(0, 8), 5, 100)), "status": level,
                                   "word_count": 0, "matched_keywords": q["keywords"][:2],
                                   "missing_keywords": q["keywords"][2:]}} for q in pool]
        details = {"results": results, "feedback": ["Practice regularly and review missing keywords."]}
        execute("INSERT INTO interview_history (user_id,category,total_questions,interview_score,"
                "performance_level,details,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (user_id, category, len(pool), score, level, json.dumps(details), _when(rng, 60)))


def seed_demo(force=False, seed=7):
    if not force and scalar("SELECT COUNT(*) FROM users") > 0:
        return False
    rng = random.Random(seed)

    for company in COMPANIES:
        if not Company.name_exists(company["name"]):
            Company.create({**company, "required_skills": ", ".join(company["required_skills"]), "is_active": 1})

    name, email, pw = DEMO_ACCOUNTS["admin"]
    User.create(name, email, pw, "admin")
    name, email, pw = DEMO_ACCOUNTS["tpo"]
    User.create(name, email, pw, "tpo")

    student_ids = []
    demo_name, demo_email, demo_pw = DEMO_ACCOUNTS["student"]
    uid, p = _insert_student(rng, demo_name, demo_email, demo_pw, 0.35, 1, _when(rng, 150),
                             override=DEMO_STUDENT, skills=DEMO_SKILLS)
    student_ids.append((uid, 0.35, p))
    for i, nm in enumerate(NAMES, start=2):
        ability = rng.gauss(0, 1)
        first, last = nm.lower().split()[0], nm.lower().split()[-1]
        uid, p = _insert_student(rng, nm, f"{first}.{last}@student.edu", "Student@123", ability, i, _when(rng, 160))
        student_ids.append((uid, ability, p))

    for uid, ability, p in student_ids:
        _history(rng, uid, p, ability)

    # Drives relative to today so the demo never looks stale.
    companies = {c["name"]: c["id"] for c in Company.all()}
    today = date.today()
    plan = [("TCS", "Graduate Engineer Trainee", 9, "Upcoming"), ("Infosys", "Systems Engineer", 16, "Upcoming"),
            ("Tech Solutions Pvt Ltd", "Python Developer", 5, "Active"),
            ("AI Solutions Pvt Ltd", "ML Engineer", 24, "Upcoming"),
            ("Accenture", "Associate Software Engineer", -30, "Completed"),
            ("Wipro", "Project Engineer", -52, "Completed"), ("Capgemini", "Analyst", -75, "Completed")]
    drive_ids = []
    for company, role, offset, status in plan:
        comp = Company.get(companies[company])
        drive_ids.append(Drive.create({
            "company_id": comp["id"], "job_role": role, "drive_date": today + timedelta(days=offset),
            "location": comp["location"], "openings": rng.choice([5, 8, 12, 20]),
            "package_lpa": comp["package_lpa"], "status": status,
            "description": f"{company} is recruiting final-year students for the {role} position."}))

    # Applications; completed drives produce real placements.
    all_companies = [Company.as_rule(c) for c in Company.all()]
    for drive_id, (company, role, offset, status) in zip(drive_ids, plan):
        comp = Company.get(companies[company])
        rule = Company.as_rule(comp)
        for uid, ability, p in student_ids:
            res = check_all_companies(p["cgpa"], p["attendance"], p["aptitude_score"], p["coding_score"],
                                      p["communication_score"], p["technical_score"], p["skills"], p["backlogs"], [rule])[0]
            if res["match_percent"] < 75 or rng.random() > 0.7:
                continue
            if status == "Completed":
                outcome = "Selected" if (ability > 0.1 and rng.random() < 0.55) else rng.choice(["Rejected", "Rejected", "Shortlisted"])
            else:
                outcome = rng.choice(["Applied", "Applied", "Shortlisted"])
            if Drive.application(drive_id, uid):
                continue
            app_id = Drive.apply(drive_id, uid)
            Drive.set_application_status(app_id, outcome)
            if outcome == "Selected" and not query_one(
                    "SELECT 1 AS x FROM students WHERE user_id=%s AND placement_status='Placed'", (uid,)):
                execute("UPDATE students SET placement_status='Placed', placed_company=%s, package_lpa=%s "
                        "WHERE user_id=%s", (company, comp["package_lpa"], uid))

    meta = get_metadata()
    m = meta["metrics"]
    execute("INSERT INTO model_versions (version, algorithm, accuracy, precision_score, recall_score, "
            "f1_score, roc_auc, train_rows, test_rows, features, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)",
            (meta["version"], meta["algorithm"], m["accuracy"], m["precision"], m["recall"], m["f1"],
             m["roc_auc"], meta["train_rows"], meta["test_rows"], ",".join(meta["features"])))
    execute("INSERT INTO datasets (filename, original_name, rows_count, placed_count, extra_features, use_for_training) "
            "VALUES (%s,%s,%s,%s,%s,1)", ("placement_dataset.csv", "Bundled demo dataset", meta["rows"],
                                           round(meta["rows"] * meta["placed_rate"] / 100),
                                           "projects,internships,certifications"))

    demo = student_ids[0][0]
    from models.notification import Notification
    Notification.create(demo, "Welcome to Student Placement Predictor",
                        "Complete your profile, then run a prediction to see where you stand.", "info", "/student/prediction")
    Notification.create(demo, "New placement drive: Tech Solutions Pvt Ltd",
                        "Python Developer drive is active now. Check your eligibility and apply.", "drive", "/student/drives")
    return True
