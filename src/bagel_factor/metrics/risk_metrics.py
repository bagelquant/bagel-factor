import numpy as np
import pandas as pd
from typing import Literal

__all__ = [
    'accumulate_return',
    'annualized_volatility',
    'sharpe_ratio',
    'max_drawdown',
    'calmar_ratio',
    'downside_risk',
    'sortino_ratio'
]

def accumulate_return(
    returns: pd.Series, 
    return_type: Literal['log', 'normal'] = 'log'
) -> pd.Series:
    """
    Accumulate returns to get the cumulative return series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    pd.Series
        Cumulative return series.
    """
    if return_type == 'log':
        return returns.cumsum().apply(np.exp)
    else:
        return (1 + returns).cumprod()

def annualized_volatility(
    returns: pd.Series, 
    periods_per_year: int = 252, 
    return_type: Literal['log', 'normal'] = 'log',
) -> float:
    """
    Calculate the annualized volatility of a returns series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    periods_per_year : int, default 252
        Number of periods in a year (e.g., 252 for daily returns).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    float
        Annualized volatility.
    """
    if returns.empty or returns.isna().all():
        return np.nan
    if return_type == 'log':
        return returns.std(ddof=1) * np.sqrt(periods_per_year)
    else:
        return returns.std(ddof=1) * np.sqrt(periods_per_year)


def sharpe_ratio(
    returns: pd.Series, 
    risk_free_rate: float = 0.0, 
    periods_per_year: int = 252, 
    return_type: Literal['log', 'normal'] = 'log'
) -> float:
    """
    Calculate the annualized Sharpe ratio of a returns series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    risk_free_rate : float, default 0.0
        Risk-free rate per period, in the same return type as `returns`.
    periods_per_year : int, default 252
        Number of periods in a year (e.g., 252 for daily returns).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    float
        Annualized Sharpe ratio.
    """
    excess_returns = returns - risk_free_rate
    if returns.empty or returns.isna().all():
        return np.nan
    if return_type == 'log':
        ann_excess_return: float = excess_returns.mean() * periods_per_year
    else:
        prod_result = (1 + excess_returns).prod()
        if isinstance(prod_result, complex):
            base = float(prod_result.real)
        else:
            try:
                base = float(pd.to_numeric(prod_result, errors='coerce'))
            except Exception:
                base = float('nan')
        if base < 0:
            return np.nan
        power = periods_per_year / len(returns)
        ann_excess_return: float = base ** power - 1
    ann_vol = annualized_volatility(returns, periods_per_year, return_type=return_type)
    if ann_vol == 0:
        return np.nan
    return ann_excess_return / ann_vol


def max_drawdown(
    returns: pd.Series, 
    return_type: Literal['log', 'normal'] = 'log'
) -> float:
    """
    Calculate the maximum drawdown of a returns series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    float
        Maximum drawdown (as a negative number).
    """
    cumulative = accumulate_return(returns, return_type=return_type)
    peak = cumulative.cummax()
    drawdown = cumulative / peak - 1
    return drawdown.min()


def calmar_ratio(
    returns: pd.Series, 
    periods_per_year: int = 252, 
    return_type: Literal['log', 'normal'] = 'log'
) -> float:
    """
    Calculate the Calmar ratio of a returns series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    periods_per_year : int, default 252
        Number of periods in a year (e.g., 252 for daily returns).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    float
        Calmar ratio.
    """
    if returns.empty or returns.isna().all():
        return np.nan
    if return_type == 'log':
        ann_return = returns.mean() * periods_per_year
    else:
        prod_result = (1 + returns).prod()
        if isinstance(prod_result, complex):
            base = float(prod_result.real)
        else:
            try:
                base = float(pd.to_numeric(prod_result, errors='coerce'))
            except Exception:
                base = float('nan')
        if base < 0:
            base = 0.0
        ann_return = base ** (periods_per_year / len(returns)) - 1
    mdd = abs(max_drawdown(returns, return_type=return_type))
    if mdd == 0:
        return np.nan
    return ann_return / mdd


def downside_risk(
    returns: pd.Series, 
    risk_free_rate: float = 0.0, 
    periods_per_year: int = 252, 
    return_type: Literal['log', 'normal'] = 'log'
) -> float:
    """
    Calculate the annualized downside risk of a returns series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    risk_free_rate : float, default 0.0
        Risk-free rate per period, in the same return type as `returns`.
    periods_per_year : int, default 252
        Number of periods in a year (e.g., 252 for daily returns).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    float
        Annualized downside risk.
    """
    if returns.empty or returns.isna().all():
        return np.nan
    downside = returns[returns < risk_free_rate] - risk_free_rate
    if downside.empty:
        return 0.0
    downside_std = downside.std(ddof=1)
    return downside_std * np.sqrt(periods_per_year)


def sortino_ratio(
    returns: pd.Series, 
    risk_free_rate: float = 0.0, 
    periods_per_year: int = 252, 
    return_type: Literal['log', 'normal'] = 'log') -> float:
    """
    Calculate the annualized Sortino ratio of a returns series.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns (log or normal, as specified by `return_type`).
    risk_free_rate : float, default 0.0
        Risk-free rate per period, in the same return type as `returns`.
    periods_per_year : int, default 252
        Number of periods in a year (e.g., 252 for daily returns).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    float
        Annualized Sortino ratio.
    """
    excess_returns = returns - risk_free_rate
    if returns.empty or returns.isna().all():
        return np.nan
    if return_type == 'log':
        ann_excess_return = excess_returns.mean() * periods_per_year
    else:
        prod_result = (1 + excess_returns).prod()
        if isinstance(prod_result, complex):
            base = float(prod_result.real)
        else:
            try:
                base = float(pd.to_numeric(prod_result, errors='coerce'))
            except Exception:
                base = float('nan')
        if base < 0:
            base = 0.0
        ann_excess_return = base ** (periods_per_year / len(returns)) - 1
    drisk = downside_risk(returns, risk_free_rate, periods_per_year, return_type=return_type)
    if drisk == 0:
        return np.nan
    return ann_excess_return / drisk
