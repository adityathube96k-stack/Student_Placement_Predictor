import os
import unittest

from tests import base  # noqa: F401
from company_eligibility.eligibility_checker import check_all_companies, check_eligibility
from interview_engine.answer_evaluator import evaluate_answer
from interview_engine.question_generator import (get_all_questions, get_question_by_id,
                                                 get_questions_by_category)
from recommendation_engine.career_roadmap import build_roadmap
from recommendation_engine.skill_gap import calculate_skill_gap
from resume_analyzer.parser import analyze_resume
from utils.readiness import calculate_readiness_score

COMPANY = {"name": "Acme", "min_cgpa": 7, "min_attendance": 75, "min_aptitude": 60, "min_coding": 60,
           "min_communication": 60, "min_technical": 60, "max_backlogs": 0,
           "required_skills": ["Python", "SQL"]}
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_resume.pdf")


class EligibilityTests(unittest.TestCase):
    def test_eligible_student(self):
        r = check_eligibility(COMPANY, 8, 85, 70, 70, 70, 70, "Python, sql", 0)
        self.assertTrue(r["eligible"])
        self.assertEqual(r["match_percent"], 100)

    def test_backlog_and_skill_failures_are_reported(self):
        r = check_eligibility(COMPANY, 8, 85, 70, 70, 70, 70, ["Python"], 2)
        self.assertFalse(r["eligible"])
        self.assertEqual(r["missing_skills"], ["SQL"])
        self.assertIn("Active backlogs", [m["requirement"] for m in r["missing_requirements"]])

    def test_low_score_gap(self):
        r = check_eligibility(COMPANY, 6.0, 85, 70, 70, 70, 70, "Python, SQL", 0)
        gap = next(m for m in r["missing_requirements"] if m["requirement"] == "CGPA")
        self.assertEqual(gap["gap"], 1.0)

    def test_check_all_sorts_eligible_first(self):
        results = check_all_companies(8, 85, 70, 70, 70, 70, "Python, SQL", 0, [COMPANY, dict(COMPANY, name="Hard", min_cgpa=9.5)])
        self.assertEqual(results[0]["company"], "Acme")


class InterviewTests(unittest.TestCase):
    def test_question_bank(self):
        self.assertGreaterEqual(len(get_all_questions()), 30)
        self.assertGreaterEqual(len(get_questions_by_category("Aptitude")), 3)
        self.assertEqual(len({q["id"] for q in get_all_questions()}), len(get_all_questions()))
        self.assertIsNotNone(get_question_by_id(1))

    def test_evaluator(self):
        good = evaluate_answer("A stack is LIFO while a queue is FIFO, so a stack pops the newest item first", ["stack", "queue", "lifo", "fifo"])
        self.assertGreaterEqual(good["score"], 80)
        self.assertEqual(evaluate_answer("", ["stack"])["score"], 0)
        short = evaluate_answer("stack queue", ["stack", "queue"])
        self.assertLessEqual(short["score"], 60)


class ScoringTests(unittest.TestCase):
    def test_readiness_levels(self):
        self.assertEqual(calculate_readiness_score(9, 95, 90, 90, 90, 90)["readiness_level"], "Excellent")
        self.assertEqual(calculate_readiness_score(4, 50, 40, 40, 40, 40)["readiness_level"], "Needs Improvement")

    def test_skill_gap_and_roadmap(self):
        gap = calculate_skill_gap(60, 90, 50, 80)
        self.assertEqual(gap["priority_skills"][0], "Communication")
        plan = build_roadmap(gap, "Python, SQL")
        self.assertEqual(len(plan["months"]), 6)
        self.assertTrue(plan["target_roles"])

    def test_resume_analysis(self):
        result = analyze_resume(FIXTURE)
        self.assertGreaterEqual(result["score"]["overall_score"], 60)
        self.assertTrue(result["score"]["sections"]["Contact Information"])
        self.assertIn("Programming Languages", result["skills"])


if __name__ == "__main__":
    unittest.main()
