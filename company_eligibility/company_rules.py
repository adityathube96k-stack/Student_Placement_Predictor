# =====================================================
# COMPANY ELIGIBILITY RULES
# =====================================================

COMPANIES = [

    {
        "id": 1,
        "name": "Tech Solutions Pvt Ltd",
        "min_cgpa": 7.0,
        "min_attendance": 75,
        "min_aptitude": 60,
        "min_coding": 65,
        "min_communication": 60,
        "min_technical": 65,
        "required_skills": [
            "Python",
            "SQL",
            "Data Structures"
        ]
    },

    {
        "id": 2,
        "name": "Software Technologies Ltd",
        "min_cgpa": 7.5,
        "min_attendance": 75,
        "min_aptitude": 65,
        "min_coding": 70,
        "min_communication": 65,
        "min_technical": 70,
        "required_skills": [
            "Java",
            "SQL",
            "Data Structures",
            "Algorithms"
        ]
    },

    {
        "id": 3,
        "name": "AI Solutions Pvt Ltd",
        "min_cgpa": 8.0,
        "min_attendance": 80,
        "min_aptitude": 70,
        "min_coding": 70,
        "min_communication": 65,
        "min_technical": 75,
        "required_skills": [
            "Python",
            "Machine Learning",
            "Data Science",
            "SQL"
        ]
    },

    {
        "id": 4,
        "name": "Cloud Systems India",
        "min_cgpa": 7.0,
        "min_attendance": 75,
        "min_aptitude": 60,
        "min_coding": 65,
        "min_communication": 60,
        "min_technical": 70,
        "required_skills": [
            "Python",
            "AWS",
            "Docker",
            "Git"
        ]
    },

    {
        "id": 5,
        "name": "Web Development Solutions",
        "min_cgpa": 6.5,
        "min_attendance": 70,
        "min_aptitude": 55,
        "min_coding": 60,
        "min_communication": 60,
        "min_technical": 60,
        "required_skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "React"
        ]
    }

]


# =====================================================
# GET ALL COMPANIES
# =====================================================

def get_all_companies():

    return COMPANIES


# =====================================================
# GET COMPANY BY ID
# =====================================================

def get_company_by_id(company_id):

    for company in COMPANIES:

        if company["id"] == company_id:

            return company

    return None


# =====================================================
# GET COMPANY BY NAME
# =====================================================

def get_company_by_name(company_name):

    for company in COMPANIES:

        if company["name"].lower() == company_name.lower():

            return company

    return None


# =====================================================
# DISPLAY COMPANY RULES
# =====================================================

def display_company_rules():

    for company in COMPANIES:

        print("\n==========================================")
        print(company["name"])
        print("==========================================")

        print(
            "Minimum CGPA       :",
            company["min_cgpa"]
        )

        print(
            "Minimum Attendance :",
            company["min_attendance"]
        )

        print(
            "Minimum Aptitude   :",
            company["min_aptitude"]
        )

        print(
            "Minimum Coding     :",
            company["min_coding"]
        )

        print(
            "Minimum Communication:",
            company["min_communication"]
        )

        print(
            "Minimum Technical  :",
            company["min_technical"]
        )

        print(
            "Required Skills    :",
            ", ".join(company["required_skills"])
        )


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    print("==========================================")
    print("COMPANY ELIGIBILITY RULES")
    print("==========================================")

    print(
        "Total Companies:",
        len(COMPANIES)
    )

    display_company_rules()

    print("\n==========================================")