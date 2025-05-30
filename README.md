# bagel-factor

## Overview

Bagel Factor is a modular Python library for quantitative equity research, supporting the full workflow from data collection to multi-factor model evaluation and backtesting. It provides standardized, reproducible tools for single-factor and multi-factor analysis, including Fama-MacBeth regression, IC/ICIR evaluation, and comprehensive reporting.

## Workflow

- **Factor Module**
  - Single Factor Evaluation ([docs](docs/doc_single_factor_evaluation.md))
- **Model Module**
  - Multi-Factor Model Evaluation ([docs](docs/doc_factor_model.md))

## Key Features

- **Single Factor Evaluation**: Sort and regression methods, IC/ICIR, group stats, cumulative returns, and automated Markdown reporting.
- **Multi-Factor Model**: Fama-MacBeth cross-sectional regression, t-tests, and interpretable output tables.
- **Data Export**: All input and output data saved as CSV for further analysis.
- **Plotting**: All key plots (IC, group means, histograms, cumulative returns) saved for reporting.

## Example Usage

```python
from bagel_factor.single_factor_evaluation.factor_evaluation import evaluate_factor

evaluate_factor(
    factor_data,  # DataFrame: date x ticker
    stock_next_returns,  # DataFrame: date x ticker
    output_path=Path('output/'),
    sorting_group_num=10,
    factor_name='Momentum',
    factor_description='12-1M momentum factor'
)
```

For multi-factor model evaluation:

```python
from bagel_factor.factor_model.factor_model import FactorModel

model = FactorModel(factor_loadings, factor_returns)
print(model.regression_params)
print(model.t_test_table)
```

## Documentation

- [Single Factor Evaluation](docs/doc_single_factor_evaluation.md)
- [Factor Model (Fama-MacBeth)](docs/doc_factor_model.md)

## References

- [BagelQuant: Factor Models](https://bagelquant.com/factor-models/)
- Fama, E. F., & MacBeth, J. D. (1973). Risk, Return, and Equilibrium: Empirical Tests. *Journal of Political Economy*, 81(3), 607-636.

## License

MIT License

