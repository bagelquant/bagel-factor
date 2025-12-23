# `bagelfactor.data.align`

Point-in-time alignment helpers.

This module focuses on **explicit** alignment steps that prevent accidental lookahead and make missing dates obvious.

## `align_to_calendar(panel, trade_calendar, method="raw") -> pd.DataFrame`

Align a canonical `(date, asset)` panel to a `pd.DatetimeIndex` of session labels.

### Inputs

- `panel`: canonical panel
- `trade_calendar`: `pd.DatetimeIndex` describing the target dates
- `method`:
  - `"raw"` (default): reindex and leave missing values as `NaN`
  - `"ffill"`: reindex then forward-fill within each asset

### Logic

1. Normalize the calendar to a sorted, unique, timezone-naive `DatetimeIndex`.
2. Collect the set of assets present in the input panel.
3. Build a target MultiIndex via Cartesian product: `(trade_calendar x assets)`.
4. Reindex the panel to the target index.
5. If `method="ffill"`, apply `groupby(level="asset").ffill()`.

### Expected output

- Index contains **every** `(date, asset)` pair for dates in the calendar.
- With `method="raw"`, any date gaps become explicit `NaN` rows.
- With `method="ffill"`, missing dates carry forward the latest known value per asset.

This makes downstream steps (labels, metrics, backtests) deterministic and calendar-aware.

## `lag_by_asset(panel, columns, periods=1) -> pd.DataFrame`

Shift selected columns forward in time within each asset.

### Logic

- `panel[columns] = panel[columns].groupby(level="asset").shift(periods)`

### Expected output

- new DataFrame with the same shape and index
- specified columns shifted; non-specified columns unchanged
- first `periods` rows per asset are `NaN` for shifted columns
