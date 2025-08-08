
import pandas as pd
from typing import Literal


def information_coefficient(
    factor: pd.Series,
    future_returns: pd.Series,
    method: Literal['pearson', 'spearman'] = 'pearson',
    min_periods_ratio: float = 0.6
) -> pd.Series:
    """
    Compute the Information Coefficient (IC) between factor and future returns, grouped by date.
    IC is the cross-sectional correlation (Pearson or Spearman) between factor and returns for each date.

    Parameters
    ----------
    factor: pd.Series 
        with MultiIndex (date, ticker)
    future_returns: pd.Series
        with MultiIndex (date, ticker), notice that this is future returns, not past returns (Avoid lookahead bias)
    method: Literal['pearson', 'spearman']
        Default 'pearson'. Correlation method to use.
    min_periods: int
        minimum number of pairs to compute correlation
    Returns
    -------
    pd.Series
        IC values indexed by date
    """
    if not factor.index.equals(future_returns.index):
        raise ValueError("Indices of factor and returns must match.")
    if method not in ('pearson', 'spearman'):
        raise ValueError("method must be 'pearson' or 'spearman'")
    df = pd.DataFrame({'factor': factor, 'future_returns': future_returns})
    def compute_ic(group):
        min_periods = int(len(group) * min_periods_ratio)
        return group['factor'].corr(group['future_returns'], method=method, min_periods=min_periods)
    ic_series = df.groupby(df.index.get_level_values('date')).apply(compute_ic)
    ic_series.name = f'IC_{method}'
    return ic_series
