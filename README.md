# Bagel Factor

## Overview

Bagel Factor is a universal, high-performance Python library for evaluating quantitative factor performance in equity trading. It is designed to be flexible, extensible, and efficient, leveraging `pandas` and `numpy` for fast computation and easy integration with existing data pipelines. The package supports a wide range of factor types and data frequencies, and provides a modular API for both research and production use.

## Key Features

- **Universality**: Supports price-based, fundamental, and alternative data factors; works with daily and intraday data.
- **Performance**: Optimized for speed and memory efficiency using vectorized operations in `numpy`/`pandas`.
- **Extensibility**: Modular design allows users to add custom metrics, filters, and workflows.
- **Usability**: Simple, well-documented API with clear input/output formats.

### Core Modules

- [**data_handling**](docs/modules/data_handling.md): Robust tools for factor data management, including validation, cleaning, and preprocessing. Supports multi-indexed Series/DataFrames and extensible metadata.
- [**metrics**](docs/modules/metrics.md): Comprehensive performance and risk metrics, including Information Coefficient (IC), quantile/group return analysis, Sharpe/Sortino ratios, drawdown, and more.
- [**visualization**](docs/modules/visualization.md): Publication-quality plotting utilities for IC time series, quantile returns, and cumulative spread returns.
- [**evaluator**](docs/modules/evaluator.md): High-level interface for orchestrating data handling, metric computation, and risk analysis. Central entry point for users.

## Quick Start Example

```python
from bagel_factor import FactorData, create_factor_data_from_df  # Data handling utilities
from bagel_factor import Evaluator  # Core evaluation
from bagel_factor import plots  # Visualization utilities

# Prepare factor and returns data (as DataFrame or Series)
factor_data = create_factor_data_from_df(factor_df)
future_returns = create_factor_data_from_df(returns_df)

# Initialize evaluator
evaluator = Evaluator(factor_data, future_returns, future_returns)

# Compute IC and quantile returns
ic_mean = evaluator.ic_mean()
qret = evaluator.quantile_return_df()

# Plot IC time series
fig = plots.plot_ic_series(evaluator.ic_series())
fig.show()
```

- Python 3.8+
- pandas
- numpy
- statsmodels (for statistical tests)
- matplotlib/seaborn (for visualization)

## Contact

- Email: [Yanzhong(Eric) Huang](mailto:eric.yanzhong.huang@gmail.com)
- Blog: [bagelquant](https://bagelquant.com)
