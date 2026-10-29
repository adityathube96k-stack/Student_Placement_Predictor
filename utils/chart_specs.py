"""Builders for chart specs consumed by static/js/charts.js (exposed to Jinja)."""

LEVEL_COLORS = {"Excellent": "var(--success)", "Good": "var(--chart-1)",
                "Moderate": "var(--chart-2)", "Needs Improvement": "var(--danger)"}
STATUS_COLORS = {"Placed": "var(--success)", "In Process": "var(--chart-2)", "Not Placed": "var(--chart-6)"}
STAGE_COLORS = {"Applied": "var(--chart-1)", "Shortlisted": "var(--chart-2)",
                "Selected": "var(--chart-3)", "Rejected": "var(--chart-5)"}


def hbar(rows, label_key, value_key, suffix="", max_value=None, colors=None, scale=1, round_to=1):
    items = []
    for row in rows:
        item = {"label": str(row[label_key]), "value": round(float(row[value_key]) * scale, round_to)}
        if colors and row[label_key] in colors:
            item["color"] = colors[row[label_key]]
        items.append(item)
    spec = {"type": "hbar", "items": items, "suffix": suffix}
    if max_value:
        spec["max"] = max_value
    return spec


def hbar_dict(data, suffix="", max_value=None):
    return hbar([{"k": k, "v": v} for k, v in data.items()], "k", "v", suffix, max_value)


def donut(data, colors, center_label="total"):
    items = [{"label": k, "value": v, "color": colors.get(k)} for k, v in data.items()]
    return {"type": "donut", "items": items, "center": {"label": center_label}}


def donut_levels(data):
    return donut(data, LEVEL_COLORS, "students")


def donut_status(data):
    return donut(data, STATUS_COLORS, "students")


def funnel(rows):
    return hbar(rows, "stage", "count", colors=STAGE_COLORS, round_to=0)


def importances(rows):
    return hbar(rows, "label", "importance", " pts", scale=100)


def register(env):
    env.globals.update(spec_hbar=hbar, spec_hbar_dict=hbar_dict, spec_donut_levels=donut_levels,
                       spec_donut_status=donut_status, spec_funnel=funnel, spec_importances=importances)
