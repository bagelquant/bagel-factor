"""bagelfactor.metrics

Single-factor evaluation metrics.

v0 scope: IC/RankIC, ICIR, quantile returns, long-short returns, turnover, coverage.
"""

from .ic import ic_series, icir
from .quantiles import assign_quantiles, quantile_returns
from .turnover import quantile_turnover
from .coverage import coverage_by_date

__all__ = [
    "ic_series",
    "icir",
    "assign_quantiles",
    "quantile_returns",
    "quantile_turnover",
    "coverage_by_date",
]
