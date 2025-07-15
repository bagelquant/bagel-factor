# Standardization Module

This module provides standardization methods for financial data, allowing users to transform their data for further analysis. The main functionalities are implemented in `standardize.py` and include several standardization techniques as well as a flexible interface for applying them to DataFrames.

## Standardization Methods

The following standardization methods are available:

- **Z-score Standardization (`z_score`)**: Transforms data by subtracting the mean and dividing by the standard deviation.
- **Min-Max Scaling (`min_max`)**: Scales data to a [0, 1] range by subtracting the minimum and dividing by the range.
- **Robust Scaling (`robust`)**: Scales data by subtracting the median and dividing by the interquartile range (IQR).

All methods accept a `pandas.DataFrame` or `pandas.Series` and return the standardized result.

## `standardize` Function

The `standardize` function applies a chosen standardization method to specified fields in a DataFrame. It supports both cross-sectional and time-series standardization.

### Parameters

- `data` (`pd.DataFrame`): The input DataFrame containing the data to be standardized.
- `data_fields` (`list[str] | str`): The field(s) to standardize. Can be a single field or a list of fields.
- `method` (`StandardizeMethod`, optional): The standardization method to use. Defaults to `z_score`.
- `cross_section` (`bool`, optional):
  - If `True`, standardizes across the date index for each ticker (cross-sectional standardization).
  - If `False`, standardizes across the ticker index for each date (time-series standardization).
  - Defaults to `True`.
- `suffix` (`str | None`, optional): Suffix to append to the standardized field names. If `None`, the original field names are used.

### Returns

- `pd.DataFrame`: A DataFrame with the standardized fields added.

### Example Usage

```python
import pandas as pd
from bagel_factor.preprocessing.standardize import standardize, min_max

data = pd.DataFrame({
  'date': ['2021-01-01', '2021-01-01', '2021-01-02'],
  'ticker': ['A', 'B', 'A'],
  'price': [10, 20, 15]
})

# Standardize 'price' across tickers for each date using min-max scaling
result = standardize(data, data_fields='price', method=min_max, suffix='minmax')
print(result)
```

### Notes

- The function expects the DataFrame to have columns `date` and `ticker` for grouping.
- The output fields will have the specified suffix if provided.

This module is useful for preparing financial data for modeling, ensuring that features are on comparable scales and robust to outliers when needed.
