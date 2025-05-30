"""
Tests for the factor_model module.
"""

import unittest
import pandas as pd
from src.bagel_factor import FactorModel


class TestFactorEvaluation(unittest.TestCase):

    def setUp(self):
        # Prepare test data similar to test_factors.py
        start_date = pd.Timestamp("2009-01-01")
        end_date = pd.Timestamp("2023-12-31")
        stock_returns = pd.read_csv("tests/test_stock_returns.csv", index_col=0, parse_dates=True).loc[start_date:end_date]
        stock_price = (stock_returns + 1).cumprod()
        stock_price = stock_price.resample("6ME").last()
        stock_returns = stock_price.pct_change().dropna()

        # Create factor loadings: current returns(last 6 month), previous returns(6 months returns and skip 6 months)
        mom_1 = stock_returns.iloc[1:-1, :]  # remove first and last row to align with next returns and mom_2
        mom_2 = stock_returns.shift(1).dropna().iloc[:-1, :]  # shift by 1 to align with next returns and remove last row
        self.factor_loadings = {
            "mom_1": mom_1,
            "mom_2": mom_2
        }
        self.stock_next_returns = stock_returns.shift(-1).dropna().iloc[1:, :]  # shift by -1 to get next returns and remove first row

        self.factor_model = FactorModel(
            factor_loadings=self.factor_loadings,
            stock_next_returns=self.stock_next_returns,
            rf=0.02
        )
    
    def test_cross_sectional_regression(self):
        """
        Test the cross-sectional regression for a specific date.
        """
        date = self.stock_next_returns.index[0]
        result = self.factor_model._cross_sectional_regression(date)
        print(f"\n===== Cross-Sectional Regression for {date} =====")
        print(result.summary())
    
    def test_regression_params(self):
        """
        Test the regression parameters DataFrame structure.
        """
        print("\n===== Regression Parameters =====")
        print(self.factor_model.regression_params)
    
    def test_t_test_table(self):
        """
        Test the t-test table structure.
        """
        print("\n===== T-Test Table =====")
        print(self.factor_model.t_test_table)
        

if __name__ == "__main__":
    unittest.main()
