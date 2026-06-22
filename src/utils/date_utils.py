"""Date utilities for Beijing timezone operations."""
from datetime import datetime, date
from zoneinfo import ZoneInfo

BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def now_beijing() -> datetime:
    return datetime.now(BEIJING_TZ)


def today_beijing() -> date:
    return now_beijing().date()


def week_label(dt: date | None = None) -> str:
    """Return ISO week label like 2025-W26."""
    d = dt or today_beijing()
    return f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"


def month_label(dt: date | None = None) -> str:
    d = dt or today_beijing()
    return d.strftime("%Y-%m")
