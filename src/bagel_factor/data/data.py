"""
Data module

This module provided functions that could return a standard data format used in this package.

The standard data format:

A multi-index DataFrame with index `date` and `ticker`

The functions include:

- read from csv file
- read from MySQL database (bagel-tushare style)
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

from sqlalchemy import create_engine, Engine


def read_csv(path: Path,
             date_col: str = 'data',
             ticker_col: str = 'ticker') -> pd.DataFrame:
    df = pd.read_csv(path, index_col=[date_col, ticker_col], parse_dates=[date_col])
    df.index.names = ['date', 'ticker']
    return df


def get_engine(host: str,
               port: int,
               user: str,
               password: str,
               database: str = 'tushare') -> Engine:
    return create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')


def read_mysql(engine: Engine,
               table_name: str,
               data_fields: list[str] | str,
               date_col: str = 'trade_date',
               ticker_col: str = 'ts_code',
               tickers: list[str] | str | None = None,
               start: datetime | None = None,
               end: datetime | None = None) -> pd.DataFrame:
    """
    Read data from MySQL database and return a DataFrame with multi-index (date, ticker).
    Optionally filter by date range and ticker list.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine connected to the MySQL database.
    table_name : str
        Name of the table to read from.
    data_fields : list[str] | str
        List of fields to select from the table, or a single field name.
    date_col : str, optional
        Name of the date column, by default 'trade_date'.
    ticker_col : str, optional
        Name of the ticker column, by default 'ts_code'.
    tickers : list[str] | str | None, optional
        List of tickers or a single ticker to filter, by default None (no filter).
    start : datetime, optional
        Start date for filtering (inclusive).
    end : datetime, optional
        End date for filtering (inclusive).

    Returns
    -------
    pd.DataFrame
        DataFrame with multi-index (date, ticker) and selected data fields.
    """
    if isinstance(data_fields, str):
        data_fields = [data_fields]
    fields = [date_col, ticker_col] + data_fields
    query = f"SELECT {', '.join(fields)} FROM {table_name}"
    conditions = []
    if start is not None:
        conditions.append(f"{date_col} >= '{start.strftime('%Y-%m-%d')}'")
    if end is not None:
        conditions.append(f"{date_col} <= '{end.strftime('%Y-%m-%d')}'")
    if tickers is not None:
        if isinstance(tickers, str):
            tickers = [tickers]
        tickers_str = ', '.join([f"'{t}'" for t in tickers])
        conditions.append(f"{ticker_col} IN ({tickers_str})")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    df = pd.read_sql(query, engine, parse_dates=[date_col], index_col=[date_col, ticker_col])
    df.index.names = ['date', 'ticker']
    return df
