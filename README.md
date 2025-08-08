# Bagel Factor

## Overview

Bagel Factor is a universal, high-performance Python library for evaluating quantitative factor performance in equity trading. It’s flexible and efficient, built on `pandas`/`numpy`, and ships with a modular API for research and production.

## Key Features

- Universality: price, fundamental, alternative data; daily or intraday.
- Performance: vectorized operations; minimal copying.
- Extensibility: plug in custom metrics and workflows.
- Usability: clear, typed API and ready-to-use plots.

### Core Modules

- data_handling: Validated containers and preprocessing (Series with MultiIndex of (date, ticker)).
- metrics: IC, quantile returns, and risk metrics (Sharpe, Sortino, max drawdown, etc.). All risk metrics accept Series or DataFrame inputs.
- visualization: Plots for IC, quantile analysis, cumulative returns, drawdown, and distributions.
- evaluator: Orchestrates the full workflow with lazy computation and user-provided price data.

## Quick Start

```python
import pandas as pd
from bagel_factor import FactorData, Evaluator
from bagel_factor.visualization.plots import (
    plot_ic_series,
    plot_ic_histogram,
    plot_quantile_returns,
    plot_quantile_heatmap,
    plot_cumulative_return,
    plot_quantile_cumulative,
    plot_drawdown,
    plot_return_distribution,
)

# Factor and price data as MultiIndex Series: index = (date, ticker)
factor = ...  # pd.Series
price = ...   # pd.Series of adjusted close

factor_fd = FactorData(factor, factor_name='my_factor', validate=True, enforce_sorted=False)
price_fd = FactorData(price, factor_name='price', validate=True, enforce_sorted=False)

ev = Evaluator(factor_data=factor_fd, price_data=price_fd, factor_name='my_factor')
ev.set_ic_horizon(126)       # horizon for IC future returns
ev.set_rebalance_period(21)  # horizon/step for quantile tests

# Metrics
ic_series = ev.ic_series(method='spearman')
qret = ev.quantile_return_df()
spread = ev.quantile_spread_series()

# Plots
plot_ic_series(ic_series)
plot_ic_histogram(ic_series)
plot_quantile_returns(qret)
# Heatmap shows per-day ranks across quantiles (1 = best)
plot_quantile_heatmap(qret)
# Cumulative plots start at 0 with an auto-added pre-date point inferred from index step
plot_cumulative_return(spread, return_type='log')
plot_quantile_cumulative(qret, return_type='log')
plot_drawdown(spread, return_type='log')
plot_return_distribution(spread)
```

## Performance Tips

- Fast construction when inputs are trusted

```python
from bagel_factor.data_handling import FactorData

fd_fast = FactorData.unsafe_from_series(series, name='my_factor')
fd_fast2 = FactorData(series, factor_name='my_factor', validate=False, enforce_sorted=False)
```

- Avoid unnecessary copies

```python
s_view = fd_fast.to_series(copy=False)
df_view = fd_fast.to_frame(copy=False)
payload = fd_fast.to_dict(copy=False)
```

- Evaluator alignment behavior
  - If `factor_data.factor_data.index` already equals the price index, the Evaluator skips reindex/ffill.
  - If your pipeline guarantees alignment, ensure indices match to get the fast path.

```python
factor = factor.reindex(price.index).groupby(level='ticker').ffill()
ev = Evaluator(FactorData.unsafe_from_series(factor, name='factor'),
               FactorData.unsafe_from_series(price, name='price'))
```

- Direct function calls

```python
from bagel_factor.metrics import information_coefficient
from bagel_factor.metrics import quantile_returns, quantile_spread

ic = information_coefficient(factor_series, future_returns_series)
qret = quantile_returns(factor_series, future_returns_series, n_quantiles=10)
spread = quantile_spread(qret)
```

## Requirements

- Python 3.10+
- pandas, numpy
- matplotlib, seaborn (plots)
- statsmodels (optional tests)

## Contact

- Email: [Yanzhong(Eric) Huang](mailto:eric.yanzhong.huang@gmail.com)
- Blog: [bagelquant](https://bagelquant.com)
