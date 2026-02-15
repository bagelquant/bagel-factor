from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def _require_mpl():
    try:
        import matplotlib.dates as mdates  # type: ignore
        import matplotlib.pyplot as plt  # type: ignore
        from matplotlib.axes import Axes  # type: ignore
        from matplotlib.figure import Figure  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Visualization requires 'matplotlib' to be installed. "
            "Install with: pip install matplotlib"
        ) from e

    return plt, mdates, Axes, Figure


def _to_dt_index(x: pd.Index) -> pd.DatetimeIndex:
    if isinstance(x, pd.DatetimeIndex):
        return x
    return pd.DatetimeIndex(pd.to_datetime(x))


def _format_datetime_xaxis(ax) -> None:
    _, mdates, _, _ = _require_mpl()
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def plot_ic_time_series(
    ic: pd.Series,
    *,
    ax=None,
    title: str | None = None,
    grid: bool = True,
    zero_line: bool = True,
    rolling: int | None = None,
    rolling_label: str | None = None,
    color: str = "C0",
):
    """Plot IC/RIC time series."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    s = ic.dropna().copy()
    if len(s) == 0:
        ax.set_title(title or "IC time series")
        ax.grid(grid)
        return ax

    s.index = _to_dt_index(s.index)
    ax.plot(s.index, s.values, lw=1.3, color=color, label="IC")

    if rolling is not None and rolling >= 2:
        r = s.rolling(rolling).mean()
        ax.plot(
            r.index,
            r.values,
            lw=2.0,
            color="C1",
            label=rolling_label or f"Rolling mean ({rolling})",
        )

    if zero_line:
        ax.axhline(0.0, color="black", lw=0.8, alpha=0.6)

    ax.set_title(title or "IC time series")
    ax.set_ylabel("IC")
    _format_datetime_xaxis(ax)
    if grid:
        ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    return ax


def plot_ic_hist(
    ic: pd.Series,
    *,
    ax=None,
    bins: int = 40,
    title: str | None = None,
    grid: bool = True,
    show_mean: bool = True,
    show_zero: bool = True,
):
    """Plot IC histogram."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(6.5, 4))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    s = ic.dropna()
    ax.hist(s.values, bins=bins, alpha=0.85, color="C0", edgecolor="white")

    if show_zero:
        ax.axvline(0.0, color="black", lw=0.8, alpha=0.6)
    if show_mean and len(s):
        m = float(s.mean())
        ax.axvline(m, color="C1", lw=1.5, alpha=0.9)
        ax.text(m, ax.get_ylim()[1] * 0.95, f"mean={m:.3g}", ha="left", va="top")

    ax.set_title(title or "IC distribution")
    ax.set_xlabel("IC")
    ax.set_ylabel("count")
    if grid:
        ax.grid(True, alpha=0.3)
    return ax


def plot_quantile_returns_time_series(
    quantile_returns: pd.DataFrame,
    *,
    ax=None,
    title: str | None = None,
    grid: bool = True,
    legend: bool = True,
):
    """Plot quantile return time series (one line per quantile).

    Shows period-over-period returns for each quantile.
    For cumulative returns, use plot_quantile_cumulative_returns().

    Parameters
    ----------
    quantile_returns : pd.DataFrame
        Quantile returns indexed by date, columns are quantile numbers
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    title : str, optional
        Plot title
    grid : bool, default True
        Show grid
    legend : bool, default True
        Show legend

    Returns
    -------
    matplotlib.axes.Axes
        The axes object
    """

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    df = quantile_returns.copy()
    if len(df) == 0:
        ax.set_title(title or "Quantile returns")
        ax.grid(grid)
        return ax

    df.index = _to_dt_index(df.index)
    for c in df.columns:
        ax.plot(df.index, df[c].values, lw=1.3, label=f"Q{c}")

    ax.axhline(0.0, color="black", lw=0.8, linestyle="--", alpha=0.4)
    ax.set_title(title or "Quantile returns (period)")
    ax.set_ylabel("return")
    _format_datetime_xaxis(ax)
    if grid:
        ax.grid(True, alpha=0.3)
    if legend:
        ax.legend(loc="best", ncol=min(5, len(df.columns)))
    return ax


