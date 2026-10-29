"""Industry certification suggestions."""
from utils.helpers import split_skills

_X = lambda name, issuer, level, weeks, url, tags, why: {  # noqa: E731
    "name": name, "issuer": issuer, "level": level, "weeks": weeks, "url": url,
    "tags": tags, "why": why}

CERTIFICATIONS = [
    _X("AWS Certified Cloud Practitioner", "Amazon Web Services", "Beginner", 4,
       "https://aws.amazon.com/certification/", ["aws", "docker", "linux"],
       "Recognised cloud entry credential; relevant for infrastructure and DevOps roles."),
    _X("Microsoft Azure Fundamentals (AZ-900)", "Microsoft", "Beginner", 3,
       "https://learn.microsoft.com/credentials/", ["aws", "docker"],
       "Shows you understand cloud concepts used by most IT services employers."),
    _X("Google Data Analytics Certificate", "Google / Coursera", "Beginner", 12,
       "https://www.coursera.org", ["sql", "data science", "python"],
       "Hands-on analytics portfolio with SQL, spreadsheets and visualisation."),
    _X("Python Institute PCEP / PCAP", "Python Institute", "Beginner", 6,
       "https://pythoninstitute.org", ["python"],
       "Independent proof of Python fundamentals."),
    _X("Oracle Certified Associate, Java SE", "Oracle", "Intermediate", 8,
       "https://education.oracle.com", ["java", "algorithms"],
       "Valued by Java-focused service companies."),
    _X("Meta Front-End Developer Certificate", "Meta / Coursera", "Beginner", 16,
       "https://www.coursera.org", ["html", "css", "javascript", "react"],
       "Covers modern front-end skills with project work."),
    _X("TensorFlow / Machine Learning Specialisation", "DeepLearning.AI", "Intermediate", 12,
       "https://www.deeplearning.ai", ["machine learning", "data science", "python"],
       "Core credential for AI and data science roles."),
    _X("HackerRank Skills Certification (SQL, Problem Solving)", "HackerRank", "Beginner", 2,
       "https://www.hackerrank.com/skills-verification", ["sql", "problem solving", "algorithms"],
       "Quick, free skill badges recruiters often check."),
    _X("Docker Certified Associate prep", "Docker / KodeKloud", "Intermediate", 6,
       "https://roadmap.sh", ["docker", "linux", "git"],
       "Demonstrates containerisation skills for DevOps roles."),
    _X("NPTEL certification (Elite/Gold)", "NPTEL (IITs)", "Beginner", 12,
       "https://nptel.ac.in", ["data structures", "algorithms", "python", "java"],
       "Respected by campus recruiters; free to learn, proctored exam for the certificate."),
]


def recommend_certifications(student_skills=None, missing_skills=None, limit=6):
    have = {s.lower() for s in (split_skills(student_skills) if isinstance(student_skills, str)
                                else (student_skills or []))}
    want = {str(s).lower() for s in (missing_skills or [])}
    scored = []
    for cert in CERTIFICATIONS:
        tags = set(cert["tags"])
        score = 3 * len(tags & want) + len(tags - have) * 0.5 + (1 if cert["level"] == "Beginner" else 0)
        reasons = sorted(tags & want)
        scored.append((score, dict(cert, matched=reasons)))
    scored.sort(key=lambda item: -item[0])
    return [c for _, c in scored[:limit]]
