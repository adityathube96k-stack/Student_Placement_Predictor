import unittest

from tests import base  # noqa: F401  (sets env before app imports)
from ml.feature_engineering import clean_dataframe, validate_inputs
from ml.model_loader import get_metadata, load_model
from ml.predict import predict_placement


class MLTests(unittest.TestCase):
    def test_model_loads_with_metadata(self):
        pipeline, meta = load_model()
        self.assertIsNotNone(pipeline)
        for key in ("version", "algorithm", "features", "metrics", "comparison", "importances"):
            self.assertIn(key, meta)
        self.assertGreater(meta["metrics"]["accuracy"], 70)

    def test_strong_profile_beats_weak_profile(self):
        strong = predict_placement(9.0, 92, 88, 90, 85, 90, 4, 2, 4)
        weak = predict_placement(5.2, 58, 45, 48, 50, 47, 0, 0, 0)
        self.assertGreater(strong["placement_probability"], 90)
        self.assertLess(weak["placement_probability"], 10)
        self.assertEqual(strong["result"], "Placed")
        self.assertEqual(weak["result"], "Not Placed")

    def test_result_shape_and_probabilities(self):
        r = predict_placement(7.0, 76, 67, 70, 68, 72, 2, 1, 2)
        self.assertAlmostEqual(r["placement_probability"] + r["not_placed_probability"], 100, places=1)
        self.assertIn(r["band"], {"High", "Moderate", "Low"})
        self.assertTrue(r["factors"])
        self.assertTrue(all({"label", "impact"} <= set(f) for f in r["factors"]))

    def test_experience_is_optional(self):
        r = predict_placement(7.5, 80, 70, 72, 70, 74)
        self.assertGreaterEqual(r["placement_probability"], 0)

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            validate_inputs({"cgpa": 11, "attendance": 80, "aptitude_score": 70, "coding_score": 70,
                             "communication_score": 70, "technical_score": 70})
        with self.assertRaises(ValueError):
            validate_inputs({"cgpa": "abc"})
        with self.assertRaises(ValueError):
            predict_placement(None, 80, 70, 70, 70, 70)

    def test_clean_dataframe_rejects_missing_columns_and_bad_rows(self):
        import pandas as pd
        with self.assertRaises(ValueError):
            clean_dataframe(pd.DataFrame({"cgpa": [7]}))
        frame = pd.DataFrame({"cgpa": [7, 7, 99], "attendance": [80, 80, 80], "aptitude_score": [70] * 3,
                              "coding_score": [70] * 3, "communication_score": [70] * 3,
                              "technical_score": [70] * 3, "placed": [1, 1, 2]})
        cleaned = clean_dataframe(frame)
        self.assertEqual(len(cleaned), 1)  # duplicate dropped, invalid label dropped


if __name__ == "__main__":
    unittest.main()
