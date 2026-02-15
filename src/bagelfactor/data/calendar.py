"""bagelfactor.data.calendar

Trading calendar helpers with a small local cache.

API:
- retrieve_trading_calendar(): download/build calendar and save under `data/calendar/`
- get_trading_calendar_daily(): load calendar from local (retrieve if missing)
- get_trading_calendar_weekly(): derived weekly schedule from daily sessions
- get_trading_calendar_monthly(): derived monthly schedule from daily/weekly sessions
- get_trading_calendar_quartly(): derived quarterly schedule from daily sessions

Calendars are sourced from the optional third-party dependency `exchange-calendars`.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Literal

import pandas as pd


class CalendarError(RuntimeError):
    """Base error for calendar issues."""


class UnsupportedMarketError(CalendarError):
    def __init__(self, market: str) -> None:
        super().__init__(f"Unsupported market: {market!r}. Supported: 'US', 'CN', 'XNYS', 'XSHG'.")


Market = Literal["US", "CN", "XNYS", "XSHG"]

WeeklyOption = Literal["mon", "tue", "wed", "thu", "fri", "start", "end"]
MonthlyOption = Literal["start", "end", "first_week_start", "last_week_end"]
QuartlyOption = Literal["start", "end"]


def _normalize_market(market: str) -> str:
    m = market.upper()
    if m == "US":
        return "XNYS"
    if m == "CN":
        return "XSHG"
    return m


def _calendar_dir() -> Path:
    import os

    return Path(os.environ.get("BAGELFACTOR_CALENDAR_DIR", "data/calendar"))


def _calendar_path(market: Market) -> Path:
    code = _normalize_market(market)
    return _calendar_dir() / f"{code.lower()}_sessions.csv"


@cache
def _get_exchange_calendar(market: Market):
    try:
        import exchange_calendars as xc
    except ImportError as e:  # pragma: no cover
        raise CalendarError(
            "exchange-calendars is required for trading calendar functionality. "
            "Install it (e.g. `uv add exchange-calendars`)."
        ) from e

    code = _normalize_market(market)
    if code not in {"XNYS", "XSHG"}:
        raise UnsupportedMarketError(market)

    return xc.get_calendar(code)


def retrieve_trading_calendar(
    *,
    market: Market = "US",
    start: str | pd.Timestamp = "1990-01-01",
    end: str | pd.Timestamp | None = None,
    overwrite: bool = False,
) -> Path:
    """Retrieve trading sessions from the source calendar and save them locally."""

    path = _calendar_path(market)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not overwrite:
        return path

    cal = _get_exchange_calendar(market)
    start_ts = pd.Timestamp(start)
    end_ts = (
        pd.Timestamp(end)
        if end is not None
        else (pd.Timestamp.utcnow().normalize() + pd.Timedelta(days=366))
    )

    idx = cal.sessions_in_range(start_ts, end_ts)  # type: ignore
    pd.DataFrame({"date": pd.DatetimeIndex(idx).tz_localize(None).strftime("%Y-%m-%d")}).to_csv(
        path, index=False
    )
    return path


def _load_daily_sessions(market: Market) -> pd.DatetimeIndex:
    path = _calendar_path(market)
    if not path.exists():
        retrieve_trading_calendar(market=market)

    df = pd.read_csv(path)
    if "date" not in df.columns:
        raise CalendarError(f"Invalid calendar file: missing 'date' column: {path}")

    idx = pd.to_datetime(df["date"], utc=False).sort_values()
    return pd.DatetimeIndex(idx, name="date")


def get_trading_calendar_daily(
    *,
    market: Market = "US",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.DatetimeIndex:
    """Load (or retrieve) and return daily trading sessions."""

    idx = _load_daily_sessions(market)
    if start is not None:
        idx = idx[idx >= pd.Timestamp(start)]
    if end is not None:
        idx = idx[idx <= pd.Timestamp(end)]
    return idx


def get_trading_calendar_weekly(
    *,
    market: Market = "US",
    option: WeeklyOption = "end",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.DatetimeIndex:
    """Return a weekly trading schedule derived from daily sessions."""

    idx = get_trading_calendar_daily(market=market, start=start, end=end)
    if len(idx) == 0:
        return idx

    week = idx.to_period("W-SUN")
    s = pd.Series(idx, index=idx)

    if option in {"start", "end"}:
        grouped = s.groupby(week)
        out = grouped.min() if option == "start" else grouped.max()
        return pd.DatetimeIndex(out.values, name="date")

    dow = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4}[option]
    out = idx[idx.dayofweek == dow]  # type: ignore
    return pd.DatetimeIndex(out, name="date")


def get_trading_calendar_monthly(
    *,
    market: Market = "US",
    option: MonthlyOption = "end",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.DatetimeIndex:
    """Return a monthly trading schedule."""

    idx = get_trading_calendar_daily(market=market, start=start, end=end)
    if len(idx) == 0:
        return idx

    if option in {"start", "end"}:
        month = idx.to_period("M")
        s = pd.Series(idx, index=idx)
        grouped = s.groupby(month)
        out = grouped.min() if option == "start" else grouped.max()
        return pd.DatetimeIndex(out.values, name="date")

    if option == "first_week_start":
        w = get_trading_calendar_weekly(market=market, option="start", start=start, end=end)
        g = pd.Series(w, index=w).groupby(w.to_period("M"))
        return pd.DatetimeIndex(g.min().values, name="date")

    w = get_trading_calendar_weekly(market=market, option="end", start=start, end=end)
    g = pd.Series(w, index=w).groupby(w.to_period("M"))
    return pd.DatetimeIndex(g.max().values, name="date")


def get_trading_calendar_quartly(
    *,
    market: Market = "US",
    option: QuartlyOption = "end",
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.DatetimeIndex:
    """Return a quarterly trading schedule (spelling kept for API compatibility)."""

    idx = get_trading_calendar_daily(market=market, start=start, end=end)
    if len(idx) == 0:
        return idx

    q = idx.to_period("Q")
    s = pd.Series(idx, index=idx)
    grouped = s.groupby(q)
    out = grouped.min() if option == "start" else grouped.max()
    return pd.DatetimeIndex(out.values, name="date")
