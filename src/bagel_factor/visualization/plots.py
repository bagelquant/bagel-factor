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
    'plot_cumulative_spread'
]


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
    quantile_return_df.mean().plot(kind="bar")
    plt.title(title)
    plt.xlabel("Quantile")
    plt.ylabel("Mean Return")
    plt.tight_layout()
    return plt.gcf()


def plot_cumulative_spread(
    spread_series: pd.Series, 
    return_type: Literal['log', 'normal'] = 'log', 
    title: str = "Cumulative Quantile Spread Return"
) -> Figure:
    plt.figure(figsize=DEFAULT_FIG_SIZE)
    spread_series_cumulative = accumulate_return(spread_series, return_type=return_type)
    plt.title(title)
    sns.lineplot(x=spread_series_cumulative.index, y=spread_series_cumulative.values)
    plt.xlabel("Date")
    plt.ylabel("Cumulative Spread Return")
    plt.tight_layout()
    return plt.gcf()
