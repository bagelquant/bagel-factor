# `bagelfactor.single_factor` (module index)

Single-factor evaluation job.

## Public API

```python
from bagelfactor.single_factor import SingleFactorJob, SingleFactorResult
```

## Typical usage

```python
from bagelfactor.data import ensure_panel_index
from bagelfactor.single_factor import SingleFactorJob

panel = ensure_panel_index(raw_df)
res = SingleFactorJob.run(panel, factor="alpha", horizons=(1, 5, 20))

ic_1d = res.ic[1]
qret_5d = res.quantile_returns[5]
```
