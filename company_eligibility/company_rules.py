"""Seed company rules.

These are DEMO criteria used to pre-fill the ``companies`` table. In a running
system, companies are managed by admins (Admin > Companies) and read from the
database; ``get_all_companies`` falls back to this list only if the database is
unavailable.
"""


def _c(id_, name, industry, location, lpa, cgpa, att, apt, cod, com, tec, backlogs, skills, about):
    return {
        "id": id_, "name": name, "industry": industry, "location": location,
        "package_lpa": lpa, "min_cgpa": cgpa, "min_attendance": att, "min_aptitude": apt,
        "min_coding": cod, "min_communication": com, "min_technical": tec,
        "max_backlogs": backlogs, "required_skills": skills, "description": about,
    }


COMPANIES = [
    _c(1, "Tech Solutions Pvt Ltd", "Software Services", "Pune", 6.5, 7.0, 75, 60, 65, 60, 65, 0,
       ["Python", "SQL", "Data Structures"], "Custom software and automation for mid-size enterprises."),
    _c(2, "Software Technologies Ltd", "Software Products", "Bengaluru", 8.0, 7.5, 75, 65, 70, 65, 70, 0,
       ["Java", "SQL", "Data Structures", "Algorithms"], "Product engineering for banking platforms."),
    _c(3, "AI Solutions Pvt Ltd", "Artificial Intelligence", "Hyderabad", 10.0, 8.0, 80, 70, 70, 65, 75, 0,
       ["Python", "Machine Learning", "Data Science", "SQL"], "Applied machine learning and analytics."),
    _c(4, "Cloud Systems India", "Cloud & DevOps", "Pune", 7.5, 7.0, 75, 60, 65, 60, 70, 1,
       ["Python", "AWS", "Docker", "Git"], "Managed cloud infrastructure and DevOps consulting."),
    _c(5, "Web Development Solutions", "Web & Digital", "Nashik", 5.0, 6.5, 70, 55, 60, 60, 60, 2,
       ["HTML", "CSS", "JavaScript", "React"], "Websites and web apps for retail and education."),
    _c(6, "TCS", "IT Services", "Pune", 3.6, 6.5, 70, 55, 55, 60, 55, 0,
       ["Python", "SQL", "Problem Solving", "Communication"], "Demo criteria. Graduate engineer trainee role."),
    _c(7, "Infosys", "IT Services", "Pune", 3.6, 6.0, 70, 55, 55, 60, 55, 1,
       ["Java", "Python", "SQL", "Communication"], "Demo criteria. Systems engineer role."),
    _c(8, "Wipro", "IT Services", "Mumbai", 3.5, 6.0, 70, 55, 55, 55, 55, 1,
       ["Python", "Java", "SQL", "Problem Solving"], "Demo criteria. Project engineer role."),
    _c(9, "Accenture", "Consulting", "Pune", 4.5, 6.5, 70, 60, 60, 65, 60, 0,
       ["Python", "SQL", "JavaScript", "Communication"], "Demo criteria. Associate software engineer role."),
    _c(10, "Capgemini", "IT Services", "Pune", 4.0, 6.0, 70, 55, 55, 60, 55, 1,
       ["Python", "SQL", "Problem Solving", "Linux"], "Demo criteria. Software engineer role."),
]


def get_all_companies():
    from company_eligibility.company_data import load_companies
    return load_companies()


def get_company_by_id(company_id):
    return next((c for c in get_all_companies() if c["id"] == company_id), None)


def get_company_by_name(name):
    return next((c for c in get_all_companies() if c["name"].lower() == name.lower()), None)
