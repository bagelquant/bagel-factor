# bagel_factor.evaluation.ic

## Module: ic.py

This module provides functions to calculate the Information Coefficient (IC) and related metrics for evaluating the predictive power and stability of financial factors.

---

## Functions

### calculate_ic_s

```python
def calculate_ic_s(
    data: pd.DataFrame,
    target: str,
    prediction: str,
    rebalance_date_index: pd.DatetimeIndex,
    method: Literal['spearman', 'pearson'] = 'spearman'
) -> pd.Series:
```

**Description:**
Calculates the Information Coefficient (IC) between the target and prediction columns for each rebalance date. The IC is a correlation (Spearman or Pearson) that measures the cross-sectional relationship between the factor and future returns.

**Parameters:**

- `data`: Multi-index DataFrame with 'date' and 'ticker' as indices, and 'datafield' as columns.
- `target`: The name of the target column.
- `prediction`: The name of the prediction column.
- `rebalance_date_index`: Index of rebalance dates.
- `method`: Correlation method to use ('spearman' or 'pearson').

**Returns:**

- Series with IC values indexed by rebalance dates.

---

## Concepts

- **IC (Information Coefficient):** Measures the cross-sectional correlation between factor values and future returns for each period.
- **ICIR (Information Coefficient Information Ratio):** Measures the stability of the IC over time (not implemented in this file, but referenced in the docstring).
- **Rolling ICIR:** A rolling window version of the ICIR.

---

## Usage Example

```python
ic_series = calculate_ic_s(data, 'factor', 'next_return', rebalance_dates, method='spearman')
```
