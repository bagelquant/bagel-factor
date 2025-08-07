# data_handling Module

The `data_handling` module provides core utilities for managing, validating, and preprocessing factor data in quantitative finance workflows. It is designed to ensure robust handling of factor values, including data cleaning, normalization, and flexible metadata support.

## Submodules

### 1. `factor_data.py`

Defines the `FactorData` class, a container for factor values with the following features:

- **Validation**: Ensures factor data is a `pandas.Series` with a MultiIndex of (`date`, `ticker`), where `date` is a `pd.Timestamp` and `ticker` is a `str`.
- **Metadata**: Supports optional metadata for extensibility.
- **Cleaning & Filtering**: Methods for dropping missing values and filtering by a universe mask.
- **Preprocessing**: Integrates with preprocessing methods for standardization (see `preprocessing.py`).
- **Conversion Utilities**: Methods to convert to/from `Series`, `DataFrame`, and `dict`.
- **Properties**: Easy access to start/end dates, shape, and unique tickers.

#### Key Class: `FactorData`

- `factor_data`: `pd.Series` with MultiIndex (`date`, `ticker`)
- `metadata`: Optional `dict` for additional context
- `factor_name`: Optional name for the factor

#### Key Methods

- `dropna(how='any')`: Remove missing values.
- `filter_by_universe(universe_mask)`: Filter by a boolean mask.
- `standardize(method)`: Apply a preprocessing method.
- `to_series()`, `to_frame()`, `to_dict()`, `from_dict()`: Conversion utilities.

#### Helper Function

- `create_factor_data_from_df(factor_df, metadata=None, factor_name=None)`: Converts a DataFrame (index: date, columns: ticker) to a `FactorData` instance.

---

### 2. `preprocessing.py`

Defines standard preprocessing (normalization) methods for factor data, all operating cross-sectionally (per date):

- `cross_sectional_zscore`: Z-score normalization.
- `cross_sectional_minmax`: Min-max scaling to [0, 1].
- `cross_sectional_rank`: Ranking (various methods, ascending/descending).
- `cross_sectional_winsorize`: Winsorization (clipping to quantiles).

All preprocessing methods accept and return a `pd.Series` with MultiIndex (`date`, `ticker`), ensuring compatibility with `FactorData`.

#### Type Alias

- `PreprocessingMethod`: `Callable[[pd.Series], pd.Series]` — for type safety and clarity.

---

## Usage Example

```python
from bagel_factor.data_handling.factor_data import FactorData, create_factor_data_from_df
from bagel_factor.data_handling.preprocessing import cross_sectional_zscore

# Create FactorData from DataFrame
factor_data = create_factor_data_from_df(df)

# Standardize using z-score
standardized = factor_data.standardize(cross_sectional_zscore)
```

---

## Summary

The `data_handling` module is the foundation for robust, extensible, and reproducible factor data management, supporting both data integrity and flexible preprocessing in quantitative research pipelines.
