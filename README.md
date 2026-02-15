# bagel-factor

[![CI](https://github.com/bagelquant/bagel-factor/workflows/CI/badge.svg)](https://github.com/bagelquant/bagel-factor/actions)
[![PyPI](https://img.shields.io/pypi/v/bagel-factor)](https://pypi.org/project/bagel-factor/)
[![Python](https://img.shields.io/pypi/pyversions/bagel-factor)](https://pypi.org/project/bagel-factor/)
[![License](https://img.shields.io/github/license/bagelquant/bagel-factor)](https://github.com/bagelquant/bagel-factor/blob/main/LICENSE)

A **pandas-first toolkit** for single-factor evaluation in quantitative finance.

## What is this?

`bagel-factor` helps you answer: **"Does my factor predict future returns?"**

Given a factor (signal) and price data, it computes:
- ✅ **IC/ICIR** - Information coefficient (predictive correlation)
- ✅ **Quantile returns** - Performance by factor bucket
- ✅ **Long-short spread** - Top-minus-bottom returns
- ✅ **Turnover** - Trading cost implications
- ✅ **Coverage** - Data quality metrics
- ✅ **Statistical tests** - Significance testing

**Perfect for**: Alpha researchers, quant traders, and anyone evaluating predictive signals.

## Scope (by design)

**What it does**:
- 📊 Canonical point-in-time panel data structure (`date × asset`)
- 🔄 Preprocessing transforms (clip/zscore/rank)
- 📈 Single-factor evaluation metrics
- 📉 Publication-quality visualizations
- 🧪 Statistical testing

**What it doesn't do** (by design):
- ❌ Multi-factor portfolio optimization
- ❌ Backtesting with transaction costs
- ❌ Risk model construction
- ❌ Position sizing / execution

This is a **precision calculation engine** for factor evaluation, not a full backtesting framework.

## Install

Requires Python >=3.12

```bash
pip install bagel-factor
```

## Install (dev / from source)

This repo is managed with [`uv`](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Quick Example

```python
from bagelfactor import SingleFactorJob, plot_result_summary

# Run evaluation
res = SingleFactorJob.run(
    panel,                    # Your data: (date, asset) indexed DataFrame
    factor="alpha",           # Factor column name
    price="close",            # Price column for forward returns
    horizons=(1, 5, 20),      # Evaluate 1, 5, and 20-period returns
    n_quantiles=5,            # Split into 5 buckets
)

# Check results
print(f"IC: {res.ic[5].mean():.3f}")
print(f"ICIR: {res.icir[5]:.2f}")
print(f"Sharpe: {res.long_short[5].mean() / res.long_short[5].std():.2f}")

# Visualize
fig = plot_result_summary(res, horizon=5)
fig.show()
```

**Output**: A comprehensive 4×2 plot showing IC, quantile returns, long-short performance, turnover, and coverage.

---

## Installation

Requires Python ≥3.12

```bash
pip install bagel-factor
```

---

## User Guide

### Step-by-Step Tutorial

#### 0) Data preparation (CRITICAL)

Before using bagel-factor, ensure your data meets these requirements:

```python
import pandas as pd
from bagelfactor.data import ensure_panel_index, lag_by_asset

# 1. Load your data
df = pd.read_csv("your_data.csv")

# 2. Create canonical panel index
panel = ensure_panel_index(df, date="date", asset="ticker")

# 3. CRITICAL: Sort the panel
panel = panel.sort_index()

# 4. Lag factors to avoid lookahead bias
# (If factor data is "as-of" date t, use it starting from t+1)
panel = lag_by_asset(panel, columns=["your_factor"], periods=1)
```

**⚠️ Critical**: Unsorted data produces incorrect results. Point-in-time integrity is your responsibility.  
📖 See [Data Format Requirements](./docs/data_format_requirements.md) for complete guide.

#### 1) Prepare a canonical panel

Most APIs expect a canonical **panel**:
- `pd.DataFrame`
- indexed by `pd.MultiIndex` with names `("date", "asset")`

```python
import pandas as pd
from bagelfactor.data import ensure_panel_index

raw = pd.DataFrame(
    {
        "date": ["2020-01-01", "2020-01-01"],
        "asset": ["A", "B"],
        "close": [10.0, 20.0],
        "alpha": [1.0, 2.0],
    }
)

panel = ensure_panel_index(raw)
panel = panel.sort_index()  # ← CRITICAL: Always sort!
```

#### 2) (Optional) preprocess the factor

```python
from bagelfactor.preprocess import Clip, Pipeline, Rank, ZScore

preprocess = Pipeline([
    Clip("alpha", lower=0.0, upper=2.0),
    ZScore("alpha"),
    Rank("alpha"),
])
```

#### 3) Run single-factor evaluation

```python
from bagelfactor import SingleFactorJob

res = SingleFactorJob.run(
    panel,
    factor="alpha",          # Factor column name
    price="close",           # Price for computing returns
    horizons=(1, 5, 20),     # Multiple forward-return windows
    n_quantiles=5,           # Number of buckets (quintiles)
    preprocess=preprocess,   # Optional
)
```

**What you get**:

```python
# Information Coefficient (per horizon)
res.ic[1]           # Daily IC time series
res.icir[1]         # IC Information Ratio

# Quantile analysis
res.quantile_returns[5]   # Mean returns per quantile (5-day horizon)
res.long_short[5]         # Top minus bottom returns

# Diagnostics
res.coverage        # Data availability
res.turnover        # Trading cost proxy
```

#### 4) Interpret results

**Quick health check**:

```python
h = 5  # 5-day horizon

# 1. Check IC
ic_mean = res.ic[h].mean()
print(f"Mean IC: {ic_mean:.4f}")  # Want: 0.03-0.10 (positive or negative)

# 2. Check stability
icir = res.icir[h]
print(f"ICIR: {icir:.2f}")  # Want: > 0.5

# 3. Check economic significance
ls_mean = res.long_short[h].mean()
ls_std = res.long_short[h].std()
sharpe = ls_mean / ls_std if ls_std > 0 else 0
print(f"L/S Sharpe: {sharpe:.2f}")  # Want: > 0.5

# 4. Check tradability
turnover = res.turnover.mean()
print(f"Avg turnover: {turnover:.1%}")  # Want: < 40%
```

📖 **Complete interpretation guide**: [Result Interpretation Guide](./docs/interpretation_guide.md)

#### 5) Visualize results

```python
from bagelfactor import plot_result_summary

# All-in-one summary (4×2 grid)
fig = plot_result_summary(res, horizon=5)
fig.savefig('factor_summary.png', dpi=150)
```

**Or use individual plots**:

```python
from bagelfactor import (
    plot_ic_time_series,
    plot_quantile_cumulative_returns,
    plot_long_short_time_series,
)

# IC over time
plot_ic_time_series(res.ic[5], rolling=20)

# Cumulative wealth by quantile
plot_quantile_cumulative_returns(res.quantile_returns[5])

# Long-short equity curve
plot_long_short_time_series(res.long_short[5], cumulative=True)
```

#### 6) Statistical tests

```python
from bagelfactor import ttest_1samp, ols_alpha_tstat

# Test if mean IC is significantly different from 0
ic_test = ttest_1samp(res.ic[5], popmean=0.0)
print(f"IC t-stat: {ic_test.statistic:.2f}, p-value: {ic_test.pvalue:.4f}")

# Test if long-short has significant alpha
ls_alpha = ols_alpha_tstat(res.long_short[5])
print(f"L/S alpha t-stat: {ls_alpha.tstat:.2f}")

# Interpretation:
# |t-stat| > 2: Significant at ~5% level
# |t-stat| > 3: Strong evidence
```

#### 7) (Optional) Validate your data

Use the diagnostic utility to check for common issues:

```python
from bagelfactor import diagnose_panel

diag = diagnose_panel(panel)
print(diag)
```

**Example output**:
```
Panel Diagnostics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Valid MultiIndex with names ['date', 'asset']
✓ Index is sorted
✓ No duplicate entries
⚠ Missing data: 5.2% of values are NaN
  Date range: 2020-01-01 to 2023-12-31 (1000 dates)
  Assets: 500 unique
```

---

## Understanding Results

### What do these metrics mean?

| Metric | What it measures | Good range | Red flag |
|--------|------------------|------------|----------|
| **IC** | Cross-sectional correlation with returns | 0.03-0.10 | < 0.01 |
| **ICIR** | IC stability (mean/std) | > 0.5 | < 0.2 |
| **Quantile spread** | Q5 - Q1 average return | Context-dependent | Non-monotonic |
| **Turnover** | Portfolio changes between periods | < 30% (daily) | > 60% |
| **Coverage** | Data availability | > 90% | < 80% |

📖 **Detailed interpretation**: [Result Interpretation Guide](./docs/interpretation_guide.md)

### Example: Good vs Concerning Factor

**✅ Good Factor**:
```
IC: 0.045, ICIR: 1.2
Quantiles: Q1=-0.8%, Q2=-0.1%, Q3=0.2%, Q4=0.6%, Q5=1.2%
L/S Sharpe: 1.8
Turnover: 25%
Coverage: 95%
```
→ Strong, stable signal with monotonic quantiles and reasonable turnover.

**⚠️ Concerning Factor**:
```
IC: 0.015, ICIR: 0.3
Quantiles: Q1=0.2%, Q2=-0.5%, Q3=0.8%, Q4=-0.2%, Q5=0.3%
L/S Sharpe: 0.4
Turnover: 65%
Coverage: 75%
```
→ Weak, unstable signal with non-monotonic quantiles, high turnover, and data quality issues.

---

## Documentation

### Getting Started

- 🚀 **[Quick Start (above)](#quick-example)** - 5-minute intro
- 📊 **[Result Interpretation Guide](./docs/interpretation_guide.md)** - How to understand your results
- ⚠️ **[Data Format Requirements](./docs/data_format_requirements.md)** - Critical data prep guide
- 📝 **[Complete Example](./docs/example.md)** - Full workflow with outputs
- 📚 **[Factor Evaluation Theory](./docs/factor_evaluation.md)** - Statistical background

### Complete Example

```bash
# Run the included example
uv run python examples/example.py

# View outputs in examples/outputs/
```

Full example with expected outputs: [`docs/example.md`](./docs/example.md).

---

## Performance

Optimized vectorized implementations:

| Metric | Speedup | Notes |
|--------|---------|-------|
| IC | 4-5x | Vectorized correlation |
| Coverage | 20-30x | Single pass counting |
| Quantiles | 10x+ | Optimized groupby |

Reproduce: `uv run python examples/benchmark_ic.py`

## API Reference

### Table of contents

- **Getting started**
  - 🚀 [Quick Start](#quick-example) (in README above)
  - 📊 **[Result Interpretation Guide](./docs/interpretation_guide.md)** ⭐ Start here for understanding results!
  - ⚠️ **[Data Format Requirements](./docs/data_format_requirements.md)** - Critical for correct results
  - 📝 [Complete Example](./docs/example.md) - Full workflow with outputs
  - 📚 [Factor Evaluation Theory](./docs/factor_evaluation.md) - Statistical background

- **Modules** (API reference)
  - [`bagelfactor.data`](./docs/modules/data.md)
    - [data/index](./docs/modules/data/index.md)
    - [data/panel](./docs/modules/data/panel.md)
    - [data/loaders](./docs/modules/data/loaders.md)
    - [data/loaders internal](./docs/modules/data/loaders_internal.md)
    - [data/align](./docs/modules/data/align.md)
    - [data/calendar](./docs/modules/data/calendar.md)
    - [data/factors](./docs/modules/data/factors.md)
    - [data/universe](./docs/modules/data/universe.md)

  - [`bagelfactor.metrics`](./docs/modules/metrics/index.md)
    - [metrics/ic](./docs/modules/metrics/ic.md)
    - [metrics/quantiles](./docs/modules/metrics/quantiles.md)
    - [metrics/turnover](./docs/modules/metrics/turnover.md)
    - [metrics/coverage](./docs/modules/metrics/coverage.md)

  - [`bagelfactor.preprocess`](./docs/modules/preprocess/index.md)
    - [preprocess/pipeline](./docs/modules/preprocess/pipeline.md)
    - [preprocess/transforms](./docs/modules/preprocess/transforms.md)

  - [`bagelfactor.single_factor`](./docs/modules/single_factor/index.md)
    - [single_factor/job](./docs/modules/single_factor/job.md)
    - [single_factor/result](./docs/modules/single_factor/result.md)

  - [`bagelfactor.visualization`](./docs/modules/visualization/index.md)
    - [visualization/single_factor](./docs/modules/visualization/single_factor.md)

  - [`bagelfactor.stats`](./docs/modules/stats/index.md)
    - [stats/tests](./docs/modules/stats/tests.md)
    - [stats/regression](./docs/modules/stats/regression.md)

  - [`bagelfactor.reporting`](./docs/modules/reporting/index.md)
    - [reporting/export](./docs/modules/reporting/export.md)

- **Design docs**
  - [v0 proposals](./docs/proposals/proposals_v0.md)

---

## Install (dev / from source)

This repo uses [`uv`](https://github.com/astral-sh/uv) for development:

```bash
git clone https://github.com/bagelquant/bagel-factor.git
cd bagel-factor
uv sync
uv run pytest  # Run tests
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

---

## FAQ

**Q: What's the difference between IC and RankIC?**  
A: IC uses Pearson correlation (linear), RankIC uses Spearman (rank-based). RankIC is more robust to outliers.

**Q: Why is my IC negative?**  
A: Negative IC means higher factor values predict lower returns. Consider inverting your factor (multiply by -1).

**Q: What IC value is "good"?**  
A: Context-dependent, but for daily equity factors: 0.03-0.06 is solid, >0.10 is exceptional (or suspicious—check for data leakage).

**Q: My quantile returns aren't monotonic. Is that bad?**  
A: Yes, it suggests the factor doesn't cleanly order assets. Check data quality, try different preprocessing, or investigate non-linear relationships.

**Q: How do I handle missing data?**  
A: The package handles NaN gracefully (cross-sectional operations skip missing values). But check coverage—if it's low, your results may be biased.

**Q: Can I use this for non-equity asset classes?**  
A: Yes! The package is asset-class agnostic. Just provide a `(date, asset)` panel with factor and price data.

📖 More details: [Interpretation Guide](./docs/interpretation_guide.md)

---

## Citation

If you use `bagel-factor` in academic research, please cite:

```bibtex
@software{bagel_factor,
  title = {bagel-factor: A pandas-first toolkit for single-factor evaluation},
  author = {{Bagel Quant}},
  year = {2024},
  url = {https://github.com/bagelquant/bagel-factor}
}
```

---

## License

MIT (see [`LICENSE`](./LICENSE)).
