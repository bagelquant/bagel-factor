# `bagelfactor.metrics.ic`

Information Coefficient (IC) utilities.

## Overview

This module computes a **per-date cross-sectional correlation** between a factor and a label (typically forward returns).

- Input must be a canonical `(date, asset)` panel.
- Output is a time series indexed by `date`.

## `ic_series(panel, factor, label, method="spearman") -> pd.Series`

Compute **per-date** information coefficient between `panel[factor]` and `panel[label]`.

### Parameters
- `panel: pd.DataFrame`
  - Must be indexed by `pd.MultiIndex` with names `("date", "asset")`.
- `factor: str`
  - Column name for the factor signal.
- `label: str`
  - Column name for the label, e.g. `"ret_fwd_1"`.
- `method: str`
  - `"spearman"` or `"pearson"`.

### Returns
- `pd.Series`
  - Indexed by `date`.
  - Name: `"ic"`.
  - Contains `NaN` for dates with fewer than 2 valid observations.

### Raises
- `TypeError` / `ValueError`: if `panel` is not a valid canonical panel.
- `KeyError`: if `factor` or `label` column is missing.
- `ValueError`: if `method` is not `"spearman"` or `"pearson"`.

### Notes (implementation details)
- `method="spearman"` is implemented as:
  1) per-date ranking of `factor` and `label`
  2) Pearson correlation on the ranks
  This avoids a SciPy dependency.

### Example
```python
ic = ic_series(panel, factor="alpha", label="ret_fwd_5", method="spearman")
```

## `icir(ic: pd.Series) -> float`

Compute IC information ratio: `mean(ic) / std(ic)` using population std (`ddof=0`).

### Parameters
- `ic: pd.Series` — IC time series.

### Returns
- `float` — ICIR.

### Edge cases
- If `ic` is empty after dropping NaNs: returns `nan`.
- If standard deviation is 0 or NaN: returns `nan`.

### Example
```python
ratio = icir(ic)
```
