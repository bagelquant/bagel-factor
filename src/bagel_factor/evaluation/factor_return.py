"""
Calculate Factor Returns
"""

import pandas as pd
import statsmodels.api as sm

from typing import Literal


def calculate_factor_return_grouping(
    data: pd.DataFrame,
    target: str,
    prediction: str,
    rebalance_date_index: pd.DatetimeIndex,
    group_num: int = 5,
) -> pd.DataFrame:
    """    
    Calculate the factor returns by grouping the predictions into quantiles.

    Parameters
    ----------
    data : pd.DataFrame
        Multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns.
    target : str
        The name of the target factor
    prediction : str
        The name of the prediction column, which will be the next period's return.
    rebalance_date_index : pd.DatetimeIndex
        The index of rebalance dates.
    grouping : int, optional
        The number of groups to create based on the predictions, by default 5.

    Returns
    -------
    pd.DataFrame
        A DataFrame with factor returns for each group indexed by rebalance dates.
    """
    factor_returns = []

    for date in rebalance_date_index:
        # Filter data for the current rebalance date
        current_data = data.xs(date, level='date')
        
        # Create quantiles based on the factor value
        current_group = pd.qcut(current_data[target], q=group_num, labels=False)

        # Calculate the mean return for each quantile
        quantile_returns = current_data.groupby(current_group)[prediction].mean()

        factor_returns.append(quantile_returns)

    next_period_return = pd.DataFrame(factor_returns, index=rebalance_date_index)
    
    # Calculate Higher Minus Lower (HML) return
    hml_return = next_period_return.iloc[:, group_num - 1] - next_period_return.iloc[:, 0]
    next_period_return['HML'] = hml_return
    return next_period_return.dropna()


def calculate_factor_return_regression(
    data: pd.DataFrame,
    target: str,
    prediction: str,
    rebalance_date_index: pd.DatetimeIndex,
    method: Literal['OLS', 'WLS', 'RLM'] = 'OLS',
    intercept: bool = False,
    **kwargs
) -> pd.DataFrame:
    """
    Calculate factor returns using regression.

    Parameters
    ----------
    data : pd.DataFrame
        Multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns.
    target : str
        The name of the target factor.
    prediction : str
        The name of the prediction column, which will be the next period's return.
    rebalance_date_index : pd.DatetimeIndex
        The index of rebalance dates.

    Returns
    -------
    pd.DataFrame
        A DataFrame with factor returns indexed by rebalance dates.
    """
    factor_returns = []
    for date in rebalance_date_index:
        # Filter data for the current rebalance date
        try:
            current_data = data.xs(date, level='date')
        except KeyError:
            continue

        # Drop NA values for regression
        reg_data = current_data[[target, prediction]].dropna()
        if reg_data.empty:
            factor_returns.append(float('nan'))
            continue

        X = reg_data[[target]]
        y = reg_data[prediction]
        if intercept:
            X = sm.add_constant(X)

        if method == 'OLS':
            model = sm.OLS(y, X, **kwargs)
            results = model.fit()
        elif method == 'WLS':
            weights = kwargs.get('weights', None)
            if weights is None:
                raise ValueError('WLS method requires "weights" in kwargs')
            model = sm.WLS(y, X, weights=weights, **kwargs)
            results = model.fit()
        elif method == 'RLM':
            model = sm.RLM(y, X, **kwargs)
            results = model.fit()
        else:
            raise ValueError(f'Unknown regression method: {method}')

        # The factor return is the coefficient of the target factor
        coef = results.params[target] if not intercept else results.params.get(target, float('nan'))
        factor_returns.append(coef)

    factor_returns_df = pd.DataFrame({'factor_return': factor_returns}, index=rebalance_date_index)
    return factor_returns_df.dropna()
