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
# compute rank IC for 5-day forward returns
ic = ic_series(panel, factor="alpha", label="ret_fwd_5", method="spearman")

# quick diagnostics
print(ic.describe())           # mean, std, quartiles
print(ic.mean(), ic.std(ddof=0))
print("ICIR:", icir(ic))

# plot with visualization helpers
from bagelfactor.visualization import plot_ic_time_series
plot_ic_time_series(ic, rolling=21)  # 21-day rolling mean
```

### Implementation note
- The vectorized implementation computes per-date moments (n, mean, variances, covariance) and derives Pearson correlation from these aggregated sums. This is numerically equivalent to per-group pandas.corr but avoids Python-level loops and scales much better for large panels.

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
