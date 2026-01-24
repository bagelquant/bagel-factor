"""bagelfactor.visualization

Matplotlib-based visualization helpers.

This subpackage is intentionally optional and requires `matplotlib`.
Install with: `pip install bagel-factor[visualization]`
"""

from .single_factor import (
    plot_coverage_time_series,
    plot_ic_hist,
    plot_ic_time_series,
    plot_long_short_time_series,
    plot_quantile_returns_heatmap,
    plot_quantile_returns_time_series,
    plot_result_summary,
    plot_turnover_heatmap,
    plot_turnover_time_series,
)

__all__ = [
    "plot_ic_time_series",
    "plot_ic_hist",
    "plot_quantile_returns_time_series",
    "plot_quantile_returns_heatmap",
    "plot_long_short_time_series",
    "plot_turnover_time_series",
    "plot_turnover_heatmap",
    "plot_coverage_time_series",
    "plot_result_summary",
]
