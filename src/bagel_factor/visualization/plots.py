import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.figure import Figure
from typing import Literal

from ..metrics import accumulate_return

# set default style
sns.set_style("whitegrid")
DEFAULT_FIG_SIZE = (12, 6)

__all__ = [
    'plot_ic_series',
    'plot_quantile_returns',
    'plot_cumulative_return',
    'plot_ic_histogram',
    'plot_quantile_heatmap',
    'plot_quantile_cumulative',
    'plot_drawdown',
    'plot_return_distribution'
]


def _prepend_zero_start(obj: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Prepend a zero-valued row one step before the first index value.

    Supported index types:
    - DatetimeIndex: uses first difference as step; fallback to 1 day.
    - TimedeltaIndex: uses first difference as step; fallback to 1 day.
    Other index types are returned unchanged.
    """
    if obj.empty:
        return obj

    idx = obj.index
    prev = None

    # DatetimeIndex
    if isinstance(idx, pd.DatetimeIndex):
        if len(idx) > 1:
            try:
                delta = idx[1] - idx[0]
            except Exception:
                delta = pd.Timedelta(days=1)
        else:
            delta = pd.Timedelta(days=1)
        prev = idx[0] - delta

    # TimedeltaIndex
    elif isinstance(idx, pd.TimedeltaIndex):
        if len(idx) > 1:
            delta = idx[1] - idx[0]
        else:
            delta = pd.Timedelta(days=1)
        prev = idx[0] - delta

    if prev is None:
        # Fallback: unable to compute, do nothing
        return obj

    if isinstance(obj, pd.Series):
        zeros = pd.Series(0.0, index=[prev], name=obj.name)
        return pd.concat([zeros, obj])
    else:
        zero_row = pd.DataFrame(0.0, index=[prev], columns=obj.columns)
        return pd.concat([zero_row, obj])


def plot_ic_series(ic_series: pd.Series, title: str = "Information Coefficient (IC) Time Series") -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    sns.lineplot(x=ic_series.index, y=ic_series.values)
    # Add average line 
    mean_ic = ic_series.mean()
    plt.axhline(y=mean_ic, color='r', linestyle='--', label=f'Mean IC: {mean_ic:.4f}')
    plt.legend()
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("IC")
    plt.tight_layout()
    return plt.gcf()

def plot_quantile_returns(quantile_return_df: pd.DataFrame, title: str = "Quantile Returns") -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    quantile_return_df.dropna().mean().plot(kind="bar")
    plt.title(title)
    plt.xlabel("Quantile")
    plt.ylabel("Mean Return")
    plt.tight_layout()
    return plt.gcf()


def plot_cumulative_return(
    spread_series: pd.Series | pd.DataFrame,
    return_type: Literal['log', 'normal'] = 'log',
    title: str = "Cumulative Quantile Spread Return"
) -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    spread_series_cumulative = accumulate_return(spread_series.dropna(), return_type=return_type)
    spread_series_cumulative = _prepend_zero_start(spread_series_cumulative)
    plt.title(title)
    if isinstance(spread_series_cumulative, pd.DataFrame):
        for col in spread_series_cumulative.columns:
            plt.plot(spread_series_cumulative.index, spread_series_cumulative[col].to_numpy(), label=str(col))
        plt.legend()
    else:
        sns.lineplot(x=spread_series_cumulative.index, y=spread_series_cumulative.to_numpy())
    plt.xlabel("Date")
    plt.ylabel("Cumulative Spread Return")
    plt.tight_layout()
    return plt.gcf()


def plot_ic_histogram(ic_series: pd.Series, bins: int = 30, title: str = "IC Distribution") -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    sns.histplot(ic_series.dropna().to_numpy(), bins=bins, kde=True, color='steelblue', alpha=0.8)
    mean_ic = ic_series.mean()
    plt.axvline(mean_ic, color='red', linestyle='--', label=f'Mean: {mean_ic:.4f}')
    plt.title(title)
    plt.xlabel("IC")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    return plt.gcf()


def plot_quantile_heatmap(quantile_return_df: pd.DataFrame, title: str = "Quantile Rank Heatmap") -> Figure:
    """Plot a heatmap of per-day ranks across quantiles.

    For each date (row), values across quantile columns are ranked so that 1 indicates
    the highest return for that day. This highlights which quantiles performed best
    over time independent of return magnitudes.
    """
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    # Ensure columns are in increasing order for better readability
    quantile_return_df = quantile_return_df.dropna()
    try:
        quantile_return_df = quantile_return_df.reindex(columns=sorted(quantile_return_df.columns))
    except Exception:
        pass
    # Rank within each day across quantiles (1 = best)
    ranks = quantile_return_df.rank(axis=1, ascending=False, method='average')
    n_q = len(ranks.columns)
    sns.heatmap(
        ranks.T,
        cmap='viridis_r',
        vmin=1,
        vmax=n_q if n_q > 0 else None,
        cbar_kws={'label': 'Rank (1 = best)'}
    )
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Quantile")
    plt.tight_layout()
    return plt.gcf()


def plot_quantile_cumulative(
    quantile_return_df: pd.DataFrame,
    return_type: Literal['log', 'normal'] = 'log',
    title: str = "Cumulative Return by Quantile"
) -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    cum = accumulate_return(quantile_return_df.dropna(), return_type=return_type)
    cum = _prepend_zero_start(cum)
    for col in cum.columns:
        plt.plot(cum.index, cum[col].to_numpy(), label=str(col))
    plt.legend(title='Quantile')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.tight_layout()
    return plt.gcf()


def plot_drawdown(
    returns: pd.Series | pd.DataFrame,
    return_type: Literal['log', 'normal'] = 'log',
    title: str = "Drawdown"
) -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    cumulative = accumulate_return(returns.dropna(), return_type=return_type)
    if isinstance(cumulative, pd.DataFrame):
        for col in cumulative.columns:
            peak = cumulative[col].cummax()
            dd = cumulative[col] / peak - 1
            plt.plot(cumulative.index, dd.to_numpy(), label=str(col))
        plt.legend()
    else:
        peak = cumulative.cummax()
        dd = cumulative / peak - 1
        sns.lineplot(x=cumulative.index, y=dd.values)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    return plt.gcf()


def plot_return_distribution(
    returns: pd.Series | pd.DataFrame,
    bins: int = 30,
    title: str = "Return Distribution"
) -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    if isinstance(returns, pd.DataFrame):
        for col in returns.columns:
            sns.histplot(returns[col].dropna().to_numpy(), bins=bins, kde=False, stat='density', alpha=0.4, label=str(col))
        plt.legend()
    else:
        sns.histplot(returns.dropna().to_numpy(), bins=bins, kde=True, stat='density', alpha=0.8, color='steelblue')
    plt.title(title)
    plt.xlabel("Return")
    plt.ylabel("Density")
    plt.tight_layout()
    return plt.gcf()
