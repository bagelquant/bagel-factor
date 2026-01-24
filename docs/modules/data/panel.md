# `bagelfactor.data.panel`

Canonical panel utilities.

A **panel** is the canonical internal representation:

- type: `pd.DataFrame`
- index: `pd.MultiIndex` with names `("date", "asset")`

This standardization is what makes cross-sectional transforms and factor evaluation composable.

## `ensure_panel_index(df, ..., source="columns") -> pd.DataFrame`

Normalizes input into canonical panel form.

### Inputs

- `source="columns"` (default): expects `date` and `asset` as columns
- `source="index"`: expects a MultiIndex already

### Logic

- If `source="columns"`:
  - convert `date` column using `pd.to_datetime`
  - set the index to `[date, asset]`
  - ensure index names are exactly `("date", "asset")` (will rename if necessary)
- If `sort=True` (default), sorts the index.

### Example
```python
from bagelfactor.data import ensure_panel_index

raw = pd.DataFrame({
    'date': ['2020-01-01', '2020-01-01'],
    'asset': ['A', 'B'],
    'close': [10.0, 11.0],
    'alpha': [0.1, 0.2],
})
panel = ensure_panel_index(raw)
assert panel.index.names == ['date','asset']
```

### Expected output

A new DataFrame with:

- `panel.index` is a MultiIndex
- index names exactly `("date", "asset")`
- columns preserved and ready for downstream transforms

## `validate_panel(panel) -> None`

Checks invariants and raises:

- `TypeError` if index is not a MultiIndex
- `ValueError` if index names are not exactly `("date", "asset")`

Expected output: `None` (or an exception).

## `add_returns(panel, price="close", ret_1d="ret_1d") -> pd.DataFrame`

Adds 1-day simple returns per asset.

### Logic

- groups by `asset`
- uses `pct_change()` on the `price` column

### Expected output

- returns a new DataFrame with one additional column (default `ret_1d`)
- the first observation per asset is `NaN` (no prior day)

## `add_forward_returns(panel, horizons=(1,5,20), prefix="ret_fwd_") -> pd.DataFrame`

Adds forward return labels for modeling/evaluation.

### Logic

For each horizon `h` (per asset):

- `ret_fwd_h[t] = price[t+h] / price[t] - 1`

### Expected output

- returns a new DataFrame with added columns: `ret_fwd_1`, `ret_fwd_5`, ...
- the last `h` rows per asset are `NaN` (no future price)
