from datetime import datetime, timezone

import pytest
from mentat_learn.cron import CronScheduler, Schedule, cron_matches


def test_wildcard_matches_everything():
    assert cron_matches("* * * * *", datetime(2026, 4, 20, 12, 30, tzinfo=timezone.utc))


def test_fixed_minute():
    assert cron_matches("30 * * * *", datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc))
    assert not cron_matches("30 * * * *", datetime(2026, 1, 1, 0, 29, tzinfo=timezone.utc))


def test_range_hour():
    assert cron_matches("0 9-17 * * *", datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))
    assert not cron_matches("0 9-17 * * *", datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc))


def test_step_minute():
    # every 5 minutes
    assert cron_matches("*/5 * * * *", datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc))
    assert cron_matches("*/5 * * * *", datetime(2026, 1, 1, 0, 15, tzinfo=timezone.utc))
    assert not cron_matches("*/5 * * * *", datetime(2026, 1, 1, 0, 2, tzinfo=timezone.utc))


def test_list_values():
    assert cron_matches("0 9,17 * * *", datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc))
    assert cron_matches("0 9,17 * * *", datetime(2026, 1, 1, 17, 0, tzinfo=timezone.utc))
    assert not cron_matches("0 9,17 * * *", datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc))


def test_invalid_expression_raises():
    with pytest.raises(ValueError, match="5 fields"):
        cron_matches("* * * *", datetime.now(timezone.utc))


def test_scheduler_tick_returns_matching_schedules():
    sched = CronScheduler()
    s1 = sched.add(Schedule(cron_expr="0 9 * * *", name="morning"))
    sched.add(Schedule(cron_expr="0 17 * * *", name="evening"))
    now = datetime(2026, 4, 20, 9, 0, tzinfo=timezone.utc)
    ready = sched.tick(now=now)
    assert [s.id for s in ready] == [s1.id]


def test_scheduler_debounces_same_minute():
    sched = CronScheduler()
    sched.add(Schedule(cron_expr="* * * * *"))
    now = datetime(2026, 4, 20, 9, 0, tzinfo=timezone.utc)
    first = sched.tick(now=now)
    second = sched.tick(now=now)
    assert len(first) == 1
    assert second == []    # debounced


def test_disabled_schedule_does_not_fire():
    sched = CronScheduler()
    s = sched.add(Schedule(cron_expr="* * * * *", enabled=False))
    assert sched.tick(now=datetime(2026, 4, 20, 9, 0, tzinfo=timezone.utc)) == []


def test_remove_schedule():
    sched = CronScheduler()
    s = sched.add(Schedule(cron_expr="* * * * *"))
    assert sched.remove(s.id) is True
    assert sched.remove("ghost") is False
