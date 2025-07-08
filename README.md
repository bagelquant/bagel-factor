# Bagel Factor

## Overview

Bagel Factor is a modular Python library for quantitative equity research. It supports the full workflow from data collection to multi-factor model evaluation and backtesting. The library provides standardized, reproducible tools for both single-factor and multi-factor analysis, including Fama-MacBeth regression, IC/ICIR evaluation, and comprehensive reporting.

## Workflow (Modules)

- Data
    - standard data format
- Preprocessing
    - standardize
    - outlier
    - missing
- Data validation
- Evaluation
    - IC: time-series of IC
    - Grouping evaluation
        - time-series of portfolio returns(groups)
    - Regression
        - time-series of factor return(regression slop)
- Report
    - summary table: IC, IC standard deviation, ICIR, factor_return, t-test factor_return
    - plots
