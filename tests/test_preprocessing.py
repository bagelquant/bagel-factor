import unittest
import json
import pandas as pd
from datetime import datetime

from src.bagel_factor import get_engine, read_mysql
from src.bagel_factor import standardize, z_score, min_max, robust


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