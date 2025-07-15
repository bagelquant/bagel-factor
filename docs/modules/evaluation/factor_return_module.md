# bagel_factor.evaluation.factor_return

## Module: factor_return.py

This module provides functions to calculate factor returns for financial data using two main approaches:

- **Grouping (Quantile) Method**: Calculates factor returns by grouping assets into quantiles based on a target factor and computing the mean return for each group.
- **Regression Method**: Calculates factor returns by regressing future returns on the target factor using OLS, WLS, or RLM regression for each rebalance date.

---

## Functions

### calculate_factor_return_grouping

```python
def calculate_factor_return_grouping(
    data: pd.DataFrame,
    target: str,
    prediction: str,
    rebalance_date_index: pd.DatetimeIndex,
    group_num: int = 5,
) -> pd.DataFrame:
```

**Description:**
Calculates the factor returns by grouping the predictions into quantiles for each rebalance date. Returns a DataFrame with mean returns for each group and the Higher Minus Lower (HML) return.

**Parameters:**

- `data`: Multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns.
- `target`: The name of the target factor.
- `prediction`: The name of the prediction column (next period's return).
- `rebalance_date_index`: Index of rebalance dates.
- `group_num`: Number of quantile groups (default 5).

**Returns:**

- DataFrame with factor returns for each group and HML, indexed by rebalance dates.

---

### calculate_factor_return_regression

```python
def calculate_factor_return_regression(
    data: pd.DataFrame,
    target: str,
    prediction: str,
    rebalance_date_index: pd.DatetimeIndex,
    method: Literal['OLS', 'WLS', 'RLM'] = 'OLS',
    intercept: bool = False,
    **kwargs
) -> pd.DataFrame:
```

**Description:**
Calculates factor returns using regression (OLS, WLS, or RLM) for each rebalance date. The factor return is the regression coefficient of the target factor.

**Parameters:**

- `data`: Multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns.
- `target`: The name of the target factor.
- `prediction`: The name of the prediction column (next period's return).
- `rebalance_date_index`: Index of rebalance dates.
- `method`: Regression method ('OLS', 'WLS', or 'RLM').
- `intercept`: Whether to include an intercept in the regression.
- `**kwargs`: Additional arguments for the regression model (e.g., weights for WLS).

**Returns:**

- DataFrame with factor returns indexed by rebalance dates.

---

## Usage Example

```python
returns = calculate_factor_return_grouping(data, 'factor', 'next_return', rebalance_dates)
reg_returns = calculate_factor_return_regression(data, 'factor', 'next_return', rebalance_dates, method='OLS')
```
