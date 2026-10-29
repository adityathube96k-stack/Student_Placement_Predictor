"""Generate the bundled DEMO placement dataset (synthetic, seeded).

Keeps the 93 original rows and adds ~1,100 synthetic rows with realistic noise so a
trained model reaches a believable accuracy instead of a perfect score.
Replace it with your institute's real data via Admin > Upload Dataset.
"""
import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUMNS = ["cgpa", "attendance", "aptitude_score", "coding_score", "communication_score",
           "technical_score", "projects", "internships", "certifications", "placed"]


def clip(a, lo, hi):
    return np.clip(a, lo, hi)


def experience(rng, ability):
    projects = clip(np.round(2.2 + 1.1 * ability + rng.normal(0, 1.1, len(ability))), 0, 8)
    internships = clip(np.round(0.8 + 0.7 * ability + rng.normal(0, 0.8, len(ability))), 0, 4)
    certs = clip(np.round(1.5 + 0.9 * ability + rng.normal(0, 1.2, len(ability))), 0, 8)
    return projects.astype(int), internships.astype(int), certs.astype(int)


def placed_label(rng, f):
    z = (-12.6 + 0.55 * f["cgpa"] + 0.018 * f["attendance"] + 0.020 * f["aptitude_score"]
         + 0.030 * f["coding_score"] + 0.022 * f["communication_score"]
         + 0.026 * f["technical_score"] + 0.16 * f["projects"]
         + 0.55 * f["internships"] + 0.10 * f["certifications"]
         + rng.normal(0, 0.9, len(f["cgpa"])))
    return (1 / (1 + np.exp(-z)) > 0.5).astype(int)


def main(n=1100, seed=42):
    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, n)
    f = {
        "cgpa": clip(np.round(7.0 + 0.95 * ability + rng.normal(0, 0.55, n), 1), 4.5, 9.9),
        "attendance": clip(np.round(76 + 8 * ability + rng.normal(0, 6, n)), 50, 100),
        "aptitude_score": clip(np.round(67 + 10 * ability + rng.normal(0, 7, n)), 35, 100),
        "coding_score": clip(np.round(70 + 11 * ability + rng.normal(0, 7, n)), 35, 100),
        "communication_score": clip(np.round(68 + 9 * ability + rng.normal(0, 8, n)), 35, 100),
        "technical_score": clip(np.round(72 + 10 * ability + rng.normal(0, 7, n)), 35, 100),
    }
    f["projects"], f["internships"], f["certifications"] = experience(rng, ability)
    f["placed"] = placed_label(rng, f)
    synthetic = pd.DataFrame(f)[COLUMNS]

    orig = pd.read_csv(os.path.join(BASE, "dataset", "placement_dataset_original.csv"))
    skill = orig[["aptitude_score", "coding_score", "communication_score", "technical_score"]].mean(axis=1)
    o_ability = ((skill - 70) / 11 + (orig["cgpa"] - 7) / 0.95) / 2
    p, i, c = experience(rng, o_ability.to_numpy())
    orig = orig.assign(projects=p, internships=i, certifications=c)[COLUMNS]

    out = pd.concat([orig, synthetic], ignore_index=True).sample(frac=1, random_state=seed)
    out.to_csv(os.path.join(BASE, "dataset", "placement_dataset.csv"), index=False)
    print(f"rows={len(out)} placed_rate={out.placed.mean():.2f}")


if __name__ == "__main__":
    main()
