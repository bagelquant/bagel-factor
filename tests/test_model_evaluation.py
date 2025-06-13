"""
Tests for the factor model evaluation module.

Author: Yanzhong(Eric) Huang
"""

import pandas as pd
from pathlib import Path
from unittest import TestCase
import shutil
from src.bagel_factor import evaluate_model


class TestModelEvaluation(TestCase):
    def setUp(self):
        # Prepare test data similar to test_factors.py
        start_date = pd.Timestamp("2009-01-01")
        end_date = pd.Timestamp("2023-12-31")
        stock_returns = pd.read_csv("tests/test_stock_returns.csv", index_col=0, parse_dates=True).loc[
                        start_date:end_date]
        stock_price = (stock_returns + 1).cumprod()
        stock_price = stock_price.resample("6ME").last()
        stock_returns = stock_price.pct_change().dropna()

        # Create factor loadings: current returns(last 6 month), previous returns(6 months returns and skip 6 months)
        mom_1 = stock_returns.iloc[1:-1, :]  # remove first and last row to align with next returns and mom_2
        mom_2 = stock_returns.shift(1).dropna().iloc[:-1,
                :]  # shift by 1 to align with next returns and remove last row
        self.factor_loadings = {
            "mom_1": mom_1,
            "mom_2": mom_2
        }
        self.stock_next_returns = stock_returns.shift(-1).dropna().iloc[1:, :]  # shift by -1 to get next returns and
        # remove first row

        # create a directory for evaluation results
        self.output_path = Path("tests/tem_eval_model_output")
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Clean up the output directory after each test
        if self.output_path.exists():
            shutil.rmtree(self.output_path)

    def test_evaluate_model_creates_report(self):
        evaluate_model(self.factor_loadings, self.stock_next_returns, self.output_path)
        # Check that the markdown report is created
        md_file = self.output_path / "model_evaluation_results.md"
        self.assertTrue(md_file.exists(), "Model evaluation markdown report was not created.")
