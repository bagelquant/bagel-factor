import unittest
import json
import pandas as pd
import numpy as np
from datetime import datetime

from src.bagel_factor import get_engine, read_mysql
from src.bagel_factor import standardize, z_score
from src.bagel_factor import calculate_ic_s
from sqlalchemy import text


class TestEvaluation(unittest.TestCase):

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

        # Select stocks in 主板 market
        with self.engine.begin() as conn:
            query = "SELECT ts_code FROM stock_basic WHERE market = '主板'"
            result = conn.execute(text(query))
            self.tickers = [row[0] for row in result.fetchall()]
            
        self.price = read_mysql(
            engine=self.engine,
            table_name='daily',
            data_fields=['close'],
            tickers=self.tickers,
            start=datetime(2020, 1, 1),
            end=datetime(2020, 6, 30)
        )
        
        self.total_share = read_mysql(
            engine=self.engine,
            table_name='balancesheet',
            data_fields='total_share',
            date_col='f_ann_date',
            start=datetime(2019, 6, 1),
            end=datetime(2020, 6, 30)
        )

        self.data = pd.concat([self.price, self.total_share]).sort_index()
        self.data['total_share'] = self.data['total_share'].groupby('ticker').ffill()
        self.data = self.data.loc[pd.IndexSlice['2020-01-01':, :], :].dropna()
        self.data['log_size'] = np.log(self.data['close'] * self.data['total_share'])

        # calculate next 20 day return
        self.data['next_20d_return'] = self.data['close'].groupby('ticker').pct_change(periods=20)
        self.data['next_20d_return'] = self.data['next_20d_return'].groupby('ticker').shift(-20)

    def test_price(self):
        print('\n====== Price Data ======')
        print(self.price)
        # memory size
        print('Memory size:', self.price.memory_usage(deep=True).sum() / (1024 ** 2), 'MB')

    def test_total_share(self):
        print('\n====== Total Share Data ======')
        print(self.total_share)
        # memory size
        print('Memory size:', self.total_share.memory_usage(deep=True).sum() / (1024 ** 2), 'MB')

    def test_data(self):
        print('\n====== Data ======')
        print(self.data)
        print(self.data.loc[pd.IndexSlice[:'2020-02-10', '000001.SZ'], :])
        # memory size
        print('Memory size:', self.total_share.memory_usage(deep=True).sum() / (1024 ** 2), 'MB')

    def test_calculate_ic(self):
        print('\n====== Testing Calculate IC ======')
        ic_s = calculate_ic_s(
            data=self.data,
            target='log_size',
            prediction='next_20d_return',
            rebalance_date_index=self.data.index.get_level_values('date').unique()  # type: ignore
        )
        print(ic_s)
        print(f'\nIC mean: {ic_s.mean():.4f}, IC std: {ic_s.std():.4f}')
