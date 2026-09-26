"""Date range for admin KPI queries, chosen in Philippine time.

Dates are whole local days in Asia/Manila (UTC+8): a range of Oct 1 to Oct 10
covers Oct 1 00:00 through Oct 10 23:59:59.999 Manila time, which is
Sep 30 16:00 UTC up to (not including) Oct 10 16:00 UTC. Filters compare
aware datetimes, so Django converts them to UTC for the database.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db.models import Q

# Pinned here rather than read from settings.TIME_ZONE so the evaluation's
# day boundaries cannot move if the server setting ever changes.
KPI_TIMEZONE_NAME = "Asia/Manila"
KPI_TIMEZONE = ZoneInfo(KPI_TIMEZONE_NAME)


@dataclass(frozen=True)
class KpiRange:
    start_date: date | None = None
    end_date: date | None = None

    @property
    def is_bounded(self) -> bool:
        return self.start_date is not None or self.end_date is not None

    @property
    def start_at(self) -> datetime | None:
        """Local midnight at the start of start_date (inclusive)."""
        if self.start_date is None:
            return None
        return datetime.combine(self.start_date, time.min, tzinfo=KPI_TIMEZONE)

    @property
    def end_before(self) -> datetime | None:
        """Local midnight after end_date (exclusive), so end_date is a full day."""
        if self.end_date is None:
            return None
        return datetime.combine(self.end_date + timedelta(days=1), time.min, tzinfo=KPI_TIMEZONE)

    def q(self, field: str) -> Q:
        """Filter `field` (a datetime path) to the range; empty Q when unbounded."""
        condition = Q()
        if self.start_at is not None:
            condition &= Q(**{f"{field}__gte": self.start_at})
        if self.end_before is not None:
            condition &= Q(**{f"{field}__lt": self.end_before})
        return condition

    def payload(self) -> dict:
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "timezone": KPI_TIMEZONE_NAME,
        }


ALL_TIME = KpiRange()
