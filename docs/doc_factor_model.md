# Factor Model Documentation

## Overview

The `FactorModel` class provides a framework for evaluating the performance of financial factors using the 
cross-sectional (Fama-MacBeth) regression approach. This model is commonly used in quantitative finance to estimate 
factor risk premium and test the significance of various factors in explaining asset returns.

## Class: `FactorModel`

### Purpose
The `FactorModel` class performs cross-sectional regressions for each time period, collects the regression coefficients (factor returns), and conducts t-tests to evaluate the statistical significance of each factor.

### Inputs
- **factor_loadings** (`dict[str, pd.DataFrame]`):
  - Dictionary mapping factor names to their loading DataFrames.
  - Each DataFrame should have dates as the index and tickers as columns.
- **factor_returns** (`pd.DataFrame`):
  - DataFrame of stock next returns, indexed by date and columns as tickers.
- **rf** (`float`, optional):
  - Risk-free rate. Default is 0.0.

### Data Structure Requirements
- All DataFrames must have the same index (dates) and columns (tickers).
- The index frequency should match the rebalance frequency of the strategy.

### Main Attributes
- **regression_params** (`pd.DataFrame`):
  - Stores the regression coefficients (intercept and factor returns) for each date.
  - Index: dates; Columns: 'const' + factor names.
- **t_test_table** (`pd.DataFrame`):
  - Stores the mean, standard deviation, t-statistic, and p-value for each regression parameter.
  - Index: 'const' + factor names; Columns: 'factor_return', 'std', 't-stat', 'p-value'.

### Main Methods
- **`__post_init__()`**
  - Automatically runs the regression and t-test upon initialization.
- **`_loop_regression()`**
  - Iterates over each date, performs cross-sectional regression, and stores the results in `regression_params`.
- **`_cross_sectional_regression(date)`**
  - For a given date, regresses stock returns on factor loadings using OLS (with intercept).
  - Returns a statsmodels regression result.
- **`_t_test()`**
  - Performs a t-test for each regression parameter across all dates.
  - Stores the results in `t_test_table`.

### Example Usage

```python
from bagel_factor.factor_model.factor_model import FactorModel

# factor_loadings: dict of factor name -> DataFrame (date x ticker)
# factor_returns: DataFrame (date x ticker)
model = FactorModel(factor_loadings, factor_returns)

# Access regression coefficients
print(model.regression_params)

# Access t-test results
print(model.t_test_table)
```

### Notes
- The model uses `statsmodels` for OLS regression and `scipy.stats` for t-tests.
- Missing data is handled by dropping NaNs in the regression step.
- The intercept ('const') is always included in the regression.

### References
- Fama, E. F., & MacBeth, J. D. (1973). Risk, Return, and Equilibrium: Empirical Tests. *Journal of Political Economy*, 81(3), 607-636.

---

For more details, see the source code in `src/bagel_factor/factor_model/factor_model.py`.

