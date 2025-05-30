"""
Factor evaluation module for Bagel Factor.

Author: Yanzhong(Eric) Huang

Provides a comprehensive, well-documented,
and organized solution for evaluating single factors using both sorting and regression methods.
Generates a Markdown report with key highlights, detailed evaluation,
and saves all plots in a dedicated subfolder.
"""

import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Annotated, Optional
from .single_factor_calculation import FactorSort, FactorRegression


def evaluate_factor(
    factor_data: pd.DataFrame,
    stock_next_returns: pd.DataFrame,
    output_path: Annotated[Path, "Should be a directory to save evaluation results"],
    sorting_group_num: int = 10,
    factor_name: str = "Unnamed Factor",
    factor_description: str = "No description provided"
) -> None:
    """
    Evaluate a single factor using both sorting and regression methods.

    :param factor_data: DataFrame containing factor data with date index and ticker columns.
    :param stock_next_returns: DataFrame of next period returns, indexed by date and columns as tickers.
    :param output_path: Directory to save the evaluation results and plots.
    :param sorting_group_num: Number of groups for sorting method (default is 10).
    :param factor_name: Name of the factor (default is "Unnamed Factor").
    :param factor_description: Description of the factor (default is "No description provided").
    :returns: None
    """
    # Ensure output directory exists
    if output_path.exists():
        if not output_path.is_dir():
            raise ValueError("output_path must be a directory")
    else:
        output_path.mkdir(parents=True, exist_ok=True)

    # Prepare plots subfolder
    plots_path = output_path / "plots"
    plots_path.mkdir(parents=True, exist_ok=True)

    # --- FactorSort Evaluation ---
    factor_sort = FactorSort(
        factor_data=factor_data,
        stock_next_returns=stock_next_returns,
        name=factor_name,
        description=factor_description,
        group_number=sorting_group_num
    )
    sort_mean = factor_sort.factor_next_returns.mean()
    sort_std = factor_sort.factor_next_returns.std()
    sort_ic, sort_icir = _calculate_sort_ics(factor_sort)

    # --- FactorRegression Evaluation ---
    factor_regression = FactorRegression(
        factor_data=factor_data,
        stock_next_returns=stock_next_returns,
        name=factor_name,
        description=factor_description
    )
    reg_mean = factor_regression.factor_next_returns.mean()
    reg_std = factor_regression.factor_next_returns.std()
    reg_ic, reg_icir, reg_ics_df = _calculate_regression_ics(factor_regression)

    # --- Highlight Table ---
    highlight_table = pd.DataFrame({
        "Method": ["Sort", "Regression"],
        "Factor Mean": [sort_mean, reg_mean],
        "Factor Std": [sort_std, reg_std],
        "IC (mean)": [sort_ic, reg_ic],
        "ICIR": [sort_icir, reg_icir],
    })

    # --- Markdown Report ---
    results = f"# {factor_name} Evaluation Results\n"
    results += f"\nDescription: {factor_description}\n\n"
    results += "## Highlight\n\n" + highlight_table.to_markdown(index=False, floatfmt=".4g") + "\n\n"
    results += (
        "**Interpretation:**  \n\n"
        "- IC > 0.15: strong predictive power\n"
        "- ICIR > 0.5: good consistency\n"
        "- ICIR > 1.0: very strong and stable factor.\n\n"
    )
    results += _evaluation_factor_sort(factor_sort, plots_path)
    results += _evaluation_factor_regression(factor_regression, plots_path, reg_ics_df)

    # Save results
    results_path = output_path / f"{factor_name}_evaluation.md"
    with results_path.open("w") as f:
        f.write(results)

    # Save input and output data for further analysis
    data_dir = output_path / "data"
    input_dir = data_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    # Save input data
    stock_next_returns.to_csv(input_dir / "stock_next_returns.csv")
    factor_data.to_csv(input_dir / "factor_data.csv")
    # Save sort method outputs
    factor_sort.portfolio_next_returns.to_csv(data_dir / "sort_group_portfolios_next_returns.csv")
    factor_sort.factor_next_returns.to_csv(data_dir / "sort_factor_next_returns.csv")
    _calculate_ics(factor_sort.portfolio_next_returns).to_csv(data_dir / "sort_ICs.csv")
    # Save regression method outputs
    factor_regression.factor_next_returns.to_csv(data_dir / "regression_factor_next_returns.csv")
    reg_ics_df.to_csv(data_dir / "regression_ICs.csv")


