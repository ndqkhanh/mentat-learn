"""Cron-style scheduler for skill-triggered automations.

Uses a minimal 5-field cron subset: "MIN HOUR DOM MON DOW". '*' is the only
wildcard. Evaluations happen on tick(now); production wires a real scheduler.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _match_field(value: int, expr: str) -> bool:
    if expr == "*":
        return True
    if "," in expr:
        return any(_match_field(value, part) for part in expr.split(","))
    if "-" in expr:
        lo, hi = expr.split("-", 1)
        try:
            return int(lo) <= value <= int(hi)
        except ValueError:
            return False
    if "/" in expr:
        _, step = expr.split("/", 1)
        try:
            return value % int(step) == 0
        except ValueError:
            return False
    try:
        return value == int(expr)
    except ValueError:
        return False


def cron_matches(expr: str, now_utc: datetime) -> bool:
    parts = expr.split()
    if len(parts) != 5:
        raise ValueError(f"cron expression must have 5 fields, got {len(parts)}: {expr!r}")
    m, h, dom, mon, dow = parts
    return (
        _match_field(now_utc.minute, m)
        and _match_field(now_utc.hour, h)
        and _match_field(now_utc.day, dom)
        and _match_field(now_utc.month, mon)
        and _match_field(now_utc.weekday(), dow)
    )


@dataclass
class Schedule:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    cron_expr: str = "* * * * *"
    user_id: str = ""
    skill_id: Optional[str] = None
    channel: str = ""
    inputs: dict = field(default_factory=dict)
    enabled: bool = True
    last_run_at: float = 0.0
    last_result: Optional[str] = None


class CronScheduler:
    """In-memory scheduler. ``tick(now=..)`` returns ready schedules."""

    def __init__(self) -> None:
        self._items: dict[str, Schedule] = {}

    def add(self, schedule: Schedule) -> Schedule:
        self._items[schedule.id] = schedule
        return schedule

    def remove(self, schedule_id: str) -> bool:
        return self._items.pop(schedule_id, None) is not None

    def all(self) -> list[Schedule]:
        return list(self._items.values())

    def active(self) -> list[Schedule]:
        return [s for s in self._items.values() if s.enabled]

    def tick(self, now: Optional[datetime] = None) -> list[Schedule]:
        """Return schedules whose cron matches `now`; debounce within the same minute."""
        if now is None:
            now = datetime.now(tz=timezone.utc)
        ready: list[Schedule] = []
        # Use this-minute epoch for debouncing
        now_ts = now.replace(second=0, microsecond=0).timestamp()
        for s in self._items.values():
            if not s.enabled:
                continue
            if cron_matches(s.cron_expr, now):
                if s.last_run_at >= now_ts:
                    continue
                s.last_run_at = now_ts
                ready.append(s)
        return ready

    def mark_result(self, schedule_id: str, result: str) -> None:
        s = self._items.get(schedule_id)
        if s is not None:
            s.last_result = result
