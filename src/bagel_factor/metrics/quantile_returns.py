
import pandas as pd
import numpy as np
from typing import Optional, List

def quantile_returns(
    factor: pd.Series,
    future_returns: pd.Series,
    n_quantiles: int = 10,
    quantile_labels: Optional[List[int | str]] = None,
    min_ratio: float = 0.5
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
    min_ratio: float in [0, 1]
        If the fraction of missing values in a (date, quantile) group exceeds this ratio,
        skip calculation for that group (result NaN). Default 0.5.
    Returns
    -------
    pd.DataFrame
        index: date, columns: quantile label, values: mean return for each quantile/date
    """
    if n_quantiles <= 0:
        raise ValueError("n_quantiles must be a positive integer")
    if quantile_labels is not None and len(quantile_labels) != n_quantiles:
        raise ValueError("quantile_labels length must equal n_quantiles")
    if not factor.index.equals(future_returns.index):
        raise ValueError("Indices of factor and returns must match.")
    labels = quantile_labels if quantile_labels is not None else list(range(1, n_quantiles + 1))
    df = pd.DataFrame({'factor': factor, 'future_returns': future_returns})
    # Group by date without sorting to preserve input order
    dates = df.index.get_level_values('date')
    g = df.groupby(dates, sort=False)
    # Identify constant groups (<=1 unique, excluding NaN)
    nunique = g['factor'].transform('nunique')
    is_const = nunique.le(1)
    # Rank within date for non-constant groups; NaNs remain NaN
    ranks = g['factor'].rank(method='first', ascending=True)
    n_non_na = g['factor'].transform('count').astype(float)
    # Compute bin edges: ceil(rank / (n / Q)) in [1..Q]
    with np.errstate(invalid='ignore', divide='ignore'):
        denom = (n_non_na / float(n_quantiles))
        qnum_arr = np.ceil((ranks / denom).to_numpy())
    qnum = pd.Series(qnum_arr, index=df.index)
    # Bound to [1, n_quantiles]
    qnum[qnum < 1] = 1
    qnum[qnum > n_quantiles] = n_quantiles
    # Assign middle quantile for constant groups
    mid_label = labels[n_quantiles // 2]
    # Prepare integer quantile numbers for mapping to labels
    qnum_int = qnum.astype('Int64')  # nullable int, preserves NaN
    # Map to labels if custom labels provided
    if quantile_labels is None:
        quantile_series = qnum_int
    else:
        map_dict = {i + 1: labels[i] for i in range(len(labels))}
        quantile_series = qnum_int.map(map_dict)
    # Fill constant groups with mid_label
    quantile_series = quantile_series.astype('object')
    quantile_series[is_const] = mid_label
    # Use ordered categorical for efficient grouping and consistent ordering
    df['quantile'] = pd.Categorical(quantile_series, categories=labels, ordered=True)
    # Aggregate with missing-ratio threshold
    grp_keys = [dates, 'quantile']
    grp_all = df.groupby(grp_keys, sort=False, observed=True)
    counts_total = grp_all.size()
    grp = grp_all['future_returns']
    counts_non_na = grp.count()
    sums = grp.sum(min_count=1)
    # Mean of non-NaNs
    means = sums / counts_non_na.replace(0, np.nan)
    # Mask groups where missing fraction > min_ratio
    with np.errstate(invalid='ignore', divide='ignore'):
        miss_frac = (counts_total - counts_non_na) / counts_total
    if min_ratio < 0 or min_ratio > 1:
        raise ValueError("min_ratio must be between 0 and 1")
    means = means.where(miss_frac <= min_ratio)
    result = means.unstack('quantile')
    # Ensure consistent column order
    try:
        result = result.reindex(columns=labels)
    except Exception:
        pass
    # Shift result by one row to align quantile returns with the current date
    return result.shift(1).dropna(how='all')

def quantile_spread(
    quantile_returns_df: pd.DataFrame,
    upper: Optional[int | str] = None,
    lower: Optional[int | str] = None
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
