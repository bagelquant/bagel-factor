"""
Factor model evaluation module.

Author: Yanzhong(Eric) Huang

Provides a `evaluate_model` function to generate a report of factor model evaluation results.

Input:

- `factor_loadings`: A dictionary where keys are factor names
and values are DataFrames containing factor loadings for each stock at each timestamp.
- `stock_next_returns`: A DataFrame containing the next period returns for each stock at each timestamp.
- `output_path`: A directory path where the evaluation results will be saved.
"""

import pandas as pd
from pathlib import Path
from typing import Annotated
from .factor_model import FactorModel


def evaluate_model(factor_loadings: dict[str, pd.DataFrame],
                   stock_next_returns: pd.DataFrame,
                   output_path: Annotated[Path, "Should be a directory to save evaluation results"]) -> None:
    """
    Evaluate the factor model and save the results to the specified output path.
    This function performs cross-sectional regression on the provided factor loadings and stock returns,
    and generates a report containing regression parameters and t-test results.

    :param factor_loadings: Dictionary of factor loadings with factor names as keys and DataFrames as values.
    :param stock_next_returns: DataFrame containing the next period returns for each stock at each timestamp.
    :param output_path: Directory path where the evaluation results will be saved.
    """
    # Ensure output_path is a Path object
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    # Initialize the FactorModel with the provided factor loadings and stock returns
    model = FactorModel(factor_loadings=factor_loadings, stock_next_returns=stock_next_returns)
    # Perform the evaluation
    regression_params = model.regression_params
    t_test_table = model.t_test_table

    # Save the results to a Markdown file
    result = f"## Factor Model Evaluation Results\n\n"
    result += "### T-Test Results\n\n"
    result += t_test_table.to_markdown() + "\n\n"
    result += "### Regression Parameters\n\n"
    result += regression_params.to_markdown() + "\n\n"

    # Write the results to a Markdown file
    output_file = output_path / "model_evaluation_results.md"
    with open(output_file, "w") as f:
        f.write(result)



