"""
This module defines the type for preprocessing methods used in factor data handling.
Preprocessing methods are callable functions that take a pandas Series and return a processed Series.

"""
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
    return factor_data.groupby('date').transform(lambda x: (x - x.mean()) / x.std(ddof=0))

def cross_sectional_minmax(factor_data: pd.Series) -> pd.Series:
    """
    Cross-sectional min-max normalization, groupby date.
    Scales each date's values to [0, 1].
    """
    return factor_data.groupby('date').transform(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0.0)

def cross_sectional_rank(factor_data: pd.Series, 
                         method: Literal['average', 'min', 'max', 'first', 'dense'] = 'dense',
                         ascending: bool = True) -> pd.Series:
    """
    Cross-sectional rank normalization, groupby date.
    Ranks each date's values, default dense method, ascending order.
    """
    return factor_data.groupby('date').transform(lambda x: x.rank(method=method, ascending=ascending))

def cross_sectional_winsorize(factor_data: pd.Series, 
                              lower: float = 0.01, 
                              upper: float = 0.99) -> pd.Series:
    """
    Cross-sectional winsorization, groupby date.
    Clips each date's values to the [lower, upper] quantiles.
    """
    def winsorize(x):
        lower_val = x.quantile(lower)
        upper_val = x.quantile(upper)
        return x.clip(lower=lower_val, upper=upper_val)
    return factor_data.groupby('date').transform(winsorize)