def _calculate_sort_ics(factor_sort: FactorSort) -> tuple:
    """
    Calculate mean IC and ICIR for FactorSort method.

    :param factor_sort: FactorSort instance.
    :returns: Tuple of (IC mean, ICIR).
    """
    ic_s = _calculate_ics(factor_sort.portfolio_next_returns)
    ic_mean = ic_s.mean().mean()
    icir = ic_mean / ic_s.std().mean()
    return ic_mean, icir


def _calculate_regression_ics(factor_regression: FactorRegression):
    """
    Calculate mean IC and ICIR for FactorRegression method.

    :param factor_regression: FactorRegression instance.
    :returns: Tuple of (IC mean, ICIR, ICs DataFrame).
    """
    reg_ics_df = _compute_regression_ics_df(factor_regression)
    ic_mean = reg_ics_df.mean().mean()
    icir = ic_mean / reg_ics_df.std().mean()
    return ic_mean, icir, reg_ics_df


def _compute_regression_ics_df(factor_regression: FactorRegression) -> pd.DataFrame:
    """
    Compute the regression ICs DataFrame (pearson, spearman) for each date.

    :param factor_regression: FactorRegression instance.
    :returns: DataFrame with pearson and spearman ICs for each date.
    """
    factor_next_returns = factor_regression.factor_next_returns
    reg_ics_df = pd.DataFrame(index=factor_next_returns.index, columns=["pearson", "spearman"])
    for date in factor_next_returns.index:
        x = factor_regression.factor_data.loc[date]
        y = factor_regression.stock_next_returns.loc[date]
        mask = x.notna() & y.notna()
        if mask.sum() < 2:
            reg_ics_df.loc[date, "pearson"] = float('nan')
            reg_ics_df.loc[date, "spearman"] = float('nan')
        else:
            reg_ics_df.loc[date, "pearson"] = x[mask].corr(y[mask], method="pearson")
            reg_ics_df.loc[date, "spearman"] = x[mask].corr(y[mask], method="spearman")
    return reg_ics_df


