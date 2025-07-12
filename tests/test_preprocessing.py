import unittest
import json
import pandas as pd
from datetime import datetime

from src.bagel_factor import get_engine, read_mysql
from src.bagel_factor import standardize, z_score, min_max, robust
from src.bagel_factor import impute_missing, fill_mean, fill_median, fill_zero
from src.bagel_factor import handle_outliers, clip_zscore, clip_iqr


class TestMissingDataImputation(unittest.TestCase):

    def setUp(self) -> None:
        self.data = pd.DataFrame({
            'date': ['2021-01-01', '2021-01-01', '2021-01-02', '2021-01-02'],
            'ticker': ['A', 'B', 'A', 'B'],
            'price': [10, None, 15, None],
            'volume': [100, 200, None, 400]
        })

    def test_fill_mean(self):
        print("====== Testing Fill Mean Imputation ======")
        result = impute_missing(self.data, data_fields='price', method=fill_mean, cross_section=True, suffix='mean')
        self.assertIn('price_mean', result.columns)
        self.assertFalse(result['price_mean'].isna().any())
        # Check mean imputation for the missing value
        print(result)


    def test_fill_median(self):
        print("====== Testing Fill Median Imputation ======")
        result = impute_missing(self.data, data_fields='volume', method=fill_median, cross_section=True, suffix='median')
        self.assertIn('volume_median', result.columns)
        self.assertFalse(result['volume_median'].isna().any())
        print(result)

    def test_fill_zero(self):
        print("====== Testing Fill Zero Imputation ======")
        result = impute_missing(self.data, data_fields=['price', 'volume'], method=fill_zero, cross_section=True, suffix='zero')
        self.assertIn('price_zero', result.columns)
        self.assertIn('volume_zero', result.columns)
        self.assertTrue((result['price_zero'] == 0).iloc[1])
        self.assertTrue((result['volume_zero'] == 0).iloc[2])
        print(result)

class TestOutlierHandling(unittest.TestCase):

    def setUp(self) -> None:
        self.data = pd.DataFrame({
            'date': ['2021-01-01', '2021-01-01', '2021-01-02', '2021-01-02'],
            'ticker': ['A', 'B', 'A', 'B'],
            'price': [10, 1000, 15, 2000],
            'volume': [100, 200, 3000, 400]
        })

    def test_clip_zscore(self):
        print("====== Testing Clip Z-Score Outlier Handling ======")
        result = handle_outliers(self.data, data_fields='price', method=clip_zscore, cross_section=True, suffix='z', threshold=1.0)
        self.assertIn('price_z', result.columns)
        # Check that outliers are clipped
        max_val = result[result['date'] == '2021-01-01']['price_z'].max()
        min_val = result[result['date'] == '2021-01-01']['price_z'].min()
        self.assertLessEqual(max_val, result[result['date'] == '2021-01-01']['price_z'].mean() + 1.0 * result[result['date'] == '2021-01-01']['price_z'].std())
        self.assertGreaterEqual(min_val, result[result['date'] == '2021-01-01']['price_z'].mean() - 1.0 * result[result['date'] == '2021-01-01']['price_z'].std())
        print(result)

    def test_clip_iqr(self):
        print("====== Testing Clip IQR Outlier Handling ======")
        result = handle_outliers(self.data, data_fields='volume', method=clip_iqr, cross_section=True, suffix='iqr', threshold=0.5)
        self.assertIn('volume_iqr', result.columns)
        # Check that outliers are clipped
        q1 = self.data[self.data['date'] == '2021-01-02']['volume'].quantile(0.25)
        q3 = self.data[self.data['date'] == '2021-01-02']['volume'].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 0.5 * iqr
        upper = q3 + 0.5 * iqr
        clipped = result[(result['date'] == '2021-01-02')]['volume_iqr']
        self.assertTrue((clipped >= lower).all() and (clipped <= upper).all())
        print(result)

class TestStandardizationMethods(unittest.TestCase):

    def setUp(self) -> None:
        # setup database connection
        with open('tests/db_config.json', 'r') as f:
            db_config = json.load(f)
        self.engine = get_engine(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        
        # get test data
        self.test_data = read_mysql(
            engine=self.engine,
            table_name='daily',
            data_fields=['close', 'open'],
            tickers=['000001.SZ', '600000.SH', '000002.SZ', '600004.SH'],
            start=datetime(2020, 1, 1),
            end=datetime(2020, 1, 9)
        )
    
    def test_z_score_standardization(self):
        print("====== Testing Z-Score Standardization ======")
        standardized_data = standardize(
            data=self.test_data,
            data_fields='close',
            method=z_score,
            cross_section=True,
            suffix='z'
        )
        self.assertIn('close_z', standardized_data.columns)
        self.assertTrue((standardized_data['close_z'].mean() - 0) < 1e-6)
        self.assertTrue((standardized_data['close_z'].std() - 1) < 1e-6)
        print(standardized_data[['close', 'close_z']].head())
    
    def test_z_score_multiple_fields(self):
        print("====== Testing Z-Score Standardization with Multiple Fields ======")
        standardized_data = standardize(
            data=self.test_data,
            data_fields=['close', 'open'],
            method=z_score,
            cross_section=True,
            suffix='z'
        )
        self.assertIn('close_z', standardized_data.columns)
        self.assertIn('open_z', standardized_data.columns)
        self.assertTrue((standardized_data['close_z'].mean() - 0) < 1e-6)
        self.assertTrue((standardized_data['open_z'].mean() - 0) < 1e-6)
        print(standardized_data[['close', 'close_z', 'open', 'open_z']].head())
    
    def test_z_score_time_series(self):
        print("====== Testing Z-Score Standardization with Time Series ======")
        standardized_data = standardize(
            data=self.test_data,
            data_fields='close',
            method=z_score,
            cross_section=False,
            suffix='z'
        )
        self.assertIn('close_z', standardized_data.columns)
        self.assertTrue((standardized_data['close_z'].mean() - 0) < 1e-6)
        self.assertTrue((standardized_data['close_z'].std() - 1) < 1e-6)
        # select a specific ticker for demonstration
        print(standardized_data.loc[pd.IndexSlice[:, '000001.SZ'], ['close', 'close_z']].head())
    
    def test_z_score_without_suffix(self):
        print("====== Testing Z-Score Standardization Without Suffix ======")
        standardized_data = standardize(
            data=self.test_data,
            data_fields='close',
            method=z_score,
            cross_section=True,
            suffix=None
        )
        self.assertIn('close', standardized_data.columns)
        self.assertTrue((standardized_data['close'].mean() - 0) < 1e-6)
        self.assertTrue((standardized_data['close'].std() - 1) < 1e-6)
        print(standardized_data[['close']].head())
            
    def test_min_max_standardization(self):
        print("====== Testing Min-Max Standardization ======")
        standardized_data = standardize(
            data=self.test_data,
            data_fields='close',
            method=min_max,
            cross_section=True,
            suffix='minmax'
        )
        self.assertIn('close_minmax', standardized_data.columns)
        self.assertTrue((standardized_data['close_minmax'].min() - 0) < 1e-6)
        self.assertTrue((standardized_data['close_minmax'].max() - 1) < 1e-6)
        print(standardized_data[['close', 'close_minmax']].head())

    def test_robust_standardization(self):
        print("====== Testing Robust Standardization ======")
        standardized_data = standardize(
            data=self.test_data,
            data_fields='close',
            method=robust,
            cross_section=True,
            suffix='robust'
        )
        print(standardized_data[['close', 'close_robust']].head())