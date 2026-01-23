# `bagelfactor.visualization.single_factor`

Matplotlib plotting helpers for `SingleFactorResult` and its component outputs.

All plotting functions:
- accept a pandas object (Series/DataFrame)
- optionally accept `ax=`
- return the `matplotlib.axes.Axes` they drew on (except `plot_result_summary`, which returns a `Figure`).

## Internal helpers

### `_require_mpl()`

Imports `matplotlib` lazily and returns `(plt, mdates, Axes, Figure)`.

- Raises `ImportError` with a friendly message if matplotlib is not installed.

### `_to_dt_index(x) -> pd.DatetimeIndex`

Convert an index to `DatetimeIndex` via `pd.to_datetime`.

### `_format_datetime_xaxis(ax)`

Applies a date locator + `ConciseDateFormatter` to the x-axis.

## IC plots

### `plot_ic_time_series(ic, *, ax=None, title=None, grid=True, zero_line=True, rolling=None, rolling_label=None, color="C0")`

Line plot of the IC series.

- If `rolling` is set (>=2), overlays a rolling mean.
- Sets a 0.0 horizontal reference line by default.

### `plot_ic_hist(ic, *, ax=None, bins=40, title=None, grid=True, show_mean=True, show_zero=True)`

Histogram of IC values.

- Optionally shows a mean vertical line and/or a zero line.

## Quantile return plots

### `plot_quantile_returns_time_series(quantile_returns, *, ax=None, title=None, grid=True, legend=True)`

Line plot: one line per quantile.

### `plot_quantile_returns_heatmap(quantile_returns, *, ax=None, title=None, cmap="RdBu_r", center=0.0)`

Heatmap of quantile returns.

- Rows are quantiles.
- Colors are centered around `center` (default 0).

## Long-short plots

### `plot_long_short_time_series(long_short, *, ax=None, title=None, grid=True, cumulative=False)`

Line plot of long-short series.

- If `cumulative=True`, plots cumulative returns via `(1+s).cumprod()-1`.

## Turnover plots

### `plot_turnover_time_series(turnover, *, ax=None, title=None, grid=True)`

Plots average turnover across quantiles through time.

### `plot_turnover_heatmap(turnover, *, ax=None, title=None, cmap="viridis")`

Heatmap of turnover with rows=quantiles, cols=dates.

## Coverage plots

### `plot_coverage_time_series(coverage, *, ax=None, title=None, grid=True)`

Line plot of per-date coverage.

## Summary

### `plot_result_summary(result, *, horizon=1, figsize=(12,10)) -> Figure`

Create a multi-panel figure summarizing:
- IC time series + histogram
- quantile returns time series + heatmap
- long-short time series
- turnover heatmap
- coverage time series

This is intended as the quickest way to visualize a `SingleFactorResult`.
