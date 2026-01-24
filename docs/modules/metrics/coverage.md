# `bagelfactor.metrics.coverage`

Coverage (missingness) metrics.

## `coverage_by_date(panel, column) -> pd.Series`

Compute the fraction of non-missing observations per date for a given column.

### Parameters
- `panel: pd.DataFrame` — canonical `(date, asset)` panel.
- `column: str` — column to measure.

### Returns
- `pd.Series`
  - index: `date`
  - name: `"coverage"`
  - values in `[0, 1]` (or `NaN` for empty groups).

### Raises
- `KeyError`: if `column` missing.
- `TypeError` / `ValueError`: if panel index is invalid.

### Example
```python
cov = coverage_by_date(panel, column="alpha")
```
