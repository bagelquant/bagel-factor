# metrics Module

The `metrics` module provides quantitative performance and risk evaluation tools for factor investing and portfolio analysis. It includes functions for calculating information coefficients, quantile-based returns, and a variety of risk and performance metrics.

## Submodules

### 1. `ic.py`

Implements the Information Coefficient (IC), a key measure of factor predictive power:

- **`information_coefficient`**: Computes the cross-sectional correlation (Pearson or Spearman) between factor values and future returns for each date. Returns a time series of IC values.
  - **Inputs**: `factor` (pd.Series), `future_returns` (pd.Series), both with MultiIndex (`date`, `ticker`)
  - **Parameters**: `method` ('pearson' or 'spearman'), `min_periods` (minimum pairs per date)
  - **Returns**: `pd.Series` indexed by date

---

### 2. `quantile_returns.py`

Provides tools for analyzing returns by factor quantiles:

- **`quantile_returns`**: Calculates mean future returns for each factor quantile, grouped by date.
  - **Inputs**: `factor` (pd.Series), `future_returns` (pd.Series), both with MultiIndex (`date`, `ticker`)
  - **Parameters**: `n_quantiles`, `quantile_labels`, `min_periods`
  - **Returns**: `pd.DataFrame` (index: date, columns: quantile, values: mean return)
- **`quantile_spread`**: Computes the spread between upper and lower quantile returns for each date.
  - **Inputs**: Output of `quantile_returns`
  - **Parameters**: `upper`, `lower` (quantile labels)
  - **Returns**: `pd.Series` (index: date, values: spread)

---

### 3. `risk_metrics.py`

A collection of standard risk and performance metrics for return series:

- **`accumulate_return`**: Computes cumulative returns (log or normal)
- **`annualized_volatility`**: Annualized standard deviation of returns
- **`sharpe_ratio`**: Annualized Sharpe ratio (risk-adjusted return)
- **`max_drawdown`**: Maximum drawdown (largest peak-to-trough loss)
- **`calmar_ratio`**: Calmar ratio (annual return / max drawdown)
- **`downside_risk`**: Annualized downside risk (volatility of negative returns)
- **`sortino_ratio`**: Annualized Sortino ratio (risk-adjusted return using downside risk)

All functions accept `pd.Series` of returns, with options for log or arithmetic returns and custom risk-free rates or period settings.

---

## Usage Example

```python
from bagel_factor.metrics.ic import information_coefficient
from bagel_factor.metrics.quantile_returns import quantile_returns, quantile_spread
from bagel_factor.metrics.risk_metrics import sharpe_ratio, max_drawdown

# Calculate IC
ic_series = information_coefficient(factor, future_returns)

# Quantile returns and spread
qret = quantile_returns(factor, future_returns)
spread = quantile_spread(qret)

# Risk metrics
sharpe = sharpe_ratio(returns)
mdd = max_drawdown(returns)
```

---

## Summary

The `metrics` module is essential for evaluating factor performance, analyzing return distributions, and quantifying risk in systematic investment research.
