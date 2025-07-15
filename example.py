"""
Example use case

1. Data
  - Read data
  - Necessary calculations, Ex: returns, factor values 
2. Preprocessing
3. Evaluation 
4. Report
"""

import json
from time import perf_counter
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import text

from src.bagel_factor import read_mysql, get_engine
from src.bagel_factor import Result


def get_raw_data() -> pd.DataFrame:
    with open('tests/db_config.json') as f:
        db_config = json.load(f)
        engine = get_engine(**db_config)

    # Select stocks in 主板 market
    with engine.begin() as conn:
        query = "SELECT ts_code FROM stock_basic WHERE market = '主板'"
        result = conn.execute(text(query))
        tickers = [row[0] for row in result.fetchall()]
        
    price = read_mysql(
        engine=engine,
        table_name='daily',
        data_fields=['close'],
        tickers=tickers,
        start=datetime(2020, 1, 1),
        end=datetime(2020, 6, 30)
    )
    
    total_share = read_mysql(
        engine=engine,
        table_name='balancesheet',
        data_fields='total_share',
        date_col='f_ann_date',
        start=datetime(2019, 6, 1), end=datetime(2020, 6, 30)
    )

    data = pd.concat([price, total_share]).sort_index()
    data['total_share'] = data['total_share'].groupby('ticker').ffill()
    return data.dropna()


def calculate_required_field(data: pd.DataFrame) -> pd.DataFrame:
    # add next n return
    for n in range(1, 21):
        data[f'next_{n}d_return'] = data['close'].groupby('ticker').pct_change(n)
        data[f'next_{n}d_return'] = data[f'next_{n}d_return'].groupby('ticker').shift(-n)
    # add log size
    data['log_size'] = np.log(data['close'] * data['total_share'])
    return data


def main() -> None:
    data = get_raw_data()
    data = calculate_required_field(data)
    
    result = Result(
        data=data,
        target='log_size',
        prediction='next_20d_return',
        rebalance_date_index=data.index.get_level_values('date').unique(),  # type: ignore[arg-type]
        description='Test result',
        group_num=10
    )

    print(result.summary(
        included_fields=[
            'description',
            'pearson_ic', 
            'pearson_icir', 
            'spearman_ic',
            'spearman_icir',
            'factor_return_grouping_hml', 
            'factor_return_grouping_t_stat', 
            'factor_return_grouping_p_value',
            'factor_return_ols',
            'factor_return_ols_t_stat',
            'factor_return_ols_p_value',
            'factor_return_rlm',
            'factor_return_rlm_t_stat',
            'factor_return_rlm_p_value',
        ]
    ))

    result.pearson_ic.plot(title='Pearson IC')
    plt.show()

if __name__ == '__main__':
    start = perf_counter()
    main()
    time_cost = perf_counter() - start
    print(f"Time cost: {time_cost:.2f}s or {time_cost/60:.2f} mins")
