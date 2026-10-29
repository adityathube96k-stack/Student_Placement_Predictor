"""Small, dependency-free helpers used across routes and templates."""
import json
from datetime import date, datetime
from urllib.parse import urlparse


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def split_skills(text):
    """'Python, sql ,Python' -> ['Python', 'sql'] (order kept, case-insensitive de-dupe)."""
    if not text:
        return []
    seen, out = set(), []
    for part in str(text).split(","):
        name = part.strip()
        if name and name.lower() not in seen:
            seen.add(name.lower())
            out.append(name)
    return out


def parse_json(text, default=None):
    if not text:
        return default if default is not None else []
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return default if default is not None else []


def initials(name):
    parts = [p for p in (name or "").split() if p]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def time_ago(value):
    if not isinstance(value, datetime):
        return ""
    seconds = int((datetime.now() - value).total_seconds())
    if seconds < 0:
        seconds = 0
    for limit, unit in ((60, "second"), (3600, "minute"), (86400, "hour"), (86400 * 30, "day")):
        if seconds < limit:
            divisor = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}[unit]
            count = max(seconds // divisor, 0)
            if unit == "second":
                return "just now"
            return f"{count} {unit}{'s' if count != 1 else ''} ago"
    return value.strftime("%d %b %Y")


def format_date(value, pattern="%d %b %Y"):
    if isinstance(value, (datetime, date)):
        return value.strftime(pattern)
    return value or "-"


def paginate(items, page, per_page=10):
    total = len(items)
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(max(page, 1), pages)
    start = (page - 1) * per_page
    return {"items": items[start:start + per_page], "page": page, "pages": pages,
            "total": total, "per_page": per_page}


def safe_redirect_target(target, fallback):
    """Only allow same-site relative redirects."""
    if target and target.startswith("/") and not target.startswith("//"):
        if not urlparse(target).netloc:
            return target
    return fallback


def percent(part, whole, digits=1):
    return round(part * 100.0 / whole, digits) if whole else 0.0
