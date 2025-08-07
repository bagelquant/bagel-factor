
import pandas as pd
import numpy as np
from typing import Optional, Union

def quantile_returns(
    factor: pd.Series,
    future_returns: pd.Series,
    n_quantiles: int = 10,
    quantile_labels: Optional[Union[list, None]] = None,
    min_periods: int = 1
) -> pd.DataFrame:
    """
    Compute mean future returns for each factor quantile, grouped by date.

    Parameters
    ----------
    factor: pd.Series
        with MultiIndex (date, ticker)
    returns: pd.Series
        with MultiIndex (date, ticker)
    n_quantiles: int
        Number of quantile bins (default 10)
    quantile_labels: list or None
        Custom labels for quantiles (default None, uses 1..n_quantiles)
    min_periods: int
        Minimum number of stocks in a quantile to compute mean return (default 1)
    Returns
    -------
    pd.DataFrame
        index: date, columns: quantile label, values: mean return for each quantile/date
    """
    if not factor.index.equals(future_returns.index):
        raise ValueError("Indices of factor and returns must match.")
    if quantile_labels is None:
        quantile_labels = list(range(1, n_quantiles + 1))
    df = pd.DataFrame({'factor': factor, 'future_returns': future_returns})
    def assign_quantile(x):
        # If all values are nan or constant, assign all to middle quantile
        if x['factor'].nunique(dropna=True) <= 1:
            return pd.Series([quantile_labels[n_quantiles // 2]] * len(x), index=x.index)
        return pd.qcut(
            x['factor'],
            q=n_quantiles,
            labels=quantile_labels,
            duplicates='drop',
            # quantile_range is not a pd.qcut arg, but could be used for custom logic
        )
    df['quantile'] = df.groupby(df.index.get_level_values('date'), group_keys=False).apply(assign_quantile)
    # Compute mean returns for each quantile/date, only if enough non-nan values
    def mean_with_min(x):
        if x.notna().sum() < min_periods:
            return np.nan
        return x.mean()
    result = df.groupby([df.index.get_level_values('date'), 'quantile'], observed=False)['future_returns'].apply(mean_with_min).unstack('quantile')
    # Shift result by one row to align quantile returns with the current date
    return result.shift(1).dropna(how='all')

def quantile_spread(
    quantile_returns_df: pd.DataFrame,
    upper: Optional[Union[int, str]] = None,
    lower: Optional[Union[int, str]] = None
) -> pd.Series:
    """
    Compute the spread between upper and lower quantile returns for each date.
    By default, uses the highest and lowest quantiles.

    Parameters
    ----------
    quantile_returns_df: pd.DataFrame
        Output of quantile_returns (index: date, columns: quantile)
    upper: int or str or None
        Column label for upper quantile (default: max column)
    lower: int or str or None
        Column label for lower quantile (default: min column)
    Returns
    -------
    pd.Series
        index: date, values: upper - lower quantile return
    """
    if upper is None:
        upper = quantile_returns_df.columns.max()
    if lower is None:
        lower = quantile_returns_df.columns.min()
    spread = quantile_returns_df[upper] - quantile_returns_df[lower]
    spread.name = 'quantile_spread'
    return spread
