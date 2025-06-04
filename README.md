# Bagel Factor

## Overview

Bagel Factor is a modular Python library for quantitative equity research. It supports the full workflow from data collection to multi-factor model evaluation and backtesting. The library provides standardized, reproducible tools for both single-factor and multi-factor analysis, including Fama-MacBeth regression, IC/ICIR evaluation, and comprehensive reporting.

## Workflow

- **Factor Module**
  - Single Factor Evaluation ([docs](docs/doc_single_factor_evaluation.md))
- **Model Module**
  - Multi-Factor Model Evaluation ([docs](docs/doc_factor_model.md))

## Key Features

- **Single Factor Evaluation**: Analyze factors using sort and regression methods. Includes IC/ICIR, group statistics, cumulative returns, and automated Markdown reporting.
- **Multi-Factor Model**: Evaluate multiple factors with Fama-MacBeth cross-sectional regression, t-tests, and clear summary tables.
- **Data Export**: All input and output data are saved as CSV files for further analysis and reproducibility.
- **Plotting**: Automatically generates and saves all key plots (IC, group means, histograms, cumulative returns) for reporting.

## Example Usage

Prepare two input DataFrames, both indexed by date with tickers as columns:

- `factor_data`: Contains factor values (e.g., momentum, value, size).
- `stock_next_returns`: Contains next period stock returns.

> **Important:**
> Ensure all data is pre-processed, cleaned, and aligned by date and ticker. For example, if using yearly rebalancing, the dates in `factor_data` and `stock_next_returns` must match and be yearly aligned.

```python
from bagel_factor import evaluate_factor
from pathlib import Path

# Evaluate a single factor and generate a report

evaluate_factor(
    factor_data,            # DataFrame: date x ticker
    stock_next_returns,     # DataFrame: date x ticker
    output_path=Path('output/'),
    sorting_group_num=10,
    factor_name='Momentum',
    factor_description='12-1M momentum factor'
)
```

For multi-factor model evaluation:

```python
from bagel_factor import evaluate_model
from pathlib import Path

# Evaluate a multi-factor model and generate a report

evaluate_model(
    factor_loadings,        # Dictionary of DataFrames: date x ticker
    stock_next_returns,     # DataFrame: date x ticker
    output_path=Path('output/')
)
```

## Documentation

- [Single Factor Evaluation](docs/doc_single_factor_evaluation.md)
- [Factor Model (Fama-MacBeth)](docs/doc_factor_model.md)

## References

- [BagelQuant: Factor Models](https://bagelquant.com/factor-models/)
- Fama, E. F., & MacBeth, J. D. (1973). Risk, Return, and Equilibrium: Empirical Tests. *Journal of Political Economy*, 81(3), 607-636.

## License

MIT License
