import unittest
import pandas as pd
import numpy as np
from src.bagel_factor.metrics import ic

class TestInformationCoefficient(unittest.TestCase):
    def setUp(self):
        # 3 dates, 4 tickers
        dates = pd.date_range('2023-01-01', periods=3)
        tickers = ['A', 'B', 'C', 'D']
        idx = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        # Factor and returns are perfectly correlated
        self.factor = pd.Series(np.tile([1, 2, 3, 4], 3), index=idx, name='factor')
        self.returns = pd.Series(np.tile([10, 20, 30, 40], 3), index=idx, name='returns')
        # Add a constant group for edge case
        self.factor_const = self.factor.copy()
        self.factor_const.loc[(dates[0], slice(None))] = 5.0
        self.returns_const = self.returns.copy()
        self.returns_const.loc[(dates[1], slice(None))] = 7.0
        # Add NaNs
        self.factor_nan = self.factor.copy()
        self.factor_nan.loc[(dates[2], 'A')] = np.nan
        self.returns_nan = self.returns.copy()
        self.returns_nan.loc[(dates[2], 'B')] = np.nan

    def test_ic_pearson_perfect(self):
        ic_series = ic.information_coefficient(self.factor, self.returns, method='pearson')
        self.assertTrue(np.allclose(ic_series, 1.0, equal_nan=False))

    def test_ic_spearman_perfect(self):
        ic_series = ic.information_coefficient(self.factor, self.returns, method='spearman')
        self.assertTrue(np.allclose(ic_series, 1.0, equal_nan=False))

    def test_ic_with_constant_group(self):
        ic_series = ic.information_coefficient(self.factor_const, self.returns, method='pearson')
        self.assertTrue(np.isnan(ic_series.iloc[0]))  # First date is constant
        self.assertFalse(np.isnan(ic_series.iloc[1:]).any())
        ic_series2 = ic.information_coefficient(self.factor, self.returns_const, method='pearson')
        self.assertTrue(np.isnan(ic_series2.iloc[1]))  # Second date is constant

    def test_ic_with_nan(self):
        ic_series = ic.information_coefficient(self.factor_nan, self.returns_nan, method='pearson')
        self.assertEqual(len(ic_series), 3)
        self.assertFalse(ic_series.isnull().all())

    def test_index_mismatch(self):
        with self.assertRaises(ValueError):
            ic.information_coefficient(self.factor, self.returns.drop(self.returns.index[0]))

    def test_invalid_method(self):
        with self.assertRaises(ValueError):
            ic.information_coefficient(self.factor, self.returns, method='kendall')  # type: ignore

class TestInformationCoefficientUsingRealData(unittest.TestCase):

    def setUp(self):
        self.factor = pd.read_csv(
            'tests/test_data/roe.csv',
            parse_dates=['date'],
            index_col=['date', 'ticker']
        )['roe'].sort_index()
            
        price = pd.read_csv(
            'tests/test_data/price.csv',
            usecols=['date', 'ticker', 'adj_close'],
            parse_dates=['date'],
            index_col=['date', 'ticker']
        )['adj_close'].sort_index()
        # Drop duplicate indices
        price = price[~price.index.duplicated(keep='first')]
        self.factor = self.factor[~self.factor.index.duplicated(keep='first')]

        returns_20d = price.groupby(level='ticker').pct_change(20, fill_method=None)
        self.future_returns = returns_20d.shift(-20).dropna()  # Future returns

        # Align indices
        self.factor = self.factor.reindex(self.future_returns.index)
        self.factor = self.factor.groupby(level='ticker').ffill()


    def test_ic_pearson_perfect(self):
        ic_series = ic.information_coefficient(self.factor, self.future_returns, method='pearson')

if __name__ == '__main__':
    unittest.main()
