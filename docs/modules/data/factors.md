# `bagelfactor.data.factors`

Lightweight factor containers.

In v0, factors are still *pandas-first* (Series/DataFrame on `(date, asset)`), but these wrappers add:

- a place for metadata (lookback, source fields, notes)
- a stable place for future factor-related helpers
- clearer intent in APIs (this object is a factor signal)

## `FactorSeries`

A single factor signal.

```python
from bagelfactor.data import FactorSeries

fs = FactorSeries(
    name="momentum_12m",
    values=panel["momentum_12m"],
    meta={"lookback_days": 252},
)
```

### Expected structure

- `values`: `pd.Series` indexed by MultiIndex `(date, asset)`.
- If the index level names are not `("date", "asset")`, they are renamed.

### `to_frame(column=None) -> pd.DataFrame`

Converts the factor to a single-column DataFrame.

Expected output:

- `pd.DataFrame` with the same MultiIndex
- one column named `column` if provided, otherwise `FactorSeries.name`

## `FactorMatrix`

A factor collection (multiple factor columns aligned to `(date, asset)`), useful for batch single-factor testing.

```python
from bagelfactor.data import FactorMatrix

fm = FactorMatrix(values=panel[["value", "quality", "momentum"]])
```

### Expected structure

- `values`: `pd.DataFrame` indexed by `(date, asset)`
- columns correspond to factor names

### `FactorMatrix.from_columns(panel, factors) -> FactorMatrix`

Builds a `FactorMatrix` from factor columns already present in a panel.

Expected output:

- `FactorMatrix(values=panel[factors])`
- raises `KeyError` if any requested factor columns are missing
