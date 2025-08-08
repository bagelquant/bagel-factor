# evaluator Module

The `evaluator` module provides a high-level interface for evaluating the performance and risk characteristics of quantitative factors in equity trading. It orchestrates data handling, metric computation, and result aggregation, serving as the main entry point for users. In v2.0.1, users supply price data and Evaluator computes future returns internally with lazy evaluation.

## Main Class: `Evaluator`

### Overview

The `Evaluator` class encapsulates the workflow for factor evaluation, including:

- Information Coefficient (IC) and Information Ratio (ICIR)
- Quantile return analysis and quantile spread
- Risk metrics (volatility, Sharpe, Sortino, drawdown, Calmar, downside risk)
- Flexible evaluation period selection

### Initialization

```python
Evaluator(
  factor_data: FactorData,
  price_data: FactorData,
  factor_name: str = 'factor',
  return_type: Literal['log', 'normal'] = 'log',
  metadata: dict = {},
  periods_per_year: int = 252,
  n_quantiles: int = 10,
  ic_horizon: int = 1,
  rebalance_period: int = 1,
)
```

- Inputs are validated and aligned. Factor data is forward-filled per ticker to match the price index. Future returns are built on-demand from price using `ic_horizon` and `rebalance_period` settings.

### Key Methods & Properties

- **Setters**
  - `set_start_date(start_date)`: Set evaluation start date
  - `set_end_date(end_date)`: Set evaluation end date
  - `set_ic_horizon(periods)`: Horizon (index steps) for IC future returns
  - `set_rebalance_period(periods)`: Horizon/step for quantile tests
  - `set_return_type('log'|'normal')`: Return convention

- **IC & ICIR**
  - `ic_mean(method='pearson'|'spearman')`: Mean IC over period
  - `ic_std(method='pearson'|'spearman')`: Std of IC over period
  - `ic_ir(method='pearson'|'spearman')`: Information Ratio (annualized)

- **Quantile Returns & Spread**
  - `quantile_return_df`: DataFrame of mean returns by quantile/date
  - `quantile_spread_series`: Series of quantile spread returns
  - `quantile_spread_cum_return`: Cumulative return of quantile spread

- **Risk Metrics (on quantile spread)**
  - `quantile_spread_annualized_volatility()`
  - `quantile_spread_sharpe_ratio(risk_free_rate=0.0)`
  - `quantile_spread_max_drawdown()`
  - `quantile_spread_calmar_ratio()`
  - `quantile_spread_downside_risk(risk_free_rate=0.0)`
  - `quantile_spread_sortino_ratio(risk_free_rate=0.0)`

All results are computed over the selected evaluation period (`start_date` to `end_date`).

---

## Usage Example

```python
from bagel_factor.evaluator import Evaluator

# Initialize with factor and returns data (as FactorData)
eval = Evaluator(factor_data, future_returns_for_ic, future_returns_for_quantile)

# Set evaluation period (optional)
eval.set_start_date(pd.Timestamp('2022-01-01'))
eval.set_end_date(pd.Timestamp('2023-01-01'))

# Compute IC and IR
ic_mean = eval.ic_mean()
ic_ir = eval.ic_ir()

# Quantile returns and risk metrics
qret = eval.quantile_return_df()
spread = eval.quantile_spread_series()
sharpe = eval.quantile_spread_sharpe_ratio()
mdd = eval.quantile_spread_max_drawdown()
```

---

## Summary

The `evaluator` module is the central interface for robust, extensible, and reproducible factor performance analysis, integrating data validation, metric computation, and risk analysis in a single, user-friendly class.
