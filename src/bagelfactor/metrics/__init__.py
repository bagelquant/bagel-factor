"""bagelfactor.metrics

Single-factor evaluation metrics.

v0 scope: IC/RankIC, ICIR, quantile returns, long-short returns, turnover, coverage.
"""

from .coverage import coverage_by_date
from .ic import ic_series, icir
from .quantiles import assign_quantiles, quantile_returns
from .turnover import quantile_turnover

__all__ = [
    "ic_series",
    "icir",
    "assign_quantiles",
    "quantile_returns",
    "quantile_turnover",
    "coverage_by_date",
]
