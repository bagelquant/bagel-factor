# Result Class Documentation

## Overview

The `Result` class is a dataclass designed to hold the results of factor return calculations. It provides various methods and properties to calculate and summarize factor returns, information coefficients (IC), and related statistics.

---

## Attributes

### Required Attributes

- **`data`** (`pd.DataFrame`):
  The input data used for calculations.
- **`target`** (`str`):
  The target factor name.
- **`prediction`** (`str`):
  The prediction column name.
- **`rebalance_date_index`** (`pd.DatetimeIndex`):
  The index of rebalance dates.

### Optional Attributes

- **`description`** (`str`, default="Factor return results"):
  A description of the result object.
- **`group_num`** (`int`, default=5):
  The number of groups for grouping calculations.
- **`rlm_weight`** (`pd.Series`, default=`pd.Series()`):
  Weights used for Robust Linear Model (RLM) calculations.

---

## Methods and Properties

### Summary Method

- **`summary(included_fields: list[str]) -> pd.Series`**
  - **Description**: Generates a summary of the results for the specified fields.
  - **Parameters**:
    - `included_fields` (`list[str]`): List of fields to include in the summary.
  - **Returns**: A `pd.Series` containing the summary of the results.
  - **Raises**: `ValueError` if a field in `included_fields` is not a valid attribute.

### Information Coefficients (IC)

- **`spearman_ic`** (`pd.Series`):
  Calculates the Spearman IC.
- **`pearson_ic`** (`pd.Series`):
  Calculates the Pearson IC.
- **`spearman_icir`** (`float`):
  Calculates the IC ratio using the Spearman method.
  - **Raises**: `ZeroDivisionError` if the standard deviation of Spearman IC is zero.
- **`pearson_icir`** (`float`):
  Calculates the IC ratio using the Pearson method.
  - **Raises**: `ZeroDivisionError` if the standard deviation of Pearson IC is zero.

### Factor Return Calculations

- **`factor_return_grouping`** (`pd.DataFrame`):
  Calculates factor returns using grouping.
- **`factor_return_grouping_hml`** (`pd.Series`):
  Extracts the HML (High Minus Low) column from the grouping results.
- **`factor_return_grouping_t_test`** (`tuple[np.float64, np.float64]`):
  Performs a t-test on the HML factor returns.
  - **Raises**: `ValueError` if the 'HML' column is missing in `factor_return_grouping`.

### Regression-Based Factor Returns

- **`factor_return_ols`** (`pd.Series`):
  Calculates factor returns using Ordinary Least Squares (OLS).
- **`factor_return_ols_t_test`** (`tuple[np.float64, np.float64]`):
  Performs a t-test on the OLS factor returns.
- **`factor_return_wls`** (`pd.Series`):
  Calculates factor returns using Weighted Least Squares (WLS).
- **`factor_return_wls_t_test`** (`tuple[np.float64, np.float64]`):
  Performs a t-test on the WLS factor returns.
- **`factor_return_rlm`** (`pd.Series`):
  Calculates factor returns using Robust Linear Model (RLM).
- **`factor_return_rlm_t_test`** (`tuple[np.float64, np.float64]`):
  Performs a t-test on the RLM factor returns.

---

## Usage Example

```python
import pandas as pd
from bagel_factor.result import Result

# Example data
data = pd.DataFrame({
    'factor': [0.1, 0.2, 0.3],
    'prediction': [0.15, 0.25, 0.35]
})
rebalance_dates = pd.date_range(start='2023-01-01', periods=3, freq='M')

# Create a Result object
result = Result(
    data=data,
    target='factor',
    prediction='prediction',
    rebalance_date_index=rebalance_dates
)

# Access properties
print(result.spearman_ic)
print(result.factor_return_ols_t_test)
```

---

## Notes

- Ensure that the input data is preprocessed correctly before creating a `Result` object.
- Handle exceptions like `ZeroDivisionError` and `ValueError` as needed when accessing properties.

---

## References

- [SciPy Documentation](https://docs.scipy.org/doc/scipy/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
