# Single Factor Evaluation

This document describes the methodology and reporting format for evaluating a single factor in the Bagel Factor framework. The evaluation combines both sorting and regression methods, generates a comprehensive Markdown report, and saves all plots in a dedicated subfolder.

The evaluation method details in [bagelquant](https://bagelquant.com/factor-models/single-factor-evaluation/) provide a foundation for this process, ensuring that the evaluation is standardized and reproducible.

## Overview

Single factor evaluation is a critical step in quantitative research. It helps determine whether a candidate factor has predictive power and stability for asset returns. The Bagel Factor evaluation module provides a standardized, reproducible process for this analysis.

## Evaluation Workflow

1. **Input Data**
   - `factor_data`: DataFrame with dates as index and tickers as columns, containing the factor values.
   - `stock_next_returns`: DataFrame with dates as index and tickers as columns, containing the next period returns.
   - Both DataFrames must:
     - Use the same time index (rebalance dates) and ticker columns
     - Be aligned in shape and order

2. **Evaluation Methods**
   - **Sorting Method**: Stocks are sorted into groups (e.g., deciles) by factor value. Group returns and high-minus-low (H-L) returns are analyzed.
   - **Regression Method**: Cross-sectional regression of next returns on factor values for each date. The regression coefficient series is analyzed. Multiple regression methods are supported:
     - `OLS`: Ordinary Least Squares
     - `WLS`: Weighted Least Squares (optional weights)
     - `RLM`: Robust Linear Model
   - The regression can be run with or without an intercept.

3. **Metrics and Plots**
   - Mean and standard deviation of factor returns
   - Information Coefficient (IC) and ICIR (IC mean / IC std)
   - Group statistics (mean, std, t-stat, p-value)
   - Cumulative returns
   - Histograms and time series plots

4. **Markdown Report**
   - Highlight section with key metrics
   - Detailed sections for sorting and regression methods
   - All plots saved in a `plots/` subfolder and referenced in the report

5. **Data Export for Further Analysis**
   - All relevant input and output data are automatically saved as CSV files for further analysis:
     - `data/input/stock_next_returns.csv`: The input next-period returns DataFrame.
     - `data/input/factor_data.csv`: The input factor values DataFrame.
     - `data/sort_group_portfolios_next_returns.csv`: Grouped portfolio returns from the sorting method.
     - `data/sort_factor_next_returns.csv`: High-minus-low (H-L) returns from the sorting method.
     - `data/sort_ICs.csv`: Information Coefficient (IC) time series for the sorting method.
     - `data/regression_factor_next_returns.csv`: Regression factor returns (cross-sectional regression coefficients).
     - `data/regression_ICs.csv`: Information Coefficient (IC) time series for the regression method.
   - These files are created in the `data/` and `data/input/` subfolders of your project, making it easy to conduct further custom analysis or validation outside the main evaluation workflow.

## Report Structure

### 1. Highlight Table

A summary table of key metrics for both methods:

| Method      | Factor Mean | Factor Std | IC (mean) | ICIR  |
|-------------|-------------|------------|-----------|-------|
| Sort        | ...         | ...        | ...       | ...   |
| Regression  | ...         | ...        | ...       | ...   |

**Interpretation:**

- IC > 0.15: strong predictive power
- ICIR > 0.5: good consistency
- ICIR > 1.0: very strong and stable factor

### 2. Sorting Method Evaluation

- Group statistics table (mean, std, t-stat, p-value)
- Plots:
  - Mean returns by group
  - ICs over time
  - Cumulative returns (Low, High, H-L)
  - Histogram of H-L returns

### 3. Regression Method Evaluation

- ICs and ICIR table
- t-test for regression coefficient series
- Plots:
  - ICs over time
  - Histogram of Pearson and Spearman ICs
  - Histogram of regression coefficient series
- **Regression Options:**
  - Regression method can be set to `OLS`, `WLS`, or `RLM`.
  - Intercept can be included or excluded.
  - Optional weights can be provided for `WLS`.

### 4. Data Export for Further Analysis

All relevant input and output data are automatically saved as CSV files for further analysis:

- `data/input/stock_next_returns.csv`: The input next-period returns DataFrame.
- `data/input/factor_data.csv`: The input factor values DataFrame.
- `data/sort_group_portfolios_next_returns.csv`: Grouped portfolio returns from the sorting method.
- `data/sort_factor_next_returns.csv`: High-minus-low (H-L) returns from the sorting method.
- `data/sort_ICs.csv`: Information Coefficient (IC) time series for the sorting method.
- `data/regression_factor_next_returns.csv`: Regression factor returns (cross-sectional regression coefficients).
- `data/regression_ICs.csv`: Information Coefficient (IC) time series for the regression method.

These files are created in the `data/` and `data/input/` subfolders of your project, making it easy to conduct further custom analysis or validation outside the main evaluation workflow.

## Example Output (Excerpt)

```markdown
# ExampleFactor Evaluation Results

Description: Example factor for demonstration

## Highlight

| Method     | Factor Mean | Factor Std | IC (mean) | ICIR  |
|------------|-------------|------------|-----------|-------|
| Sort       | 0.0123      | 0.0345     | 0.21      | 0.88  |
| Regression | 0.0111      | 0.0312     | 0.19      | 0.75  |

**Interpretation:**

- IC > 0.15: strong predictive power
- ICIR > 0.5: good consistency
- ICIR > 1.0: very strong and stable factor

## FactorSort Evaluation

### Group Statistics

|       | n_t | mean   | std    | t_stat | p_value |
|-------|-----|--------|--------|--------|---------|
| 1     | ... | ...    | ...    | ...    | ...     |
| ...   | ... | ...    | ...    | ...    | ...     |
| H-L   | ... | ...    | ...    | ...    | ...     |

![Mean Returns by Group](plots/group_means.png)

### ICs and ICIR

|       | pearson | spearman |
|-------|---------|----------|
| mean  | ...     | ...      |
| std   | ...     | ...      |
| ...   | ...     | ...      |

ICIR Table:

|       | ICs mean | std  | ICIR |
|-------|----------|------|------|
|pearson| ...      | ...  | ...  |
|spearman| ...     | ...  | ...  |

![ICs over Time](plots/ics.png)

### Accumulated Returns

|       | Low | High | H-L |
|-------|-----|------|-----|
| ...   | ... | ...  | ... |

![Cumulative Returns](plots/accumulated_returns.png)

### Histogram of Factor Returns

![Factor Next Returns Distribution](plots/factor_next_returns_hist.png)

## FactorRegression Evaluation

### ICs and ICIR for Regression Method

|       | pearson | spearman |
|-------|---------|----------|
| mean  | ...     | ...      |
| std   | ...     | ...      |
| ...   | ...     | ...      |

ICIR Table:

|       | ICs mean | std  | ICIR |
|-------|----------|------|------|
|pearson| ...      | ...  | ...  |
|spearman| ...     | ...  | ...  |

![ICs over Time](plots/ics_regression.png)

### ICs Histogram (Pearson)

![Pearson ICs Distribution](plots/ics_pearson_hist_regression.png)

### ICs Histogram (Spearman)

![Spearman ICs Distribution](plots/ics_spearman_hist_regression.png)

### t-test for factor_next_returns

T-statistic: ... , p-value: ...

### Histogram of Factor Returns (Regression)

![Factor Next Returns Distribution (Regression)](plots/factor_next_returns_hist_regression.png)
```

## References

- [Single Factor Test](https://bagelquant.com/factor-models/single-factor-test/)
- Bagel Factor documentation
