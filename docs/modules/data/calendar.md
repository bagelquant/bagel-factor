# `bagelfactor.data.calendar`

Trading calendar helpers with a local on-disk cache.

This module provides **session labels** (trading dates) for markets using `exchange-calendars`, and stores the resulting daily sessions under `data/calendar/` so your research is:

- reproducible
- fast to re-run
- consistent across modules

## Supported markets (v0)

- US equities: NYSE (`XNYS`) via `market="US"` or `market="XNYS"`
- China equities: Shanghai (`XSHG`) via `market="CN"` or `market="XSHG"`

## Cache layout

By default, the cache directory is:

- `data/calendar/`

Files are written as CSVs with a single column:

- `date` (ISO formatted, timezone-naive)

Example:

- `data/calendar/xnys_sessions.csv`
- `data/calendar/xshg_sessions.csv`

Override cache directory via:

- `BAGELFACTOR_CALENDAR_DIR=/some/path`

## API

### 1) `retrieve_trading_calendar(...) -> Path`

Downloads/builds daily sessions from the source calendar and writes them to disk.

```python
from bagelfactor.data import retrieve_trading_calendar

path = retrieve_trading_calendar(market="US", start="2010-01-01", end="2025-12-31")
```

Expected output:

- returns a `Path` pointing to the cached CSV
- the file exists after the call

### 2) `get_trading_calendar_daily(...) -> pd.DatetimeIndex`

Loads daily sessions from disk (retrieving them first if missing).

```python
from bagelfactor.data import get_trading_calendar_daily

idx = get_trading_calendar_daily(market="US", start="2020-01-01", end="2020-12-31")
```

Expected output:

- a sorted `pd.DatetimeIndex` of trading session labels

### 3) `get_trading_calendar_weekly(option=...) -> pd.DatetimeIndex`

Derives a weekly schedule from daily sessions.

Options:

- `option="start"`: first trading day of each Monday–Sunday week
- `option="end"`: last trading day of each Monday–Sunday week
- `option in {"mon","tue","wed","thu","fri"}`: sessions occurring on that weekday (if present)

Expected output:

- a `DatetimeIndex` at weekly frequency (subset/aggregation of daily sessions)

### 4) `get_trading_calendar_monthly(option=...) -> pd.DatetimeIndex`

Derives a monthly schedule.

Options:

- `"start"`: first trading day of each month
- `"end"`: last trading day of each month
- `"first_week_start"`: first weekly-"start" date within each month
- `"last_week_end"`: last weekly-"end" date within each month

Expected output:

- a `DatetimeIndex` with one date per month

### 5) `get_trading_calendar_quartly(option=...) -> pd.DatetimeIndex`

Derives a quarterly schedule from daily sessions (note: function name spelling is `quartly`).

Options:

- `"start"`: first trading day of each quarter
- `"end"`: last trading day of each quarter

Expected output:

- a `DatetimeIndex` with one date per quarter
