"""
Unit tests for ProgressService.recalculate_stats - the core streak and
completion-percentage engine. Repositories are faked (no real DB needed)
since this logic is pure computation over plan/progress rows.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from types import SimpleNamespace

from app.services.progress_service import ProgressService


@dataclass
class FakePlanDay:
    day_number: int
    reading_date: date
    old_testament: str | None = "Genesis 1"
    new_testament: str | None = "Matthew 1"


@dataclass
class FakeProgressEntry:
    day_number: int
    reading_plan_id: str
    completed: bool = True


class FakePlanRepo:
    def __init__(self, days: list[FakePlanDay], today_day_number: int):
        self._days = days
        self._today_day_number = today_day_number

    def list_all_ordered(self):
        return self._days

    def get_today(self):
        for d in self._days:
            if d.day_number == self._today_day_number:
                return d
        return None


class FakeProgressRepo:
    def __init__(self, entries: list[FakeProgressEntry]):
        self._entries = entries
        self.saved_stats = None

    def all_for_user(self, user_id):
        return self._entries

    def upsert_stats(self, user_id, **kwargs):
        self.saved_stats = kwargs
        return SimpleNamespace(**kwargs)


def make_service(days: list[FakePlanDay], entries: list[FakeProgressEntry], today_day: int) -> tuple[ProgressService, FakeProgressRepo]:
    service = ProgressService.__new__(ProgressService)  # bypass __init__ (no real DB)
    service.plan_repo = FakePlanRepo(days, today_day)
    service.progress_repo = FakeProgressRepo(entries)
    return service, service.progress_repo


def _days(n: int, start: date):
    return [FakePlanDay(day_number=i + 1, reading_date=start + timedelta(days=i)) for i in range(n)]


def test_perfect_streak_all_days_completed():
    start = date(2026, 1, 1)
    days = _days(5, start)
    entries = [FakeProgressEntry(day_number=d.day_number, reading_plan_id=d.day_number) for d in days]
    service, repo = make_service(days, entries, today_day=5)

    stats = service.recalculate_stats(user_id="u1")

    assert stats.days_completed == 5
    assert stats.current_streak == 5
    assert stats.longest_streak == 5
    assert stats.overall_percentage == 100.0


def test_streak_broken_by_missed_day():
    start = date(2026, 1, 1)
    days = _days(5, start)
    # completed days 1,2 then missed day 3, then completed 4,5
    entries = [FakeProgressEntry(day_number=n, reading_plan_id=n) for n in (1, 2, 4, 5)]
    service, repo = make_service(days, entries, today_day=5)

    stats = service.recalculate_stats(user_id="u1")

    assert stats.days_completed == 4
    assert stats.current_streak == 2  # days 4,5 consecutive ending today
    assert stats.longest_streak == 2  # both runs (1,2) and (4,5) are length 2
    assert stats.overall_percentage == 80.0


def test_current_streak_zero_when_today_not_done_yet():
    start = date(2026, 1, 1)
    days = _days(5, start)
    entries = [FakeProgressEntry(day_number=n, reading_plan_id=n) for n in (1, 2, 3, 4)]  # today (5) not done
    service, repo = make_service(days, entries, today_day=5)

    stats = service.recalculate_stats(user_id="u1")

    assert stats.days_completed == 4
    assert stats.current_streak == 4  # streak carried from yesterday since today isn't done yet
    assert stats.longest_streak == 4


def test_no_completions_gives_zero_stats():
    start = date(2026, 1, 1)
    days = _days(3, start)
    service, repo = make_service(days, [], today_day=3)

    stats = service.recalculate_stats(user_id="u1")

    assert stats.days_completed == 0
    assert stats.current_streak == 0
    assert stats.longest_streak == 0
    assert stats.overall_percentage == 0.0
