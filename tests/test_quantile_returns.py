import unittest
import pandas as pd
import numpy as np
from src.bagel_factor import quantile_returns, quantile_spread

class TestQuantileReturns(unittest.TestCase):
    def setUp(self):
        # 3 dates, 6 tickers
        dates = pd.date_range('2023-01-01', periods=3)
        tickers = ['A', 'B', 'C', 'D', 'E', 'F']
        idx = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        # Factor: 1-6 repeated for each date
        self.factor = pd.Series(np.tile(np.arange(1, 7), 3), index=idx, name='factor')
        # Returns: 10-60 repeated for each date
        self.future_returns = pd.Series(np.tile(np.arange(10, 70, 10), 3), index=idx, name='returns')
        # Constant factor for first date
        self.factor_const = self.factor.copy()
        self.factor_const.loc[(dates[0], slice(None))] = 5.0
        # NaN in returns for last date
        self.returns_nan = self.future_returns.copy()
        self.returns_nan.loc[(dates[2], 'A')] = np.nan

    def test_quantile_returns_basic(self):
        qrets = quantile_returns(self.factor, self.future_returns, n_quantiles=3)
        self.assertEqual(qrets.shape, (2, 3))
        # For perfect monotonic, each quantile should have 2 stocks per date
        for d in qrets.index:
            self.assertFalse(qrets.loc[d].isnull().any())
            self.assertTrue(np.allclose(qrets.loc[d].values, [15, 35, 55]))

    def test_quantile_returns_custom_labels(self):
        qrets = quantile_returns(self.factor, self.future_returns, n_quantiles=2, quantile_labels=['low', 'high'])
        self.assertListEqual(list(qrets.columns), ['low', 'high'])

    def test_quantile_returns_constant(self):
        qrets = quantile_returns(self.factor_const, self.future_returns, n_quantiles=3)
        # All assigned to middle quantile for first date
        self.assertTrue((qrets.loc[qrets.index[0]].dropna().index == 2).all())

    def test_quantile_returns_nan(self):
        qrets = quantile_returns(self.factor, self.returns_nan, n_quantiles=3)

    def test_quantile_spread(self):
        qrets = quantile_returns(self.factor, self.future_returns, n_quantiles=3)
        spread = quantile_spread(qrets)
        self.assertTrue(np.allclose(spread, 40))

    def test_index_mismatch(self):
        with self.assertRaises(ValueError):
            quantile_returns(self.factor, self.future_returns.drop(self.future_returns.index[0]))

if __name__ == '__main__':
    unittest.main()
