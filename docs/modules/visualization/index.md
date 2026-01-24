# `bagelfactor.visualization`

Matplotlib-based visualization helpers for single-factor evaluation outputs.

## Install

This module requires `matplotlib`.

## Public API

```python
from bagelfactor.visualization import (
    plot_ic_time_series,
    plot_ic_hist,
    plot_quantile_returns_time_series,
    plot_quantile_returns_heatmap,
    plot_long_short_time_series,
    plot_turnover_time_series,
    plot_turnover_heatmap,
    plot_coverage_time_series,
    plot_result_summary,
)
```

## Example

```python
from bagelfactor.single_factor import SingleFactorJob
from bagelfactor.visualization import plot_result_summary

res = SingleFactorJob.run(panel, factor="alpha", horizons=(1, 5, 20), n_quantiles=5)
fig = plot_result_summary(res, horizon=5)
fig.show()
```

## Detailed docs

- [`single_factor`](./single_factor.md)
