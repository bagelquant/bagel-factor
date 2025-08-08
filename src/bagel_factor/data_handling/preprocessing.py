"""
This module defines the type for preprocessing methods used in factor data handling.
Preprocessing methods are callable functions that take a pandas Series and return a processed Series.

Performance notes:
- Prefer vectorized GroupBy.transform with built-ins over Python lambdas.
- Compute group statistics once and broadcast instead of per-row lambdas.
"""
import numpy as np
import pandas as pd
from typing import Callable, Literal


__all__ = [
    'PreprocessingMethod',
    'cross_sectional_zscore',
    'cross_sectional_minmax',
    'cross_sectional_rank',
    'cross_sectional_winsorize',
]

PreprocessingMethod = Callable[[pd.Series], pd.Series]


def cross_sectional_zscore(factor_data: pd.Series) -> pd.Series:
    """
    Cross-sectional z-score normalization, groupby date.
    :param factor_data: Series with MultiIndex (date, ticker).
    :return: Series with same index, z-scored within each date.
    """
    s = factor_data
    g = s.groupby(level='date', sort=False)
    mean = g.transform('mean')
    # std with ddof=0 computed from ddof=1 to avoid Python lambdas
    std1 = g.transform('std')
    n = g.transform('count').astype(float)
    # Guard against n==0 to avoid divide-by-zero; for n==1 std0 should be 0
    with np.errstate(invalid='ignore', divide='ignore'):
        std0 = std1 * np.sqrt((n - 1.0).clip(lower=0) / n.where(n > 0, np.nan))
    z = (s - mean) / std0
    return z

def cross_sectional_minmax(factor_data: pd.Series) -> pd.Series:
    """
    Cross-sectional min-max normalization, groupby date.
    Scales each date's values to [0, 1].
    """
    s = factor_data
    g = s.groupby(level='date', sort=False)
    minv = g.transform('min')
    maxv = g.transform('max')
    denom = (maxv - minv)
    # Where denom==0 (constant group), define result as 0.0 per spec
    out = pd.Series(0.0, index=s.index)
    mask = denom.ne(0)
    out.loc[mask] = ((s - minv) / denom).loc[mask]
    return out

def cross_sectional_rank(factor_data: pd.Series, 
                         method: Literal['average', 'min', 'max', 'first', 'dense'] = 'dense',
                         ascending: bool = True) -> pd.Series:
    """
    Cross-sectional rank normalization, groupby date.
    Ranks each date's values, default dense method, ascending order.
    """
    return factor_data.groupby(level='date', sort=False).rank(method=method, ascending=ascending)

def cross_sectional_winsorize(factor_data: pd.Series, 
                              lower: float = 0.01, 
                              upper: float = 0.99) -> pd.Series:
    """
    Cross-sectional winsorization, groupby date.
    Clips each date's values to the [lower, upper] quantiles.
    """
    s = factor_data
    g = s.groupby(level='date', sort=False)
    # Compute per-date quantiles once, then broadcast via map (avoids per-row Python calls)
    # Compute lower/upper quantiles separately to satisfy type checkers
    q_low = g.quantile(float(lower)).rename(lower)
    q_high = g.quantile(float(upper)).rename(upper)
    qdf = pd.concat([q_low, q_high], axis=1)
    # Broadcast thresholds back to full index via the date level
    dates = s.index.get_level_values('date')
    lower_thr = dates.map(qdf[lower])
    upper_thr = dates.map(qdf[upper])
    return s.clip(lower=lower_thr.values, upper=upper_thr.values)
