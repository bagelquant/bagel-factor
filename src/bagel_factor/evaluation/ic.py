"""
Calculate the IC and ICIR

IC -> a time-series of information coefficients
ICIR -> a ratio that measures the stability of the IC over time
rolling ICIR -> a rolling window of the ICIR

input data: standard format(multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns)
"""

import pandas as pd
from typing import Literal


def calculate_ic_s(
    data: pd.DataFrame,
    target: str,
    prediction: str,
    rebalance_date_index: pd.DatetimeIndex,
    method: Literal['spearman', 'pearson'] = 'spearman'
) -> pd.Series:
    """
    Calculate the IC (Information Coefficient) between the target and prediction for each rebalance date.

    Return a Series with the IC values indexed by rebalance dates.
    
    Parameters
    ----------
    data : pd.DataFrame
        Multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns.
    target : str
        The name of the target column.
    prediction : str
        The name of the prediction column.
    rebalance_date_index : pd.DatetimeIndex
        The index of rebalance dates.
    method : Literal['spearman', 'pearson']
        The method to use for calculating the correlation.

    Returns
    -------
    pd.Series
        A Series with the IC values indexed by rebalance dates.
    """
    ic_values = []

    for date in rebalance_date_index:
        # Filter data for the current rebalance date
        current_data = data.xs(date, level='date')
        
        # Calculate the correlation
        if method == 'spearman':
            ic = current_data[target].corr(current_data[prediction], method='spearman')
        elif method == 'pearson':
            ic = current_data[target].corr(current_data[prediction], method='pearson')
        else:
            raise ValueError("Method must be either 'spearman' or 'pearson'.")

        ic_values.append(ic)

    return pd.Series(ic_values, index=rebalance_date_index).dropna()
