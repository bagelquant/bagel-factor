# `bagelfactor.metrics.quantiles`

Quantile assignment and quantile-return aggregation.

## `assign_quantiles(panel, factor, n_quantiles=5) -> pd.Series`

Assign a **cross-sectional quantile bucket** per `(date, asset)`.

### Parameters
- `panel: pd.DataFrame` — canonical panel.
- `factor: str` — factor column.
- `n_quantiles: int` — number of buckets (>= 2).

### Returns
- `pd.Series`
  - Same index as `panel` (`(date, asset)`).
  - dtype: pandas nullable `Int64`.
  - Values are 1..`n_quantiles`, or `pd.NA` if factor is missing.
  - Name: `"quantile"`.

### Raises
- `ValueError`: if `n_quantiles < 2`.
- `KeyError`: if `factor` column missing.

### Notes (internal behavior)
- Ranking uses `rank(method="first")` for deterministic tie-breaking.
- Buckets are computed with `pd.qcut(..., duplicates="drop")`.
  - If duplicates are dropped, you may end up with fewer than `n_quantiles` realized buckets on that date.

## `quantile_returns(panel, quantile, label) -> pd.DataFrame`

Compute mean label return per `(date, quantile)`.

### Parameters
- `panel: pd.DataFrame` — canonical panel.
- `quantile: pd.Series`
  - Quantile assignment series, typically from `assign_quantiles`.
  - Reindexed to `panel.index` internally.
- `label: str` — label column (e.g. `ret_fwd_1`).

### Returns
- `pd.DataFrame`
  - index: `date`
  - columns: integer quantile numbers (sorted)
  - values: mean label return across assets in that quantile at that date

### Raises
- `KeyError`: if `label` is missing.

### Example
```python
# assign 5 quantiles and compute 20-day quantile returns
q = assign_quantiles(panel, factor="alpha", n_quantiles=5)
qr = quantile_returns(panel, quantile=q, label="ret_fwd_20")

# quick checks
print(q.groupby(level='date').value_counts().head())  # bucket sizes per date
print(qr.mean())  # average return per quantile over time
```

### Notes on bucket construction
- Deterministic tie-breaking is used for reproducibility; when the factor has many identical values this may result in fewer realized buckets on that date.
- For thin universes, prefer fewer quantiles (e.g., 3) to ensure stable bucket membership.
