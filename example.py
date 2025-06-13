"""
Example usage of the bagel-factor package
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Literal
from time import perf_counter

from src.bagel_factor import evaluate_factor, evaluate_model

# Global parameters
TEST_DATA_CSV: Path = Path("tests/test_stock_returns.csv")
START_DATE: pd.Timestamp = pd.Timestamp("2009-01-01")
END_DATE: pd.Timestamp = pd.Timestamp("2023-12-31")
OUTPUT_DIR: Path = Path("example_report")
SINGLE_FACTOR_DIR: Path = OUTPUT_DIR / "single_factor"
MULTI_FACTOR_DIR: Path = OUTPUT_DIR / "multi_factor"
FACTOR_NAME: str = "ExampleFactor"
FACTOR_DESCRIPTION: str = "Example factor based on 6-month returns."
SORTING_GROUP_NUM: int = 5
REGRESSION_METHOD: Literal["OLS", "WLS", "RLM"] = "OLS"
REGRESSION_INTERCEPT: bool = True


def prepare_data() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    Prepare example factor and return data for single and multi-factor evaluation.

    :return: 
        factor_data (pd.DataFrame): Factor values for single factor evaluation.
        stock_next_returns (pd.DataFrame): Next period returns for single factor evaluation.
        factor_loadings (Dict[str, pd.DataFrame]): Dictionary of factor loadings for multi-factor evaluation.
        stock_next_returns_multi (pd.DataFrame): Next period returns for multi-factor evaluation.
    """
    stock_returns = pd.read_csv(TEST_DATA_CSV, index_col=0, parse_dates=True)
    stock_returns = stock_returns.loc[START_DATE:END_DATE]
    stock_price = (stock_returns + 1).cumprod()
    stock_price = stock_price.resample("6ME").last()
    stock_returns = stock_price.pct_change().dropna()
    # Single factor
    factor_data = stock_returns.iloc[:-1]
    stock_next_returns = stock_returns.shift(-1).dropna()
    factor_data = factor_data.iloc[:len(stock_next_returns)]
    # Multi-factor
    mom_1 = stock_returns.iloc[1:-1, :]
    mom_2 = stock_returns.shift(1).dropna().iloc[:-1, :]
    factor_loadings = {"mom_1": mom_1, "mom_2": mom_2}
    stock_next_returns_multi = stock_returns.shift(-1).dropna().iloc[1:, :]
    return factor_data, stock_next_returns, factor_loadings, stock_next_returns_multi


def run_single_factor_example(
    factor_data: pd.DataFrame,
    stock_next_returns: pd.DataFrame
) -> None:
    """
    Run single factor evaluation and save the report.

    :param factor_data: pd.DataFrame
        Factor values for single factor evaluation.
    :param stock_next_returns: pd.DataFrame
        Next period returns for single factor evaluation.
    :return: None
    """
    SINGLE_FACTOR_DIR.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    evaluate_factor(
        factor_data=factor_data,
        stock_next_returns=stock_next_returns,
        output_path=SINGLE_FACTOR_DIR,
        sorting_group_num=SORTING_GROUP_NUM,
        regression_method=REGRESSION_METHOD,
        regression_intercept=REGRESSION_INTERCEPT,
        factor_name=FACTOR_NAME,
        factor_description=FACTOR_DESCRIPTION
    )
    elapsed = perf_counter() - start
    print(f"Single factor evaluation report saved to: {SINGLE_FACTOR_DIR} (Elapsed: {elapsed:.2f}s)")


def run_multi_factor_example(
    factor_loadings: Dict[str, pd.DataFrame],
    stock_next_returns_multi: pd.DataFrame
) -> None:
    """
    Run multi-factor model evaluation and save the report.

    :param factor_loadings: Dict[str, pd.DataFrame]
        Dictionary of factor loadings for multi-factor evaluation.
    :param stock_next_returns_multi: pd.DataFrame
        Next period returns for multi-factor evaluation.
    :return: None
    """
    MULTI_FACTOR_DIR.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    evaluate_model(
        factor_loadings=factor_loadings,
        stock_next_returns=stock_next_returns_multi,
        output_path=MULTI_FACTOR_DIR
    )
    elapsed = perf_counter() - start
    print(f"Multi-factor model evaluation report saved to: {MULTI_FACTOR_DIR} (Elapsed: {elapsed:.2f}s)")


def main() -> None:
    """
    Run the example workflow for both single and multi-factor evaluation.

    :return: None
    """
    factor_data, stock_next_returns, factor_loadings, stock_next_returns_multi = prepare_data()
    run_single_factor_example(factor_data, stock_next_returns)
    run_multi_factor_example(factor_loadings, stock_next_returns_multi)


if __name__ == "__main__":
    main()
