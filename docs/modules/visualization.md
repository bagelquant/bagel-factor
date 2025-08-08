# visualization Module

The `visualization` module provides plotting utilities for analyzing and presenting factor model results, including information coefficient (IC) time series, quantile returns, cumulative and drawdown charts, and distributions. It works seamlessly with outputs of the `metrics` module and supports publication-quality visualizations using Matplotlib and Seaborn.

## Submodules

### 1. `plots.py`

Functions for visualizing key aspects of factor performance:

- `plot_ic_series(ic_series)`: IC time series with a dashed mean line.
- `plot_ic_histogram(ic_series, bins=30)`: Histogram of IC values with KDE and mean marker.
- `plot_quantile_returns(quantile_return_df)`: Bar chart of mean returns by quantile.
- `plot_quantile_heatmap(quantile_return_df)`: Heatmap of per-day ranks across quantiles (1 = best), highlighting which quantiles led on each date independent of magnitude.
- `plot_cumulative_return(spread_series, return_type='log')`: Cumulative quantile spread return; starts from zero by auto-prepending a pre-date point based on inferred index step.
- `plot_quantile_cumulative(quantile_return_df, return_type='log')`: Cumulative return per quantile; also starts from zero as above.
- `plot_drawdown(returns, return_type='log')`: Drawdown over time from cumulative returns.
- `plot_return_distribution(returns, bins=30)`: Return distribution; supports overlay for DataFrame inputs.

Notes:

- Most functions accept either `pd.Series` or `pd.DataFrame` where it makes sense.
- Cumulative plots add one synthetic timestamp before the first index and set value to 0 to emphasize a common starting point.

All plots use a consistent, publication-ready style (`whitegrid`) and a default figure size for clarity.

---

## Usage Example

```python
from bagel_factor.visualization.plots import (
  plot_ic_series,
  plot_ic_histogram,
  plot_quantile_returns,
  plot_quantile_heatmap,
  plot_cumulative_return,
  plot_quantile_cumulative,
  plot_drawdown,
  plot_return_distribution,
)

plot_ic_series(ic_series)
plot_ic_histogram(ic_series)
plot_quantile_returns(quantile_returns_df)
plot_quantile_heatmap(quantile_returns_df)  # ranks per day (1 = best)
plot_cumulative_return(quantile_spread, return_type='log')  # starts at 0
plot_quantile_cumulative(quantile_returns_df, return_type='log')  # starts at 0
plot_drawdown(quantile_spread)
plot_return_distribution(quantile_spread)
```

---

## Summary

The `visualization` module enables intuitive, reproducible presentation of factor analysis, supporting both research notebooks and reports.