def plot_quantile_cumulative_returns(
    quantile_returns: pd.DataFrame,
    *,
    ax=None,
    title: str | None = None,
    grid: bool = True,
    legend: bool = True,
    start_value: float = 1.0,
):
    """Plot cumulative returns for each quantile.

    Computes cumulative product of (1 + return) to show wealth accumulation.
    Useful for visualizing long-term performance differences between quantiles.

    Parameters
    ----------
    quantile_returns : pd.DataFrame
        Quantile returns indexed by date, columns are quantile numbers
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    title : str, optional
        Plot title
    grid : bool, default True
        Show grid
    legend : bool, default True
        Show legend
    start_value : float, default 1.0
        Initial value for cumulative returns (e.g., 1.0 for 100% starting capital)

    Returns
    -------
    matplotlib.axes.Axes
        The axes object

    Examples
    --------
    >>> res = SingleFactorJob.run(panel, factor='alpha', price='close')
    >>> plot_quantile_cumulative_returns(res.quantile_returns[5])
    """

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    df = quantile_returns.copy()
    if len(df) == 0:
        ax.set_title(title or "Quantile cumulative returns")
        ax.grid(grid)
        return ax

    # Compute cumulative returns: (1 + r1) * (1 + r2) * ... * start_value
    cumret = (1.0 + df).cumprod() * start_value

    cumret.index = _to_dt_index(cumret.index)
    for c in cumret.columns:
        ax.plot(cumret.index, cumret[c].values, lw=2.0, label=f"Q{c}")

    ax.axhline(start_value, color="black", lw=0.8, linestyle="--", alpha=0.4)
    ax.set_title(title or "Quantile cumulative returns")
    ax.set_ylabel(f"cumulative value (start={start_value})")
    _format_datetime_xaxis(ax)
    if grid:
        ax.grid(True, alpha=0.3)
    if legend:
        ax.legend(loc="best", ncol=min(5, len(df.columns)))
    return ax


def plot_quantile_returns_heatmap(
    quantile_returns: pd.DataFrame,
    *,
    ax=None,
    title: str | None = None,
    cmap: str = "RdBu_r",
    center: float = 0.0,
):
    """Plot a heatmap of quantile returns (rows=quantiles, cols=dates)."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 3.5))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    df = quantile_returns.copy()
    if len(df) == 0:
        ax.set_title(title or "Quantile returns (heatmap)")
        return ax

    df = df.sort_index(axis=1)
    mat = df.T.values  # (n_quantiles, n_dates)

    vmax = float(pd.Series(mat.ravel()).dropna().abs().max()) if mat.size else 1.0
    if not pd.notna(vmax) or vmax == 0:
        vmax = 1.0

    im = ax.imshow(
        mat,
        aspect="auto",
        cmap=cmap,
        vmin=center - vmax,
        vmax=center + vmax,
        interpolation="nearest",
    )

    ax.set_yticks(range(len(df.columns)))
    ax.set_yticklabels([f"Q{c}" for c in df.columns])
    ax.set_xticks([])
    ax.set_title(title or "Quantile returns (heatmap)")
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    return ax


def plot_long_short_time_series(
    long_short: pd.Series,
    *,
    ax=None,
    title: str | None = None,
    grid: bool = True,
    cumulative: bool = False,
):
    """Plot long-short time series."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    s = long_short.dropna().copy()
    if len(s) == 0:
        ax.set_title(title or "Long-short")
        ax.grid(grid)
        return ax

    s.index = _to_dt_index(s.index)

    y = (1.0 + s).cumprod() - 1.0 if cumulative else s

    ax.plot(y.index, y.values, lw=1.5, color="C2")
    ax.axhline(0.0, color="black", lw=0.8, alpha=0.6)
    ax.set_title(title or ("Long-short (cumulative)" if cumulative else "Long-short"))
    ax.set_ylabel("return")
    _format_datetime_xaxis(ax)
    if grid:
        ax.grid(True, alpha=0.3)
    return ax


def _turnover_pivot(turnover: pd.Series) -> pd.DataFrame:
    if not isinstance(turnover.index, pd.MultiIndex):
        raise TypeError("turnover must be indexed by (date, quantile)")
    return (
        turnover.rename("turnover")
        .reset_index()
        .pivot(index="date", columns="quantile", values="turnover")
    )


