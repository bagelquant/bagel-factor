# Project Structure

## Whole Project Structure

```plaintext
bagel-factor/
├── docs/
│   ├── project_structure.md
│   ├── v_2_0_0_proposal.md
│   └── ...
├── src/                            # Source code directory
│   └── bagel_factor/
│       ├── __init__.py
│       └── ...
├── tests/
│   └── ...
├── examples/
│   ├── example_notebook_1.ipynb
│   └── ...
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Source Code Structure

```plaintext
bagel_factor/
├── __init__.py                     # Package initialization
├── evaluator.py                    # Interface: main class for factor evaluation
├── visualizer.py                   # Interface: Class for visualization and exporting results
├── data_handling/                # Module for data input, validation, and preprocessing
│   ├── __init__.py
│   ├── factor_data.py              # Class for handling factor data
│   └── preprocessing.py            # Preprocessing methods (e.g., winsorization, z-score)
├── metrics/                      # Module for performance metric calculations
│   ├── __init__.py
│   ├── ic.py                       # Information Coefficient calculations
│   ├── quantile_returns.py         # Quantile return analysis
│   └── risk_metrics.py             # Risk and return metrics (Sharpe, Sortino, drawdown)
├── visualization/                # Module for plotting and exporting results
│   ├── __init__.py
│   ├── plots.py                    # Plotting functions
│   └── export.py                   # Exporting results to files
└── utils/                        # Utility functions
    ├── __init__.py
    └── helpers.py                  # Helper functions
```
