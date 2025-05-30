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

    def test_evaluate_factor_creates_md_file(self):
        factor_name = "UnitTestFactor"
        factor_description = "UnitTest Description"
        evaluate_factor(
            factor_data=self.factor_data,
            stock_next_returns=self.stock_next_returns,
            output_path=self.tmp_dir,
            sorting_group_num=5,
            factor_name=factor_name,
            factor_description=factor_description
        )

if __name__ == "__main__":
    unittest.main()
