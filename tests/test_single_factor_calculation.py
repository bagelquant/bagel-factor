"""
Tests for the factors module.
"""

import unittest
import pandas as pd
from src.bagel_factor import FactorSort, FactorRegression


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

        # setup factor data(momentum (returns from t-6 month to t))
        self.factor_data = stock_returns
        self.stock_next_returns = stock_returns.shift(-1).dropna()

        # drop the last row make sure the factor_data and stock_next_returns have the same length
        self.factor_data = self.factor_data.iloc[:-1]
        self.factor = FactorSort(factor_data=self.factor_data, stock_next_returns=self.stock_next_returns, group_number=7)


    def test_factor_returns(self):
        print("\n=== test_factor.TestFactorSort.test_factor_returns ===")
        print(f"Factor returns:\n{self.factor.factor_next_returns}")
    

    def test_portfolio_next_returns(self):
        print("\n=== test_factor.TestFactorSort.test_portfolio_next_returns ===")
        print(f"Portfolio next returns:\n{self.factor.portfolio_next_returns}")


    def test_group_labels(self):
        print("\n=== test_factor.TestFactorSort.test_group_labels ===")
        print(f"Group labels:\n{self.factor.group_labels}")

        # count how many stocks in each group at each timestamp
        group_counts = self.factor.group_labels.apply(pd.Series.value_counts, axis=1).fillna(0).astype(int)
        print(f"Group counts at each timestamp:\n{group_counts}")
        # Assert that the sum of group counts equals the number of columns (stocks) at each timestamp
        for idx, row in group_counts.iterrows():
            self.assertEqual(row.sum(), self.factor_data.shape[1])

    def test_group_labels_range(self):
        """
        Test that group labels are within the expected range (1 to group_number).
        """
        min_label = self.factor.group_labels.min().min()
        max_label = self.factor.group_labels.max().max()
        self.assertGreaterEqual(min_label, 1)
        self.assertLessEqual(max_label, self.factor.group_number)

    def test_portfolio_next_returns_shape(self):
        """
        Test that portfolio_next_returns has the correct shape.
        """
        expected_shape = (self.factor_data.shape[0], self.factor.group_number)
        self.assertEqual(self.factor.portfolio_next_returns.shape, expected_shape)

    def test_factor_next_returns_length(self):
        """
        Test that factor_next_returns has the correct length (same as number of timestamps).
        """
        self.assertEqual(len(self.factor.factor_next_returns), self.factor_data.shape[0])

    def test_portfolio_next_returns_nan(self):
        """
        Test that there are no NaNs in portfolio_next_returns.
        """
        self.assertFalse(self.factor.portfolio_next_returns.isnull().values.any())

    def test_group_labels_no_nan(self):
        """
        Test that there are no NaNs in group_labels.
        """
        self.assertFalse(self.factor.group_labels.isnull().values.any())

    def test_factor_next_returns_not_nan(self):
        """
        Test that there are no NaNs in factor_next_returns.
        """
        self.assertFalse(pd.isnull(self.factor.factor_next_returns).any())

    def test_group_labels_unique_per_row(self):
        """
        Test that each group label appears at least once in each timestamp (row).
        """
        for idx, row in self.factor.group_labels.iterrows():
            unique_labels = set(row)
            for group in range(1, self.factor.group_number + 1):
                self.assertIn(group, unique_labels)

    def test_str_representation(self):
        """
        Test the __str__ method of FactorSort.
        """
        s = str(self.factor)
        self.assertIn("Unnamed Factor", s) 

    def test_factor_next_returns_ttest(self):
        """
        Test that the mean of factor_next_returns is significantly different from zero using a t-test.
        """
        t_stat, p_value = self.factor.t_test_factor_returns()
        print(f"T-test statistic: {t_stat}, p-value: {p_value}")
        self.assertIsInstance(t_stat, float)
        self.assertIsInstance(p_value, float)


class TestFactorRegression(unittest.TestCase):
    def setUp(self):
        # Test price data
        start_date = pd.Timestamp("2009-01-01")
        end_date = pd.Timestamp("2023-12-31")
        stock_returns = pd.read_csv("tests/test_stock_returns.csv", index_col=0, parse_dates=True).loc[start_date:end_date]
        stock_price = (stock_returns + 1).cumprod()  # convert returns to price
        stock_price = stock_price.resample("6ME").last()
        stock_returns = stock_price.pct_change().dropna()
        self.factor_data = stock_returns
        self.stock_next_returns = stock_returns.shift(-1).dropna()
        self.factor_data = self.factor_data.iloc[:-1]
        self.factor = FactorRegression(factor_data=self.factor_data, stock_next_returns=self.stock_next_returns)

    def test_factor_returns(self):
        """
        Test that factor_next_returns is calculated correctly.
        """
        print("\n=== test_factor.TestFactorRegression.test_factor_returns ===")
        print(f"Factor returns:\n{self.factor.factor_next_returns}")

    def test_residuals(self):
        """
        Test that residuals are calculated correctly.
        """
        print("\n=== test_factor.TestFactorRegression.test_residuals ===")
        print(f"Residuals:\n{self.factor.residuals}")

    def test_intercept_values(self):
        """
        Test that intercept_values are calculated correctly.
        """
        print("\n=== test_factor.TestFactorRegression.test_intercept_values ===")
        print(f"Intercept values:\n{self.factor.intercept_values}")


    def test_factor_next_returns_length(self):
        """
        Test that factor_next_returns has the correct length (same as number of timestamps).
        """
        self.assertEqual(len(self.factor.factor_next_returns), self.factor_data.shape[0])

    def test_residuals_shape(self):
        """
        Test that residuals DataFrame has the correct shape.
        """
        self.assertEqual(self.factor.residuals.shape, self.factor_data.shape)

    def test_intercept_values_length(self):
        """
        Test that intercept_values has the correct length (same as number of timestamps).
        """
        self.assertEqual(len(self.factor.intercept_values), self.factor_data.shape[0])

    def test_str_representation(self):
        s = str(self.factor)
        self.assertIn("Unnamed Factor", s)

    def test_factor_next_returns_ttest(self):
        """
        Test that the mean of factor_next_returns is significantly different from zero using a t-test.
        """
        t_stat, p_value = self.factor.t_test_factor_returns()
        print(f"T-test statistic: {t_stat}, p-value: {p_value}")
        self.assertIsInstance(t_stat, float)
        self.assertIsInstance(p_value, float)


if __name__ == "__main__":
    unittest.main()
