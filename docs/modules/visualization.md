# visualization Module

The `visualization` module provides plotting utilities for analyzing and presenting factor model results, including information coefficient (IC) time series, quantile returns, and cumulative spread returns. It is designed to work seamlessly with the outputs of the `metrics` module and supports publication-quality visualizations using Matplotlib and Seaborn.

## Submodules

### 1. `plots.py`

Contains functions for visualizing key aspects of factor performance:

- **`plot_ic_series`**: Plots the time series of Information Coefficient (IC) values, with an average IC reference line.
  - **Inputs**: `ic_series` (pd.Series, indexed by date)
  - **Parameters**: `title` (str, optional)
  - **Returns**: Matplotlib `Figure`

- **`plot_quantile_returns`**: Plots the mean return for each factor quantile as a bar chart.
  - **Inputs**: `quantile_return_df` (pd.DataFrame, columns: quantiles)
  - **Parameters**: `title` (str, optional)
  - **Returns**: Matplotlib `Figure`

- **`plot_cumulative_spread`**: Plots the cumulative return of the quantile spread strategy over time.
  - **Inputs**: `spread_series` (pd.Series, indexed by date)
  - **Parameters**: `return_type` ('log' or 'normal'), `title` (str, optional)
  - **Returns**: Matplotlib `Figure`

All plots use a consistent, publication-ready style (`whitegrid`) and a default figure size for clarity.

---

## Usage Example

```python
from bagel_factor.visualization.plots import plot_ic_series, plot_quantile_returns, plot_cumulative_spread

# Plot IC time series
fig1 = plot_ic_series(ic_series)
fig1.show()

# Plot quantile returns
fig2 = plot_quantile_returns(quantile_return_df)
fig2.show()

# Plot cumulative spread return
fig3 = plot_cumulative_spread(spread_series)
fig3.show()
```

---

## Summary

The `visualization` module enables intuitive and effective presentation of factor analysis results, supporting both research and reporting workflows in quantitative finance.
