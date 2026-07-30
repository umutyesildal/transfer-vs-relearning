from __future__ import annotations

from datetime import datetime


def start_is_on_time(*, cutoff: datetime, now: datetime) -> bool:
    if cutoff.tzinfo is None or now.tzinfo is None:
        raise ValueError("Cutoff and current time must be timezone-aware")
    return now <= cutoff
