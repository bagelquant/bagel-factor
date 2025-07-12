# Outlier Handling Module

This module provides outlier detection and handling methods for financial data, allowing users to manage anomalous values before further analysis. The main functionalities are implemented in `outlier.py` and include several outlier handling techniques as well as a flexible interface for applying them to DataFrames.

## Outlier Handling Methods

The following outlier handling methods are available:

- **Z-score Clipping (`clip_zscore`)**: Clips values to within a specified number of standard deviations from the mean.
- **IQR Clipping (`clip_iqr`)**: Clips values to within a specified interquartile range (IQR) from the median.

All methods accept a `pandas.DataFrame` or `pandas.Series` and return the processed result.

## `handle_outliers` Function

The `handle_outliers` function applies a chosen outlier handling method to specified fields in a DataFrame. It supports both cross-sectional and time-series outlier handling.

### Parameters

- `data` (`pd.DataFrame`): The input DataFrame containing the data to be processed.
- `data_fields` (`list[str] | str`): The field(s) to process. Can be a single field or a list of fields.
- `method` (`OutlierMethod`, optional): The outlier handling method to use. Defaults to `clip_zscore`.
- `cross_section` (`bool`, optional):
  - If `True`, processes across the date index for each ticker (cross-sectional handling).
  - If `False`, processes across the ticker index for each date (time-series handling).
  - Defaults to `True`.
- `suffix` (`str | None`, optional): Suffix to append to the processed field names. If `None`, the original field names are used.
- `**method_kwargs`: Additional keyword arguments to pass to the method (e.g., `threshold`).

### Returns

- `pd.DataFrame`: A DataFrame with the processed fields added.

### Example Usage

```python
import pandas as pd
from bagel_factor.preprocessing.outlier import handle_outliers, clip_iqr

data = pd.DataFrame({
    'date': ['2021-01-01', '2021-01-01', '2021-01-02'],
    'ticker': ['A', 'B', 'A'],
    'price': [10, 200, 15]
})

# Handle outliers in 'price' across tickers for each date using IQR clipping
result = handle_outliers(data, data_fields='price', method=clip_iqr, cross_section=True, suffix='iqr', threshold=1.5)
print(result)
```

### Notes

- The function expects the DataFrame to have columns `date` and `ticker` for grouping.
- The output fields will have the specified suffix if provided.

This module is useful for preparing financial data for modeling, ensuring that extreme values do not unduly influence analysis or model training.