def _calculate_ics(portfolio_next_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ICs (Information Coefficient) for each timestamp.

    :param portfolio_next_returns: DataFrame of portfolio next returns by group.
    :returns: DataFrame with pearson and spearman ICs for each date.
    """
    pearson_ic = pd.Series(index=portfolio_next_returns.index, name="pearson_ic")
    spearman_ic = pd.Series(index=portfolio_next_returns.index, name="spearman_ic")
    for date in portfolio_next_returns.index:
        pearson_ic[date] = portfolio_next_returns.loc[date].corr(portfolio_next_returns.columns.to_series(), method="pearson")
        spearman_ic[date] = portfolio_next_returns.loc[date].corr(portfolio_next_returns.columns.to_series(), method="spearman")
    return pd.DataFrame({"pearson": pearson_ic, "spearman": spearman_ic})


def _icir_table(ic_s: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ICIR (mean/std) for each IC type.

    :param ic_s: DataFrame of ICs (pearson, spearman).
    :returns: DataFrame with mean, std, and ICIR for each IC type.
    """
    ic_icir_table = pd.DataFrame(columns=["ICs mean", "std", "ICIR"])
    ic_icir_table["ICs mean"] = ic_s.mean()
    ic_icir_table["std"] = ic_s.std()
    ic_icir_table["ICIR"] = ic_icir_table["ICs mean"] / ic_icir_table["std"]
    return ic_icir_table


def _accumulated_returns(*returns_series) -> pd.DataFrame:
    """
    Calculate accumulated (cumulative) returns for given series.

    :param returns_series: One or more Series of returns.
    :returns: DataFrame with each series as a column of cumulative returns.
    """
    returns = pd.concat(returns_series, axis=1)
    accumulated = (returns + 1).cumprod() - 1
    return accumulated


def _group_statistics_table(portfolio_next_returns: pd.DataFrame, factor_next_returns: pd.Series) -> pd.DataFrame:
    """
    Calculate statistics for each group and the high-low factor return.

    :param portfolio_next_returns: DataFrame of group returns.
    :param factor_next_returns: Series of high-low factor returns.
    :returns: DataFrame with n_t, mean, std, t-stat, p-value for each group and H-L.
    """
    group_result_table = pd.DataFrame(columns=["n_t", "mean", "std", "t_stat", "p_value"], index=portfolio_next_returns.columns)
    for group in portfolio_next_returns.columns:
        group_result_table.loc[group, "n_t"] = portfolio_next_returns[group].count()
        group_result_table.loc[group, "mean"] = portfolio_next_returns[group].mean()
        group_result_table.loc[group, "std"] = portfolio_next_returns[group].std()
        t_stat, p_value = stats.ttest_1samp(portfolio_next_returns[group], 0)
        group_result_table.loc[group, "t_stat"] = t_stat  # type: ignore
        group_result_table.loc[group, "p_value"] = p_value  # type: ignore
    # Factor statistics
    t_stat, p_value = stats.ttest_1samp(factor_next_returns, 0)
    group_result_table.loc["H-L", "n_t"] = int(factor_next_returns.count())
    group_result_table.loc["H-L", "mean"] = factor_next_returns.mean()
    group_result_table.loc["H-L", "std"] = factor_next_returns.std()
    group_result_table.loc["H-L", "t_stat"] = t_stat  # type: ignore
    group_result_table.loc["H-L", "p_value"] = p_value  # type: ignore
    return group_result_table


def _plot_group_means(group_result_table: pd.DataFrame, output_path: Path, filename: str = "group_means.png"):
    """
    Plot mean returns by group and save to file.

    :param group_result_table: DataFrame with group statistics.
    :param output_path: Path to save the plot.
    :param filename: Filename for the plot image.
    :returns: None
    """
    ax = group_result_table.loc[group_result_table.index != "H-L", "mean"].plot(
        kind="bar", title="Mean Returns by Group", ylabel="Mean Return", xlabel="Group", figsize=(10, 6))
    fig = ax.figure
    fig.savefig(output_path / filename)  # type: ignore
    plt.close(fig)  # type: ignore


def _plot_ics(ic_s: pd.DataFrame, output_path: Path, filename: str = "ics.png"):
    """
    Plot ICs over time and save to file.

    :param ic_s: DataFrame of ICs (pearson, spearman).
    :param output_path: Path to save the plot.
    :param filename: Filename for the plot image.
    :returns: None
    """
    ax = ic_s.plot(title="ICs over Time", ylabel="IC", xlabel="Date", figsize=(10, 6))
    fig = ax.figure
    fig.savefig(output_path / filename)  # type: ignore
    plt.close(fig)  # type: ignore


def _plot_accumulated_returns(accumulated_returns: pd.DataFrame, output_path: Path, filename: str = "accumulated_returns.png"):
    """
    Plot cumulative returns and save to file.

    :param accumulated_returns: DataFrame of cumulative returns.
    :param output_path: Path to save the plot.
    :param filename: Filename for the plot image.
    :returns: None
    """
    ax = accumulated_returns.plot(title="Cumulative Returns", ylabel="Cumulative Return", xlabel="Date", figsize=(10, 6), grid=True)
    fig = ax.figure
    fig.savefig(output_path / filename)  # type: ignore
    plt.close(fig)  # type: ignore


def _plot_histogram(series: pd.Series, output_path: Path, filename: str = "hist.png", title: str = "Factor Next Returns Distribution"):
    """
    Plot histogram of a series and save to file.

    :param series: Series to plot.
    :param output_path: Path to save the plot.
    :param filename: Filename for the plot image.
    :param title: Title for the plot.
    :returns: None
    """
    ax = series.plot(kind="hist", title=title, xlabel="Next Returns", ylabel="Frequency", figsize=(10, 6), grid=True)
    fig = ax.figure
    fig.savefig(output_path / filename)  # type: ignore
    plt.close(fig)  # type: ignore


def _evaluation_factor_sort(factor_sort: FactorSort, output_path: Path) -> str:
    """
    Evaluate FactorSort and return markdown summary.

    :param factor_sort: FactorSort instance.
    :param output_path: Path to save plots.
    :returns: Markdown summary string for FactorSort evaluation.
    """
    factor_next_returns = factor_sort.factor_next_returns
    portfolio_next_returns = factor_sort.portfolio_next_returns
    # Table of each group + factor returns
    group_table = _group_statistics_table(portfolio_next_returns, factor_next_returns)
    # ic_s and ICIR
    ic_s = _calculate_ics(portfolio_next_returns)
    ic_ir = _icir_table(ic_s)
    # Accumulated returns
    acc_returns = _accumulated_returns(portfolio_next_returns.iloc[:, 0], portfolio_next_returns.iloc[:, -1], factor_next_returns)
    acc_returns.columns = ["Low", "High", "H-L"]
    # Plots
    _plot_group_means(group_table, output_path)
    _plot_ics(ic_s, output_path)
    _plot_accumulated_returns(acc_returns, output_path)
    _plot_histogram(factor_next_returns, output_path, "factor_next_returns_hist.png")
    # Markdown summary
    md = "## FactorSort Evaluation\n\n"
    md += "### Group Statistics\n\n" + group_table.to_markdown() + "\n\n"
    md += "![Mean Returns by Group](plots/group_means.png)\n\n"
    md += "### ic_s and ICIR\n\n" + ic_s.describe().to_markdown() + "\n\n"
    md += "ICIR Table:\n\n" + ic_ir.to_markdown() + "\n\n"
    md += "![ic_s over Time](plots/ics.png)\n\n"
    md += "### Accumulated Returns\n\n" + acc_returns.tail().to_markdown() + "\n\n"
    md += "![Cumulative Returns](plots/accumulated_returns.png)\n\n"
    md += "### Histogram of Factor Returns\n\n"
    md += "![Factor Next Returns Distribution](plots/factor_next_returns_hist.png)\n\n"
    return md


def _evaluation_factor_regression(
    factor_regression: FactorRegression,
    output_path: Path,
    reg_ics_df: Optional[pd.DataFrame] = None
) -> str:
    """
    Evaluate FactorRegression and return markdown summary.

    :param factor_regression: FactorRegression instance.
    :param output_path: Path to save plots.
    :param reg_ics_df: (Optional) DataFrame of regression ic_s to avoid recomputation.
    :returns: Markdown summary string for FactorRegression evaluation.
    """
    factor_next_returns = factor_regression.factor_next_returns
    # Use provided ic_s if available, else compute
    if reg_ics_df is None:
        reg_ics_df = _compute_regression_ics_df(factor_regression)
    ic_s = reg_ics_df
    icir = pd.DataFrame({
        "ic_s mean": ic_s.mean(),
        "std": ic_s.std(),
        "ICIR": ic_s.mean() / ic_s.std()
    })
    # t-test for factor_next_returns
    t_stat, p_value = stats.ttest_1samp(factor_next_returns.dropna(), 0)
    # Plots (regression-specific names)
    _plot_ics(ic_s, output_path, "ics_regression.png")
    _plot_histogram(ic_s["pearson"].dropna(), output_path, "ics_pearson_hist_regression.png", title="Pearson ic_s Distribution (Regression)")
    _plot_histogram(ic_s["spearman"].dropna(), output_path, "ics_spearman_hist_regression.png", title="Spearman ic_s Distribution (Regression)")
    _plot_histogram(factor_next_returns, output_path, "factor_next_returns_hist_regression.png", title="Factor Next Returns Distribution (Regression)")
    # Markdown summary
    md = "## FactorRegression Evaluation\n\n"
    md += "### ic_s and ICIR for Regression Method\n\n" + ic_s.describe().to_markdown() + "\n\n"
    md += "ICIR Table:\n\n" + icir.to_markdown() + "\n\n"
    md += "![ic_s over Time](plots/ics_regression.png)\n\n"
    md += "### ic_s Histogram (Pearson)\n\n"
    md += "![Pearson ic_s Distribution](plots/ics_pearson_hist_regression.png)\n\n"
    md += "### ic_s Histogram (Spearman)\n\n"
    md += "![Spearman ic_s Distribution](plots/ics_spearman_hist_regression.png)\n\n"
    md += f"### t-test for factor_next_returns\n\nT-statistic: {t_stat:.4f}, p-value: {p_value:.4g}\n\n"
    md += "### Histogram of Factor Returns (Regression)\n\n"
    md += "![Factor Next Returns Distribution (Regression)](plots/factor_next_returns_hist_regression.png)\n"
    return md
