"""bagelfactor

Single-factor evaluation/testing toolkit.

Core data primitives live in `bagelfactor.data`.
"""

__all__ = [
    # data
    "LoadConfig",
    "load_df",
    "ensure_panel_index",
    "validate_panel",
    "add_returns",
    "add_forward_returns",
    "FactorSeries",
    "FactorMatrix",
    "Universe",
    "align_to_calendar",
    "lag_by_asset",
    "retrieve_trading_calendar",
    "get_trading_calendar_daily",
    "get_trading_calendar_weekly",
    "get_trading_calendar_monthly",
    "get_trading_calendar_quartly",
    # metrics
    "ic_series",
    "icir",
    "assign_quantiles",
    "quantile_returns",
    "quantile_turnover",
    "coverage_by_date",
    # preprocess
    "Pipeline",
    "DropNa",
    "Clip",
    "ZScore",
    "Rank",
    # reporting
    "to_csv",
    "to_parquet",
    # single_factor
    "SingleFactorJob",
    "SingleFactorResult",
    # stats
    "TTestResult",
    "ttest_1samp",
    "ttest_ind",
    "OLSResult",
    "ols_alpha_tstat",
    "ols_summary",
    # utils
    "PanelDiagnostics",
    "diagnose_panel",
    # visualization
    "plot_ic_time_series",
    "plot_ic_hist",
    "plot_quantile_returns_time_series",
    "plot_quantile_cumulative_returns",
    "plot_quantile_returns_heatmap",
    "plot_long_short_time_series",
    "plot_turnover_time_series",
    "plot_turnover_heatmap",
    "plot_coverage_time_series",
    "plot_result_summary",
]

from .data import (
    FactorMatrix,
    FactorSeries,
    LoadConfig,
    Universe,
    add_forward_returns,
    add_returns,
    align_to_calendar,
    ensure_panel_index,
    get_trading_calendar_daily,
    get_trading_calendar_monthly,
    get_trading_calendar_quartly,
    get_trading_calendar_weekly,
    lag_by_asset,
    load_df,
    retrieve_trading_calendar,
    validate_panel,
)
from .metrics import (
    assign_quantiles,
    coverage_by_date,
    ic_series,
    icir,
    quantile_returns,
    quantile_turnover,
)
from .preprocess import Clip, DropNa, Pipeline, Rank, ZScore
from .reporting import to_csv, to_parquet
from .single_factor import SingleFactorJob, SingleFactorResult
from .stats import OLSResult, TTestResult, ols_alpha_tstat, ols_summary, ttest_1samp, ttest_ind
from .utils import PanelDiagnostics, diagnose_panel
from .visualization import (
    plot_coverage_time_series,
    plot_ic_hist,
    plot_ic_time_series,
    plot_long_short_time_series,
    plot_quantile_cumulative_returns,
    plot_quantile_returns_heatmap,
    plot_quantile_returns_time_series,
    plot_result_summary,
    plot_turnover_heatmap,
    plot_turnover_time_series,
)
