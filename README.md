# Bagel Factor

## Overview

Bagel Factor is a universal, high-performance Python library for evaluating quantitative factor performance in equity trading. It is designed to be flexible, extensible, and efficient, leveraging `pandas` and `numpy` for fast computation and easy integration with existing data pipelines. The package supports a wide range of factor types and data frequencies, and provides a modular API for both research and production use.

## Key Features

- **Universality**: Supports price-based, fundamental, and alternative data factors; works with daily and intraday data.
- **Performance**: Optimized for speed and memory efficiency using vectorized operations in `numpy`/`pandas`.
- **Extensibility**: Modular design allows users to add custom metrics, filters, and workflows.
- **Usability**: Simple, well-documented API with clear input/output formats.

### Core Modules

- **Factor Data Handling**: Standardized input format for factor values, returns, and metadata. Multi-indexed DataFrame support. Data validation and cleaning utilities.
- **Performance Metrics**: Information Coefficient (IC/Rank IC), quantile/group return analysis, turnover, Sharpe/Sortino ratios, drawdown, and custom metric registration.
- **Visualization**: Built-in plotting for IC time series, quantile returns, turnover, and more. Export to CSV, Excel, and image formats.
- **Parallelization (Optional)**: Multi-core computation support via `numba`, `joblib`, or similar.

## Implementation Plan

1. Define data structures and input validation logic
2. Implement core metric calculations (IC, quantile returns, etc.)
3. Develop backtesting module
4. Add visualization utilities
5. Write documentation and usage examples
6. Optimize for performance and add optional parallelization
7. Package for PyPI and provide installation instructions

## Dependencies

- Python 3.8+
- pandas
- numpy
- statsmodels (for statistical tests)
- matplotlib/seaborn (for visualization)
- (Optional) numba/joblib for parallelization

## Contact

- Email: [Yanzhong(Eric) Huang](mailto:eric.yanzhong.huang@gmail.com)
- Blog: [bagelquant](https://bagelquant.com)
