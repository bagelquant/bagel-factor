# Factor Model Documentation

## Overview

The `FactorModel` class in Bagel Factor provides a robust and extensible framework for evaluating the performance of financial factors using the cross-sectional (Fama-MacBeth) regression approach. This methodology is a cornerstone of quantitative finance, enabling researchers and practitioners to estimate factor risk premia and rigorously test the significance of various factors in explaining asset returns.

## What is a Factor Model?

A factor model explains asset returns as a function of one or more risk factors. In the Fama-MacBeth approach, cross-sectional regressions are performed at each time period, and the resulting factor returns (regression coefficients) are analyzed for statistical significance.

## Class: `FactorModel`

### Purpose

The `FactorModel` class automates the process of running cross-sectional regressions for each time period, collecting the regression coefficients (factor returns), and conducting t-tests to evaluate the statistical significance of each factor. This allows for a standardized, reproducible evaluation of factor models.

### Inputs

- **factor_loadings** (`dict[str, pd.DataFrame]`):
  - Dictionary mapping factor names to their loading DataFrames.
  - Each DataFrame should have dates as the index and tickers as columns.
- **stock_next_returns** (`pd.DataFrame`):
  - DataFrame of next-period stock returns, indexed by date and columns as tickers.
- **rf** (`float`, optional):
  - Risk-free rate. Default is 0.0.

#### Data Structure Requirements

- All DataFrames must have the same index (dates) and columns (tickers).
- The index frequency should match the rebalance frequency of the strategy.
- Missing data is handled by dropping NaNs in the regression step.

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
# stock_next_returns: DataFrame (date x ticker)
model = FactorModel(factor_loadings, stock_next_returns)

# Access regression coefficients (factor returns)
print(model.regression_params)

# Access t-test results
print(model.t_test_table)
```

### Notes & Best Practices

- The model uses `statsmodels` for OLS regression and `scipy.stats` for t-tests.
- The intercept ('const') is always included in the regression.
- Ensure all input DataFrames are properly aligned and cleaned before use.
- The Fama-MacBeth approach provides robust inference for factor significance, especially in the presence of time-varying exposures.

### References

- Fama, E. F., & MacBeth, J. D. (1973). Risk, Return, and Equilibrium: Empirical Tests. *Journal of Political Economy*, 81(3), 607-636.
- [BagelQuant: Factor Models](https://bagelquant.com/factor-models/)

---

For more details, see the source code in `src/bagel_factor/factor_model/factor_model.py`.
