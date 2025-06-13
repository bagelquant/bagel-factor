"""
Tests for the factor_evaluation module.
"""

import unittest
import shutil
import pandas as pd
from pathlib import Path
from src.bagel_factor import evaluate_factor


class TestFactorEvaluation(unittest.TestCase):
    def setUp(self):
        # Prepare test data similar to test_factors.py
        start_date = pd.Timestamp("2009-01-01")
        end_date = pd.Timestamp("2023-12-31")
        stock_returns = pd.read_csv("tests/test_stock_returns.csv", index_col=0, parse_dates=True).loc[start_date:end_date]
        stock_price = (stock_returns + 1).cumprod()
        stock_price = stock_price.resample("6ME").last()
        stock_returns = stock_price.pct_change().dropna()
        self.factor_data = stock_returns.iloc[:-1]
        self.stock_next_returns = stock_returns.shift(-1).dropna()
        self.factor_data = self.factor_data.iloc[:len(self.stock_next_returns)]

        # Create a temporary directory for output
        self.tmp_dir = Path("tests/tmp_eval_output")
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary output directory after each test
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_evaluate_factor_creates_all_outputs(self):
        factor_name = "UnitTestFactor"
        factor_description = "UnitTest Description"
        regression_methods = ["OLS", "WLS", "RLM"]
        intercept_options = [True, False]
        for method in regression_methods:
            for intercept in intercept_options:
                out_dir = self.tmp_dir / f"{method}_{intercept}"
                evaluate_factor(
                    factor_data=self.factor_data,
                    stock_next_returns=self.stock_next_returns,
                    output_path=out_dir,
                    sorting_group_num=5,
                    regression_method=method,  # type: ignore
                    regression_intercept=intercept,
                    factor_name=factor_name,
                    factor_description=factor_description
                )
                # Check markdown report
                md_file = out_dir / f"{factor_name}_evaluation.md"
                self.assertTrue(md_file.exists(), f"Markdown report missing for {method}, intercept={intercept}")
                # Check plots
                plots_dir = out_dir / "plots"
                for plot in [
                    "group_means.png", "ics.png", "accumulated_returns.png", "factor_next_returns_hist.png",
                    "ics_regression.png", "ics_pearson_hist_regression.png", "ics_spearman_hist_regression.png", "factor_next_returns_hist_regression.png"
                ]:
                    self.assertTrue((plots_dir / plot).exists(), f"Plot {plot} missing for {method}, intercept={intercept}")
                # Check data outputs
                data_dir = out_dir / "data"
                input_dir = data_dir / "input"
                for csv in [
                    "sort_group_portfolios_next_returns.csv", "sort_factor_next_returns.csv", "sort_ICs.csv",
                    "regression_factor_next_returns.csv", "regression_ICs.csv"
                ]:
                    self.assertTrue((data_dir / csv).exists(), f"Data output {csv} missing for {method}, intercept={intercept}")
                for csv in ["stock_next_returns.csv", "factor_data.csv"]:
                    self.assertTrue((input_dir / csv).exists(), f"Input data {csv} missing for {method}, intercept={intercept}")

if __name__ == "__main__":
    unittest.main()