def plot_turnover_time_series(
    turnover: pd.Series,
    *,
    ax=None,
    title: str | None = None,
    grid: bool = True,
    quantiles: Iterable[int] | None = None,
    average: bool = False,
):
    """Plot quantile turnover over time."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    df = _turnover_pivot(turnover)
    if len(df) == 0:
        ax.set_title(title or "Turnover")
        ax.grid(grid)
        return ax

    df.index = _to_dt_index(df.index)

    if average:
        s = df.mean(axis=1)
        ax.plot(s.index, s.values, lw=1.6, color="C3", label="avg")
    else:
        cols = list(df.columns)
        if quantiles is not None:
            cols = [c for c in cols if int(c) in set(quantiles)]
        for c in cols:
            ax.plot(df.index, df[c].values, lw=1.2, label=f"Q{c}")

    ax.set_title(title or ("Turnover (avg)" if average else "Turnover"))
    ax.set_ylabel("turnover")
    _format_datetime_xaxis(ax)
    if grid:
        ax.grid(True, alpha=0.3)
    ax.legend(loc="best", ncol=min(5, len(df.columns)))
    return ax


def plot_turnover_heatmap(
    turnover: pd.Series,
    *,
    ax=None,
    title: str | None = None,
    cmap: str = "viridis",
):
    """Heatmap of turnover (rows=quantiles, cols=dates)."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 3.5))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    df = _turnover_pivot(turnover).sort_index(axis=1)
    if len(df) == 0:
        ax.set_title(title or "Turnover (heatmap)")
        return ax

    mat = df.T.values
    im = ax.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")
    ax.set_yticks(range(len(df.columns)))
    ax.set_yticklabels([f"Q{c}" for c in df.columns])
    ax.set_xticks([])
    ax.set_title(title or "Turnover (heatmap)")
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    return ax


def plot_coverage_time_series(
    coverage: pd.Series,
    *,
    ax=None,
    title: str | None = None,
    grid: bool = True,
):
    """Plot coverage (non-missing fraction) over time."""

    plt, _, Axes, _ = _require_mpl()

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 3.5))

    if not isinstance(ax, Axes):
        raise TypeError("ax must be a matplotlib Axes")

    s = coverage.dropna().copy()
    if len(s) == 0:
        ax.set_title(title or "Coverage")
        ax.grid(grid)
        return ax

    s.index = _to_dt_index(s.index)
    ax.plot(s.index, s.values, lw=1.5, color="C4")
    ax.set_ylim(0.0, 1.05)
    ax.set_title(title or "Coverage")
    ax.set_ylabel("fraction")
    _format_datetime_xaxis(ax)
    if grid:
        ax.grid(True, alpha=0.3)
    return ax


def plot_result_summary(
    res,
    *,
    horizon: int | None = None,
    figsize: tuple[float, float] = (14, 12),
    cumulative: bool = True,
):
    """Multi-panel summary figure for a `SingleFactorResult`.

    Creates a 4×2 grid showing IC, quantile returns, long-short, and turnover.

    Parameters
    ----------
    res : SingleFactorResult
        Result object from SingleFactorJob.run()
    horizon : int, optional
        Which forward return horizon to plot. If None, uses first available.
    figsize : tuple[float, float], default (14, 12)
        Figure size in inches
    cumulative : bool, default True
        If True, show cumulative returns for quantiles. If False, show period returns.

    Returns
    -------
    matplotlib.figure.Figure
        The figure object
    """

    plt, _, _, Figure = _require_mpl()

    h = horizon if horizon is not None else (res.horizons[0] if res.horizons else None)
    if h is None:
        raise ValueError("No horizon available for plotting")

    fig: Figure
    fig, axes = plt.subplots(4, 2, figsize=figsize, constrained_layout=True)

    # Row 0: IC analysis
    plot_ic_time_series(res.ic[h], ax=axes[0, 0], title=f"IC time series (h={h})")
    plot_ic_hist(res.ic[h], ax=axes[0, 1], title=f"IC distribution (h={h})")

    # Row 1: Quantile returns
    if cumulative:
        plot_quantile_cumulative_returns(
            res.quantile_returns[h], ax=axes[1, 0], title=f"Quantile cumulative returns (h={h})"
        )
    else:
        plot_quantile_returns_time_series(
            res.quantile_returns[h], ax=axes[1, 0], title=f"Quantile returns (h={h})"
        )
    plot_quantile_returns_heatmap(
        res.quantile_returns[h], ax=axes[1, 1], title=f"Quantile returns heatmap (h={h})"
    )

    # Row 2: Long-short
    plot_long_short_time_series(
        res.long_short[h], ax=axes[2, 0], title=f"Long-short (h={h})", cumulative=False
    )
    plot_long_short_time_series(
        res.long_short[h], ax=axes[2, 1], title=f"Long-short cumulative (h={h})", cumulative=True
    )

    # Row 3: Turnover and coverage
    plot_turnover_time_series(res.turnover, ax=axes[3, 0], title="Turnover (avg)", average=True)
    plot_coverage_time_series(res.coverage, ax=axes[3, 1], title="Coverage")

    fig.suptitle(f"SingleFactorResult summary: {res.factor}", fontsize=14, y=0.995)
    return fig
