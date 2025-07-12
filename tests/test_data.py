import unittest
import json
from datetime import datetime

from src.bagel_factor import get_engine, read_mysql

class TestDataFunctions(unittest.TestCase):

    def setUp(self) -> None:
        with open('tests/db_config.json', 'r') as f:
            db_config = json.load(f)
        self.engine = get_engine(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )

    def test_read_mysql(self) -> None:
        print('\n===================== Testing read_mysql ====================')
        df = read_mysql(engine=self.engine,
                        table_name='daily',
                        data_fields='close')
        print(df.head())
        print(f'Data shape: {df.shape}')

    def test_read_mysql_with_multiple_fields(self) -> None:
        print('\n===================== Testing read_mysql with multiple fields ====================')
        df = read_mysql(engine=self.engine,
                        table_name='daily',
                        tickers=['000001.SZ', '600000.SH'],
                        data_fields=['close', 'open'])
        print(df.head())
        print(f'Data shape: {df.shape}')

    def test_read_mysql_with_tickers(self) -> None:
        print('\n===================== Testing with tickers ====================')
        df = read_mysql(engine=self.engine,
                        table_name='daily',
                        data_fields='close',
                        tickers=['000001.SZ', '600000.SH'])
        print(df.head())
        print(f'Data shape: {df.shape}')
    
    def test_read_mysql_with_date_range(self) -> None:
        print('\n===================== Testing with date range ====================')
        df = read_mysql(engine=self.engine,
                        table_name='daily',
                        data_fields='close',
                        start=datetime(2020, 1, 1),
                        end=datetime(2020, 12, 31))
        print(df.head())
        print(df.shape)
    
    def test_read_mysql_with_tickers_and_date_range(self) -> None:
        print('===================== Testing with tickers and date range ====================')
        df = read_mysql(engine=self.engine,
                        table_name='daily',
                        data_fields=['close', 'open'],
                        tickers=['000001.SZ', '600000.SH'],
                        start=datetime(2020, 1, 1),
                        end=datetime(2020, 12, 31))
        print(df.head())


if __name__ == "__main__":
    unittest.main()
