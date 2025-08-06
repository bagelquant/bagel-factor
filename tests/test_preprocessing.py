import unittest
import pandas as pd
import numpy as np
from src.bagel_factor import preprocessing

class TestPreprocessingMethods(unittest.TestCase):
    def setUp(self):
        # Create a MultiIndex Series: 3 dates, 4 tickers
        dates = pd.date_range('2023-01-01', periods=3)
        tickers = ['A', 'B', 'C', 'D']
        idx = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        values = np.arange(12, dtype=float)
        self.s = pd.Series(values, index=idx)
        # Add a constant group for minmax edge case
        self.s_const = self.s.copy()
        self.s_const.loc[(dates[0], slice(None))] = 5.0

    def test_cross_sectional_zscore(self):
        z = preprocessing.cross_sectional_zscore(self.s)
        for d in self.s.index.get_level_values('date').unique():
            group = z.loc[d]
            self.assertAlmostEqual(group.mean(), 0, places=7)
            self.assertAlmostEqual(group.std(ddof=0), 1, places=7)

    def test_cross_sectional_minmax(self):
        mm = preprocessing.cross_sectional_minmax(self.s)
        for d in self.s.index.get_level_values('date').unique():
            group = mm.loc[d]
            self.assertAlmostEqual(group.min(), 0, places=7)
            self.assertAlmostEqual(group.max(), 1, places=7)
        # Constant group should be 0.0
        mm_const = preprocessing.cross_sectional_minmax(self.s_const)
        self.assertTrue((mm_const.loc[self.s.index.get_level_values('date')[0]] == 0.0).all())

    def test_cross_sectional_rank(self):
        # Ascending, dense
        r = preprocessing.cross_sectional_rank(self.s, method='dense', ascending=True)
        for d in self.s.index.get_level_values('date').unique():
            orig = self.s.loc[d]
            group = r.loc[d]
            expected = orig.rank(method='dense', ascending=True)
            pd.testing.assert_series_equal(group, expected)
        # Descending, min
        r_desc = preprocessing.cross_sectional_rank(self.s, method='min', ascending=False)
        for d in self.s.index.get_level_values('date').unique():
            orig = self.s.loc[d]
            group = r_desc.loc[d]
            expected = orig.rank(method='min', ascending=False)
            pd.testing.assert_series_equal(group, expected)

    def test_cross_sectional_winsorize(self):
        # Add outliers
        s_out = self.s.copy()
        s_out.loc[(self.s.index.get_level_values('date')[0], 'A')] = 1000
        w = preprocessing.cross_sectional_winsorize(s_out, lower=0.1, upper=0.9)
        for d in s_out.index.get_level_values('date').unique():
            group = s_out.loc[d]
            wgroup = w.loc[d]
            lower_val = group.quantile(0.1)
            upper_val = group.quantile(0.9)
            self.assertTrue((wgroup >= lower_val - 1e-8).all())
            self.assertTrue((wgroup <= upper_val + 1e-8).all())

    def test_preprocessingmethod_type(self):
        # All methods should be valid PreprocessingMethod
        for fn in [preprocessing.cross_sectional_zscore,
                   preprocessing.cross_sectional_minmax,
                   lambda s: preprocessing.cross_sectional_rank(s, method='dense'),
                   preprocessing.cross_sectional_winsorize]:
            self.assertTrue(callable(fn))
            out = fn(self.s)
            self.assertIsInstance(out, pd.Series)
            self.assertTrue(out.index.equals(self.s.index))

if __name__ == '__main__':
    unittest.main()
