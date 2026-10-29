"""Phase-based learning path built from the skill gap."""

PHASES = [
    ("Foundation", "Fix the biggest gaps first", 0.45),
    ("Core practice", "Build speed and accuracy", 0.35),
    ("Interview ready", "Simulate real selection rounds", 0.20),
]
ACTIVITIES = {
    "Aptitude": ["Solve 20 timed quantitative questions daily", "Take a full aptitude mock every week"],
    "Coding": ["Solve 3 DSA problems daily", "Revise arrays, strings, hashing and recursion"],
    "Communication": ["Record a 2-minute self-introduction and review it", "Join a weekly group discussion"],
    "Technical": ["Revise DBMS, OS and networking notes", "Build and explain one end-to-end project"],
}


def build_learning_path(skill_analysis, hours_per_week=10):
    """Return phases with hours split across the weakest skill areas."""
    gaps = sorted(skill_analysis.items(), key=lambda kv: -kv[1].get("gap", 0))
    focus = [name for name, data in gaps if data.get("gap", 0) > 0] or [name for name, _ in gaps[:2]]
    path = []
    for index, (name, goal, share) in enumerate(PHASES):
        areas = focus[: max(2, 3 - index)] if focus else []
        path.append({
            "phase": name, "goal": goal, "weeks": [4, 4, 2][index],
            "hours_per_week": round(hours_per_week * (1.0 if index < 2 else 0.8)),
            "focus": areas,
            "activities": [a for area in areas for a in ACTIVITIES.get(area, [])][:4],
            "share": int(share * 100),
        })
    return path
