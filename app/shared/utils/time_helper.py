from datetime import datetime, timezone, date, timedelta


def today_utc() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _end_of_utc_day(d: date, tz: timezone = timezone.utc) -> datetime:
    """Inclusive end of calendar day `d` in `tz` (for created_at / range upper bound)."""
    return datetime(d.year, d.month, d.day, 23, 59, 59, 999999, tzinfo=tz)


def resolve_period(
    days: int | None,
    from_date: date | None,
    to_date: date | None,
    tz: timezone = timezone.utc,
) -> tuple[datetime, datetime]:
    """Returns [start, end] datetimes: start = midnight first day, end = last instant of last day (inclusive)."""
    if from_date and to_date:
        start = datetime(from_date.year, from_date.month, from_date.day, tzinfo=tz)
        end = _end_of_utc_day(to_date, tz)
    else:
        today_start = today_utc()
        d = days or 30
        start = today_start - timedelta(days=d - 1)
        end = _end_of_utc_day(today_start.date(), tz)

    return start, end