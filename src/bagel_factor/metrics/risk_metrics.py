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
    returns: pd.Series | pd.DataFrame,
    return_type: Literal['log', 'normal'] = 'log'
) -> pd.Series | pd.DataFrame:
    """
    Accumulate returns to get the cumulative return series.

    Parameters
    ----------
    returns : pd.Series | pd.DataFrame
        Periodic returns (log or normal, as specified by `return_type`).
    return_type : {'log', 'normal'}, default 'log'
        Type of returns provided. If 'log', input is log returns. If 'normal', input is arithmetic returns.

    Returns
    -------
    pd.Series | pd.DataFrame
        Cumulative return series.
    """
    if return_type == 'log':
        # Elementwise exp that preserves pandas type for Series/DataFrame
        return returns.cumsum().transform(np.exp)
    else:
        # Works for Series and DataFrame
        return (1 + returns).cumprod() - 1

def annualized_volatility(
    returns: pd.Series | pd.DataFrame,
    periods_per_year: int = 252,
    return_type: Literal['log', 'normal'] = 'log',
) -> float | pd.Series:
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
    float | pd.Series
        Annualized volatility.
    """
    # For both Series and DataFrame, std over index axis and scale by sqrt(T)
    vol = returns.std(ddof=1) * np.sqrt(periods_per_year)
    return vol


def sharpe_ratio(
    returns: pd.Series | pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    return_type: Literal['log', 'normal'] = 'log'
) -> float | pd.Series:
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
    if return_type == 'log':
        ann_excess_return: float | pd.Series = excess_returns.mean() * periods_per_year
    else:
        base = (1 + excess_returns).prod()
        if isinstance(base, pd.Series):
            base = base.astype(float)
            base = base.where(base >= 0, np.nan)
            ann_excess_return = base.pow(periods_per_year / len(excess_returns)) - 1
        else:
            try:
                base_val = np.asarray(base, dtype=float).item()
            except Exception:
                base_val = float('nan')
            if base_val < 0:
                ann_excess_return = float('nan')
            else:
                ann_excess_return = base_val ** (periods_per_year / len(excess_returns)) - 1
    ann_vol = annualized_volatility(returns, periods_per_year, return_type=return_type)
    result = ann_excess_return / ann_vol
    if isinstance(result, pd.Series):
        return result.replace([np.inf, -np.inf], np.nan)
    # scalar
    if not np.isfinite(result):
        return np.nan
    return float(result)


def max_drawdown(
    returns: pd.Series | pd.DataFrame,
    return_type: Literal['log', 'normal'] = 'log'
) -> float | pd.Series:
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
    returns: pd.Series | pd.DataFrame,
    periods_per_year: int = 252,
    return_type: Literal['log', 'normal'] = 'log'
) -> float | pd.Series:
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
    if return_type == 'log':
        ann_return: float | pd.Series = returns.mean() * periods_per_year
    else:
        base = (1 + returns).prod()
        if isinstance(base, pd.Series):
            base = base.astype(float)
            base = base.where(base >= 0, 0.0)
            ann_return = base.pow(periods_per_year / len(returns)) - 1
        else:
            try:
                base_val = np.asarray(base, dtype=float).item()
            except Exception:
                base_val = float('nan')
            if base_val < 0:
                base_val = 0.0
            ann_return = base_val ** (periods_per_year / len(returns)) - 1
    mdd = abs(max_drawdown(returns, return_type=return_type))
    result = ann_return / mdd
    if isinstance(result, pd.Series):
        return result.replace([np.inf, -np.inf], np.nan)
    if not np.isfinite(result):
        return np.nan
    return float(result)


def downside_risk(
    returns: pd.Series | pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    return_type: Literal['log', 'normal'] = 'log'
) -> float | pd.Series:
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
    # Identify downside observations relative to risk free rate
    if isinstance(returns, pd.DataFrame):
        downside = returns.where(returns < risk_free_rate) - risk_free_rate
        downside_std = downside.std(ddof=1).fillna(0.0)
        return downside_std * np.sqrt(periods_per_year)
    else:
        if returns.empty:
            return np.nan
        downside = returns[returns < risk_free_rate] - risk_free_rate
        if downside.empty:
            return 0.0
        downside_std = downside.std(ddof=1)
        return float(downside_std * np.sqrt(periods_per_year))


def sortino_ratio(
    returns: pd.Series | pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    return_type: Literal['log', 'normal'] = 'log'
) -> float | pd.Series:
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
    if return_type == 'log':
        ann_excess_return: float | pd.Series = excess_returns.mean() * periods_per_year
    else:
        base = (1 + excess_returns).prod()
        if isinstance(base, pd.Series):
            base = base.astype(float)
            base = base.where(base >= 0, 0.0)
            ann_excess_return = base.pow(periods_per_year / len(returns)) - 1
        else:
            try:
                base_val = np.asarray(base, dtype=float).item()
            except Exception:
                base_val = float('nan')
            if base_val < 0:
                base_val = 0.0
            ann_excess_return = base_val ** (periods_per_year / len(returns)) - 1
    drisk = downside_risk(returns, risk_free_rate, periods_per_year, return_type=return_type)
    result = ann_excess_return / drisk
    if isinstance(result, pd.Series):
        return result.replace([np.inf, -np.inf], np.nan)
    if not np.isfinite(result):
        return np.nan
    return float(result)
