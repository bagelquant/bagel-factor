# `bagelfactor.data`

The `bagelfactor.data` package defines the **canonical data model** and utilities used throughout `bagel-factor`.

At v0, most workflows are built on a single canonical representation:

- a **panel**: `pd.DataFrame` indexed by `("date", "asset")`

This makes it easy to:

- compute labels (returns),
- align features to a trading calendar,
- enforce point-in-time rules,
- filter by a universe,
- and keep factor signals consistent.

## Design principles

- **Explicit point-in-time**: if a transformation could introduce lookahead, it should be explicit (e.g., lagging or calendar alignment).
- **Thin wrappers**: factor/universe objects are lightweight wrappers around pandas objects.
- **Composable utilities**: most helpers accept/return canonical pandas objects (DataFrame/Series/DatetimeIndex).

## Canonical objects

### Panel

A panel is a `pd.DataFrame` whose index is a `pd.MultiIndex` with:

- level 0 name: `date`
- level 1 name: `asset`

Example index:

```
(date, asset)
(2020-01-02, AAPL)
(2020-01-02, MSFT)
(2020-01-03, AAPL)
...
```

### Trading calendar

A trading calendar is a `pd.DatetimeIndex` describing valid session labels at some frequency:

- daily sessions (most common)
- weekly / monthly / quarterly schedules
- or any user-provided index

## Sub-modules

- `bagelfactor.data.loaders` — load tabular data from files into `pd.DataFrame`
- `bagelfactor.data.panel` — panel index normalization + return labeling
- `bagelfactor.data.align` — lagging and alignment to trading calendars
- `bagelfactor.data.factors` — `FactorSeries` / `FactorMatrix` containers
- `bagelfactor.data.universe` — membership masks (`Universe`) and filtering
- `bagelfactor.data.calendar` — cached trading calendars (US/CN) + schedules

## Typical workflow (example)

```python
import pandas as pd
from bagelfactor.data import (
    LoadConfig, load_df,
    ensure_panel_index,
    add_forward_returns,
    align_to_calendar,
    get_trading_calendar_daily,
)

# 1) Load raw data
panel = load_df(LoadConfig(source="prices.parquet"))

# 2) Normalize to canonical panel
panel = ensure_panel_index(panel)  # expects columns date/asset

# 3) Add labels
panel = add_forward_returns(panel, price="close", horizons=(1, 5, 20))

# 4) Align to a trading calendar (optional)
cal = get_trading_calendar_daily(market="US", start="2018-01-01", end="2024-12-31")
panel = align_to_calendar(panel, cal, method="ffill")
```

Expected output shape after step (4):

- index is all `(date, asset)` combinations for dates in `cal` and all assets observed in `panel`
- missing dates become explicit rows
- when `method="ffill"`, values carry forward per-asset
