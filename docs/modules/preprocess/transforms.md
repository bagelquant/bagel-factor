# `bagelfactor.preprocess.transforms`

Cross-sectional preprocessing transforms.

All transforms expect a canonical `(date, asset)` panel.

## `DropNa(column)`

Drop rows where `panel[column]` is `NaN`.

- Method: `transform(panel) -> pd.DataFrame`
- Raises: validation errors if panel index is not canonical.

## `Clip(column, lower=None, upper=None)`

Clip a column to `[lower, upper]` using `Series.clip()`.

- `lower`/`upper` may be `None` to clip on only one side.

## `ZScore(column)`

Per-date cross-sectional z-score.

### Behavior
- Groups by `date`.
- Uses population std (`ddof=0`).
- If std is 0 or NaN for a date, returns `NA` for that date.

### Example
```python
from bagelfactor.preprocess import ZScore
panel_z = ZScore('alpha').transform(panel)
# check per-date mean ~ 0 and std ~ 1 (where defined)
print(panel_z.groupby(level='date')['alpha'].agg(['mean','std']).dropna().head())
```

### Notes
- Z-scoring preserves relative distances but not monotonic ordering; if only order matters prefer `Rank`.
- For heavy-tailed signals consider winsorizing (`Clip`) before z-scoring to reduce the influence of outliers.

## `Rank(column, pct=True, method="first")`

Per-date cross-sectional ranking.

### Parameters
- `pct=True`: scales ranks to `[0, 1]`.
- `method="first"`: deterministic ordering for ties.

### Example
```python
from bagelfactor.preprocess import Rank
panel2 = Rank("alpha").transform(panel)
```
