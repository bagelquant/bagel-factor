# Data Module

This module provides functions to load and standardize financial data for use in the package. The standard data format is a multi-index `pandas.DataFrame` indexed by `date` and `ticker`, which is well-suited for time-series analysis in quantitative finance.

## Standard Data Format

- **Multi-index DataFrame**: Indexed by `date` and `ticker` (asset), allowing efficient operations and easy access to data for specific assets and dates.

## Main Functionalities

### 1. Read from CSV File

- **Function**: `read_csv`
- **Description**: Reads data from a CSV file and returns a DataFrame with a multi-index (`date`, `ticker`).
- **Parameters**:
  - `path` (`Path`): Path to the CSV file.
  - `date_col` (`str`, default `'data'`): Name of the date column in the CSV.
  - `ticker_col` (`str`, default `'ticker'`): Name of the ticker column in the CSV.
- **Returns**: `pd.DataFrame` with multi-index (`date`, `ticker`).

### 2. Read from MySQL Database (bagel-tushare style)

- **Function**: `read_mysql`
- **Description**: Reads data from a MySQL database table and returns a DataFrame with a multi-index (`date`, `ticker`). Supports filtering by date range and ticker list.
- **Parameters**:
  - `engine` (`Engine`): SQLAlchemy engine connected to the MySQL database.
  - `table_name` (`str`): Name of the table to read from.
  - `data_fields` (`list[str] | str`): List of fields or a single field to select.
  - `date_col` (`str`, default `'trade_date'`): Name of the date column.
  - `ticker_col` (`str`, default `'ts_code'`): Name of the ticker column.
  - `tickers` (`list[str] | str | None`, optional): List of tickers or a single ticker to filter.
  - `start` (`datetime | None`, optional): Start date for filtering (inclusive).
  - `end` (`datetime | None`, optional): End date for filtering (inclusive).
- **Returns**: `pd.DataFrame` with multi-index (`date`, `ticker`) and selected data fields.

### 3. Create SQLAlchemy Engine

- **Function**: `get_engine`
- **Description**: Creates a SQLAlchemy engine for connecting to a MySQL database.
- **Parameters**:
  - `host` (`str`): Database host.
  - `port` (`int`): Database port.
  - `user` (`str`): Database user.
  - `password` (`str`): Database password.
  - `database` (`str`, default `'tushare'`): Database name.
- **Returns**: `Engine` object for database connection.

## Example Usage

```python
from pathlib import Path
from bagel_factor.data.data import read_csv, get_engine, read_mysql

# Read from CSV
csv_df = read_csv(Path('data.csv'), date_col='date', ticker_col='ticker')

# Read from MySQL
env = get_engine(host='localhost', port=3306, user='user', password='pass')
mysql_df = read_mysql(env, table_name='daily', data_fields=['open', 'close'], start='2021-01-01', end='2021-12-31')
```

This module ensures that all data loaded into the package follows a consistent, analysis-ready format, whether sourced from CSV files or a MySQL database.
