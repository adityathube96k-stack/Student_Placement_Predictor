import os

from resume_analyzer.extract_text import extract_text_from_pdf
from resume_analyzer.skill_extractor import extract_skills
from resume_analyzer.resume_score import calculate_resume_score
from resume_analyzer.recommendation import (
    generate_resume_recommendations
)


def analyze_resume(pdf_path):
    """
    Complete resume analysis pipeline.

    Pipeline:
        PDF
         ↓
        Text Extraction
         ↓
        Skill Extraction
         ↓
        Resume Score
         ↓
        Recommendations

    Args:
        pdf_path (str): Path to the PDF resume.

    Returns:
        dict: Complete resume analysis result.
    """

    if not pdf_path:
        raise ValueError(
            "Resume PDF path is required."
        )

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"Resume file not found: {pdf_path}"
        )

    # -------------------------------------------------
    # Step 1: Extract text from PDF
    # -------------------------------------------------

    resume_text = extract_text_from_pdf(
        pdf_path
    )

    # -------------------------------------------------
    # Step 2: Extract skills
    # -------------------------------------------------

    extracted_skills = extract_skills(
        resume_text
    )

    # -------------------------------------------------
    # Step 3: Calculate resume score
    # -------------------------------------------------

    score_result = calculate_resume_score(
        resume_text=resume_text,
        extracted_skills=extracted_skills
    )

    # -------------------------------------------------
    # Step 4: Generate recommendations
    # -------------------------------------------------

    recommendations = generate_resume_recommendations(
        resume_score_result=score_result,
        extracted_skills=extracted_skills
    )

    # -------------------------------------------------
    # Step 5: Prepare final result
    # -------------------------------------------------

    return {
        "resume_text": resume_text,
        "skills": extracted_skills,
        "score": score_result,
        "recommendations": recommendations
    }


def print_analysis(result):
    """
    Display resume analysis in a readable format.
    """

    print("\n==========================================")
    print("RESUME ANALYSIS RESULT")
    print("==========================================")

    # -------------------------------------------------
    # Resume Score
    # -------------------------------------------------

    score = result["score"]

    print("\nRESUME SCORE")
    print("------------------------------------------")

    print(
        f"Overall Score : "
        f"{score['overall_score']}%"
    )

    print(
        f"Rating        : "
        f"{score['rating']}"
    )

    print(
        f"Section Score : "
        f"{score['section_score']}%"
    )

    print(
        f"Skill Score   : "
        f"{score['skill_score']}%"
    )

    print(
        f"Length Score  : "
        f"{score['length_score']}%"
    )

    # -------------------------------------------------
    # Skills
    # -------------------------------------------------

    print("\nEXTRACTED SKILLS")
    print("------------------------------------------")

    if result["skills"]:

        for category, skills in result["skills"].items():

            print(f"\n{category}:")

            for skill in skills:
                print(f"  - {skill}")

    else:

        print("No technical skills detected.")

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------

    print("\nRECOMMENDATIONS")
    print("------------------------------------------")

    if result["recommendations"]:

        for index, recommendation in enumerate(
            result["recommendations"],
            start=1
        ):

            print(
                f"\n{index}. "
                f"{recommendation['title']}"
            )

            print(
                f"   Category : "
                f"{recommendation['category']}"
            )

            print(
                f"   Priority : "
                f"{recommendation['priority']}"
            )

            print(
                f"   Suggestion: "
                f"{recommendation['description']}"
            )

    else:

        print(
            "No additional recommendations."
        )

    print("\n==========================================")


if __name__ == "__main__":

    print("==========================================")
    print("RESUME ANALYZER")
    print("==========================================")

    print(
        "This module requires a PDF resume."
    )

    print(
        "Use analyze_resume(pdf_path) "
        "to analyze a resume."
    )

    print("==========================================")