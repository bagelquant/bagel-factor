# `bagelfactor.metrics.turnover`

Quantile turnover calculation.

## `quantile_turnover(quantile, n_quantiles) -> pd.Series`

Compute per-date turnover for each quantile.

Turnover is defined as:

`turnover(q, t) = 1 - |members(q,t) ∩ members(q,t-1)| / |members(q,t) ∪ members(q,t-1)|`

### Parameters
- `quantile: pd.Series`
  - Must be indexed by `(date, asset)`.
  - Values are quantile IDs (1..n).
- `n_quantiles: int`
  - Maximum quantile ID to consider (loops `1..n_quantiles`).

### Returns
- `pd.Series`
  - index: `pd.MultiIndex` with names `(date, quantile)`
  - name: `"turnover"`
  - dates begin at the **second unique date** (turnover needs `t-1`).

### Raises
- `TypeError`: if `quantile` is not indexed by a `pd.MultiIndex`.

### Notes (implementation details)
- Internally builds membership sets for each `(date, quantile)`.
- If an entire `(date, quantile)` pair has no members in both `t` and `t-1`, it is omitted.
- If the input has fewer than 2 unique dates, returns an empty float series.

### Example
```python
turn = quantile_turnover(q, n_quantiles=5)
```
