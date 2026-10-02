from company_eligibility.company_rules import get_all_companies


# ==========================================================
# NORMALIZE NUMBER
# ==========================================================

def to_float(value):
    """
    Convert Decimal, integer, string or float
    into a normal Python float.
    """

    if value is None:
        return 0.0

    return float(value)


# ==========================================================
# NORMALIZE SKILLS
# ==========================================================

def normalize_skills(skills):
    """
    Convert student skills into a clean lowercase set.
    """

    if not skills:
        return set()

    if isinstance(skills, str):

        skill_list = skills.split(",")

    elif isinstance(skills, (list, tuple, set)):

        skill_list = skills

    else:

        return set()

    return {
        str(skill).strip().lower()
        for skill in skill_list
        if skill and str(skill).strip()
    }


# ==========================================================
# CHECK SINGLE COMPANY
# ==========================================================

def check_eligibility(
    company,
    cgpa,
    attendance,
    aptitude_score,
    coding_score,
    communication_score,
    technical_score,
    student_skills=None
):

    # ------------------------------------------------------
    # CONVERT STUDENT VALUES TO FLOAT
    # ------------------------------------------------------

    cgpa = to_float(cgpa)

    attendance = to_float(attendance)

    aptitude_score = to_float(
        aptitude_score
    )

    coding_score = to_float(
        coding_score
    )

    communication_score = to_float(
        communication_score
    )

    technical_score = to_float(
        technical_score
    )


    # ------------------------------------------------------
    # SCORE REQUIREMENTS
    # ------------------------------------------------------

    score_checks = [

        (
            "CGPA",
            cgpa,
            to_float(company["min_cgpa"])
        ),

        (
            "Attendance",
            attendance,
            to_float(company["min_attendance"])
        ),

        (
            "Aptitude Score",
            aptitude_score,
            to_float(company["min_aptitude"])
        ),

        (
            "Coding Score",
            coding_score,
            to_float(company["min_coding"])
        ),

        (
            "Communication Score",
            communication_score,
            to_float(company["min_communication"])
        ),

        (
            "Technical Score",
            technical_score,
            to_float(company["min_technical"])
        )

    ]


    missing_requirements = []


    for requirement, student_score, required_score in score_checks:

        if student_score < required_score:

            missing_requirements.append({

                "requirement": requirement,

                "student_score": round(
                    student_score,
                    2
                ),

                "required_score": round(
                    required_score,
                    2
                ),

                "gap": round(
                    required_score - student_score,
                    2
                )

            })


    # ------------------------------------------------------
    # SKILL REQUIREMENTS
    # ------------------------------------------------------

    required_skills = company.get(
        "required_skills",
        []
    )


    student_skill_set = normalize_skills(
        student_skills
    )


    missing_skills = []


    for required_skill in required_skills:

        if (
            str(required_skill).strip().lower()
            not in student_skill_set
        ):

            missing_skills.append(
                required_skill
            )


    # ------------------------------------------------------
    # FINAL ELIGIBILITY
    # ------------------------------------------------------

    eligible = (

        len(missing_requirements) == 0

        and

        len(missing_skills) == 0

    )


    # ------------------------------------------------------
    # RESULT
    # ------------------------------------------------------

    return {

        "company": company["name"],

        "eligible": eligible,

        "missing_requirements":
            missing_requirements,

        "required_skills":
            required_skills,

        "missing_skills":
            missing_skills

    }


# ==========================================================
# CHECK ALL COMPANIES
# ==========================================================

def check_all_companies(
    cgpa,
    attendance,
    aptitude_score,
    coding_score,
    communication_score,
    technical_score,
    student_skills=None
):

    companies = get_all_companies()

    results = []


    for company in companies:

        result = check_eligibility(

            company=company,

            cgpa=cgpa,

            attendance=attendance,

            aptitude_score=aptitude_score,

            coding_score=coding_score,

            communication_score=communication_score,

            technical_score=technical_score,

            student_skills=student_skills

        )


        # --------------------------------------------------
        # ADD REQUIREMENTS FOR TEMPLATE
        # --------------------------------------------------

        result["requirements"] = {

            "cgpa":
                to_float(
                    company["min_cgpa"]
                ),

            "attendance":
                to_float(
                    company["min_attendance"]
                ),

            "aptitude_score":
                to_float(
                    company["min_aptitude"]
                ),

            "coding_score":
                to_float(
                    company["min_coding"]
                ),

            "communication_score":
                to_float(
                    company["min_communication"]
                ),

            "technical_score":
                to_float(
                    company["min_technical"]
                )

        }


        results.append(result)


    return results


# ==========================================================
# GET ELIGIBLE COMPANIES
# ==========================================================

def get_eligible_companies(results):

    return [

        result

        for result in results

        if result["eligible"]

    ]


# ==========================================================
# GET NON-ELIGIBLE COMPANIES
# ==========================================================

def get_non_eligible_companies(results):

    return [

        result

        for result in results

        if not result["eligible"]

    ]


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

def display_results(results):

    print()

    print("=" * 50)

    print(
        "COMPANY ELIGIBILITY RESULTS"
    )

    print("=" * 50)


    for result in results:

        print()

        print(
            "Company :",
            result["company"]
        )


        if result["eligible"]:

            print(
                "Status  : Eligible"
            )

            print(
                "✓ Student satisfies "
                "all score and skill requirements."
            )


        else:

            print(
                "Status  : Not Eligible"
            )


            # ----------------------------------------------
            # MISSING SCORE REQUIREMENTS
            # ----------------------------------------------

            if result[
                "missing_requirements"
            ]:

                print(
                    "Missing Requirements:"
                )


                for item in result[
                    "missing_requirements"
                ]:

                    print(

                        f"  - {item['requirement']}: "

                        f"{item['student_score']} "

                        f"(Required: "
                        f"{item['required_score']}, "

                        f"Gap: "
                        f"{item['gap']})"

                    )


            # ----------------------------------------------
            # MISSING SKILLS
            # ----------------------------------------------

            if result[
                "missing_skills"
            ]:

                print(
                    "Missing Skills:"
                )


                for skill in result[
                    "missing_skills"
                ]:

                    print(
                        f"  - {skill}"
                    )


    eligible_count = len(
        get_eligible_companies(results)
    )


    not_eligible_count = len(
        get_non_eligible_companies(results)
    )


    print()

    print("=" * 50)

    print(
        f"Eligible Companies: "
        f"{eligible_count}"
    )

    print(
        f"Not Eligible Companies: "
        f"{not_eligible_count}"
    )

    print("=" * 50)


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    student_skills = (
        "Python, SQL, Data Structures, "
        "Git, HTML, CSS, JavaScript"
    )


    results = check_all_companies(

        cgpa=7.8,

        attendance=89.61,

        aptitude_score=75.48,

        coding_score=67.55,

        communication_score=65.70,

        technical_score=70.43,

        student_skills=student_skills

    )


    display_results(results)