"""
Tests for the factors module.
"""

import unittest
import pandas as pd
from src.bagel_factor import FactorSort


class TestFactorSort(unittest.TestCase):
    def setUp(self):
        # Test price data
        start_date = pd.Timestamp("2009-01-01")
        end_date = pd.Timestamp("2023-12-31")
        stock_returns = pd.read_csv("tests/test_stock_returns.csv", index_col=0, parse_dates=True).loc[start_date:end_date]
        stock_price = (stock_returns + 1).cumprod()  # convert returns to price

        # resample to 6-month frequency
        stock_price = stock_price.resample("6ME").last()
        stock_returns = stock_price.pct_change().dropna()

        # setup factor data(momentum (returns from t-6 monthe to t))
        self.factor_data = stock_returns
        self.stock_next_returns = stock_returns.shift(-1).dropna()

        # drop the last row make sure the factor_data and stock_next_returns have the same length
        self.factor_data = self.factor_data.iloc[:-1]
        self.factor = FactorSort(factor_data=self.factor_data, stock_next_returns=self.stock_next_returns)


    def test_factor_returns(self):
        print("\n=== test_factor.TestFactorSort.test_factor_returns ===")
        print(f"Factor returns:\n{self.factor.factor_next_returns}")
    

    def test_portfolio_next_returns(self):
        print("\n=== test_factor.TestFactorSort.test_portfolio_next_returns ===")
        print(f"Portfolio next returns:\n{self.factor.portfolio_next_returns}")

