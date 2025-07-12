# Missing Data Imputation Module

This module provides methods for handling missing data in financial datasets. The main functionalities are implemented in `missing_data.py` and include several imputation techniques as well as a flexible interface for applying them to DataFrames.

## Imputation Methods

The following imputation methods are available:

- **Mean Imputation (`fill_mean`)**: Fills missing values with the mean of the data.
- **Median Imputation (`fill_median`)**: Fills missing values with the median of the data.
- **Zero Imputation (`fill_zero`)**: Fills missing values with zero.

All methods accept a `pandas.DataFrame` or `pandas.Series` and return the imputed result.

## `impute_missing` Function

The `impute_missing` function applies a chosen imputation method to specified fields in a DataFrame. It supports both cross-sectional and time-series imputation.

### Parameters

- `data` (`pd.DataFrame`): The input DataFrame containing the data to be imputed.
- `data_fields` (`list[str] | str`): The field(s) to impute. Can be a single field or a list of fields.
- `method` (`ImputeMethod`, optional): The imputation method to use. Defaults to `fill_mean`.
- `cross_section` (`bool`, optional):
  - If `True`, imputes across the date index for each ticker (cross-sectional imputation).
  - If `False`, imputes across the ticker index for each date (time-series imputation).
  - Defaults to `True`.
- `suffix` (`str | None`, optional): Suffix to append to the imputed field names. If `None`, the original field names are used.

### Returns

- `pd.DataFrame`: A DataFrame with the imputed fields added.

### Example Usage

```python
import pandas as pd
from bagel_factor.preprocessing.missing_data import impute_missing, fill_median

data = pd.DataFrame({
    'date': ['2021-01-01', '2021-01-01', '2021-01-02'],
    'ticker': ['A', 'B', 'A'],
    'price': [10, None, 15]
})

# Impute 'price' across tickers for each date using median imputation
result = impute_missing(data, data_fields='price', method=fill_median, cross_section=True, suffix='median')
print(result)
```

### Notes

- The function expects the DataFrame to have columns `date` and `ticker` for grouping.
- The output fields will have the specified suffix if provided.

This module is useful for preparing financial data for modeling, ensuring that missing values are handled in a consistent and robust manner.
