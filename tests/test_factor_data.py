import unittest
import pandas as pd
from src.bagel_factor.data_handling.factor_data import FactorData, create_factor_data_from_df


class TestFactorData(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range('2023-01-01', periods=3)
        tickers = ['A', 'B']
        data = pd.DataFrame(
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
            index=dates, columns=tickers
        )
        self.df = data
        self.series: pd.Series = data.stack()  # type: ignore
        self.series.index.names = ['date', 'ticker']
        self.metadata = {'source': 'test'}
        self.factor_name = 'test_factor'
        self.fd = FactorData(factor_data=self.series, metadata=self.metadata, factor_name=self.factor_name)

    def test_check_format_valid(self):
        # Should not raise
        self.fd._check_format()

    def test_check_format_invalid(self):
        with self.assertRaises(ValueError):
            FactorData(factor_data=pd.Series([1,2,3]), metadata={}, factor_name='bad')

    def test_post_init_sort_and_name(self):
        fd = FactorData(factor_data=self.series[::-1], metadata=self.metadata, factor_name='zzz')
        self.assertEqual(fd.factor_data.name, 'zzz')
        self.assertTrue(fd.factor_data.index.is_monotonic_increasing)

    def test_dropna(self):
        s = self.series.copy()
        s.iloc[0] = None
        fd = FactorData(factor_data=s, metadata=self.metadata, factor_name=self.factor_name)
        dropped = fd.dropna()
        self.assertFalse(dropped.factor_data.isnull().any())
        self.assertEqual(dropped.factor_name, self.factor_name)

    def test_filter_by_universe(self):
        mask = self.series > 2
        filtered = self.fd.filter_by_universe(mask)
        self.assertTrue((filtered.factor_data > 2).all())
        self.assertEqual(filtered.factor_name, self.factor_name)

    def test_align_with(self):
        # Align with a subset
        idx = self.series.index[:2]
        other = FactorData(factor_data=self.series.loc[idx], metadata=self.metadata, factor_name=self.factor_name)
        aligned = self.fd.is_aligned(other)
        self.assertTrue(aligned)

    def test_standardize(self):
        def dummy_method(s):
            return (s - s.mean()) / s.std()
        std_fd = self.fd.standardize(dummy_method)
        self.assertAlmostEqual(std_fd.factor_data.mean(), 0, places=7)
        self.assertIn('preprocessing_method', std_fd.metadata)

    def test_to_series_and_to_frame(self):
        s = self.fd.to_series()
        f = self.fd.to_frame()
        self.assertTrue(isinstance(s, pd.Series))
        self.assertTrue(isinstance(f, pd.DataFrame))
        self.assertEqual(f.columns[0], self.factor_name)

    def test_to_dict_and_from_dict(self):
        d = self.fd.to_dict()
        fd2 = FactorData.from_dict(d)
        pd.testing.assert_series_equal(fd2.factor_data, self.fd.factor_data)
        self.assertEqual(fd2.metadata, self.fd.metadata)
        self.assertEqual(fd2.factor_name, self.fd.factor_name)

    def test_repr_and_str(self):
        r = repr(self.fd)
        s = str(self.fd)
        self.assertEqual(r, s)

    def test_properties(self):
        self.assertEqual(self.fd.start_date, self.df.index.min())
        self.assertEqual(self.fd.end_date, self.df.index.max())
        self.assertEqual(self.fd.shape, self.series.shape)
        self.assertTrue(set(self.fd.tickers) == set(self.df.columns))

class TestCreateFactorDataFromDf(unittest.TestCase):
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=2)
        self.tickers = ['X', 'Y']
        self.df = pd.DataFrame(
            [[10, 20], [30, 40]],
            index=self.dates, columns=self.tickers
        )
        self.meta = {'foo': 'bar'}

    def test_valid(self):
        fd = create_factor_data_from_df(self.df, metadata=self.meta, factor_name='abc')
        self.assertIsInstance(fd, FactorData)
        self.assertEqual(fd.factor_name, 'abc')
        self.assertEqual(fd.metadata, self.meta)
        self.assertTrue(isinstance(fd.factor_data, pd.Series))
        self.assertEqual(fd.factor_data.name, 'abc')
        self.assertEqual(fd.factor_data.index.names, ['date', 'ticker'])

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            create_factor_data_from_df([1,2,3])  # type: ignore
        with self.assertRaises(ValueError):
            create_factor_data_from_df(pd.DataFrame(), metadata=self.meta)
        bad_idx = pd.DataFrame([[1]], index=[1], columns=['A'])
        with self.assertRaises(ValueError):
            create_factor_data_from_df(bad_idx)

if __name__ == '__main__':
    unittest.main()
