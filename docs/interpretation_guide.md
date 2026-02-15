# Result Interpretation Guide

A practical guide to understanding and interpreting single-factor evaluation results from `bagel-factor`.

## Quick Reference

| Metric | Good Range | Interpretation | What to Check |
|--------|-----------|----------------|---------------|
| **IC (mean)** | 0.03-0.10 | Factor's predictive power | Sign matches expectation |
| **ICIR** | > 0.5 | Signal stability | Consistency across time |
| **Coverage** | > 0.90 | Data availability | Missing data patterns |
| **Quantile Spread** | Context-dependent | Economic significance | Monotonic ordering |
| **Turnover** | < 0.3 (daily) | Trading costs | Stability vs IC tradeoff |

---

## Understanding SingleFactorResult

When you run:

```python
from bagelfactor import SingleFactorJob

res = SingleFactorJob.run(
    panel,
    factor="alpha",
    price="close",
    horizons=(1, 5, 20),
    n_quantiles=5,
)
```

You get a `SingleFactorResult` object with these attributes:

### Core Metrics (per horizon)

```python
res.ic[h]              # IC time series for horizon h
res.icir[h]            # ICIR summary statistic
res.quantile_returns[h]  # Mean returns per quantile
res.long_short[h]      # Top minus bottom quantile returns
```

### Additional Diagnostics

```python
res.coverage           # Data availability over time
res.turnover           # Quantile membership changes
res.factor             # Factor name used
res.horizons           # List of horizons evaluated
```

---

## 1. Information Coefficient (IC)

### What It Is

IC measures the **cross-sectional correlation** between your factor and forward returns at each date.

**Mathematical definition** (per date t):
```
IC_t = correlation(factor_values_t, forward_returns_t)
```

Across all assets at date t, IC tells you:
- **Positive IC**: Higher factor → higher returns
- **Negative IC**: Higher factor → lower returns
- **Zero IC**: No relationship

### How to Interpret

**Magnitude** (absolute value):

| Range | Interpretation | Action |
|-------|----------------|--------|
| < 0.01 | Noise | ❌ Likely not useful |
| 0.01-0.03 | Weak | ⚠️ Needs validation |
| 0.03-0.06 | Good | ✅ Promising signal |
| 0.06-0.10 | Strong | ✅ Excellent |
| > 0.10 | Exceptional | ⚠️ Check for data leakage! |

**Sign**:
```python
mean_ic = res.ic[5].mean()

if mean_ic > 0:
    print("Higher factor → higher returns (positive alpha factor)")
elif mean_ic < 0:
    print("Higher factor → lower returns (consider inverting)")
else:
    print("No clear relationship")
```

**Time series patterns**:

```python
from bagelfactor import plot_ic_time_series

# Visualize IC over time
plot_ic_time_series(res.ic[5], rolling=20)
```

Look for:
- ✅ **Consistent sign**: Mostly positive or mostly negative
- ⚠️ **Regime changes**: IC flips sign across periods
- ❌ **Random walk**: IC oscillates wildly without pattern

### Example: Good vs Bad IC

**Good IC (stable positive)**:
```
date
2020-01-01    0.045
2020-01-02    0.062
2020-01-03    0.038
2020-01-06    0.051
2020-01-07    0.049
...
Mean: 0.048, Std: 0.015 → ICIR = 3.2
```

**Bad IC (noisy)**:
```
date
2020-01-01    0.023
2020-01-02   -0.018
2020-01-03    0.041
2020-01-06   -0.035
2020-01-07    0.009
...
Mean: 0.004, Std: 0.028 → ICIR = 0.14
```

---

## 2. ICIR (Information Coefficient Information Ratio)

### What It Is

ICIR measures the **stability** of your IC:

```
ICIR = mean(IC) / std(IC)
```

Similar to a Sharpe ratio but for IC instead of returns.

### How to Interpret

| ICIR | Quality | Meaning |
|------|---------|---------|
| < 0.2 | Weak | Unreliable signal |
| 0.2-0.5 | Modest | May work with large sample |
| 0.5-1.0 | Good | Solid factor |
| 1.0-2.0 | Strong | Excellent factor |
| > 2.0 | Exceptional | Very rare—verify! |

### Why It Matters

**High mean IC + low ICIR** = Unstable signal
- Works great sometimes, fails others
- Hard to size positions
- Risky in live trading

**Moderate IC + high ICIR** = Reliable signal  
- Consistent performance
- Easier to trade
- More predictable

### Example Comparison

```python
# Factor A: High IC, low stability
ic_a = pd.Series([0.10, -0.05, 0.15, -0.08, 0.12])
icir_a = ic_a.mean() / ic_a.std()  # 0.048 / 0.096 = 0.50

# Factor B: Moderate IC, high stability
ic_b = pd.Series([0.04, 0.05, 0.05, 0.04, 0.05])
icir_b = ic_b.mean() / ic_b.std()  # 0.046 / 0.005 = 9.2

# Factor B is more reliable despite similar mean IC!
```

---

## 3. Quantile Returns

### What They Are

Assets are sorted by factor value and split into buckets (quantiles) each date.

For **n_quantiles=5**:
- **Q1**: Bottom 20% (lowest factor values)
- **Q2**: 20-40%
- **Q3**: 40-60%
- **Q4**: 60-80%
- **Q5**: Top 20% (highest factor values)

`res.quantile_returns[h]` shows the mean forward return for each bucket.

### How to Interpret

**Look for monotonicity**:

✅ **Good pattern** (ascending):
```
Quantile    Mean Return
Q1          -0.5%
Q2           0.2%
Q3           0.8%
Q4           1.5%
Q5           2.3%
```
Clear progression from worst to best.

❌ **Bad pattern** (non-monotonic):
```
Quantile    Mean Return
Q1           0.8%
Q2          -0.3%
Q3           1.2%
Q4           0.5%
Q5           0.9%
```
No clear relationship—factor doesn't order assets well.

### Visualization

```python
from bagelfactor import (
    plot_quantile_returns_time_series,
    plot_quantile_cumulative_returns,
    plot_quantile_returns_heatmap
)

# Period-over-period returns
plot_quantile_returns_time_series(res.quantile_returns[5])

# Cumulative wealth (shows long-term divergence)
plot_quantile_cumulative_returns(res.quantile_returns[5])

# Heatmap view (spot patterns)
plot_quantile_returns_heatmap(res.quantile_returns[5])
```

### What to Check

1. **Spread (Q5 - Q1)**:
   ```python
   spread = res.quantile_returns[5][5] - res.quantile_returns[5][1]
   mean_spread = spread.mean()
   print(f"Average spread: {mean_spread*100:.2f}% per period")
   ```
   - Larger spread = stronger factor
   - Must exceed transaction costs

2. **Consistency**:
   ```python
   # What % of time does Q5 beat Q1?
   win_rate = (spread > 0).mean()
   print(f"Win rate: {win_rate*100:.1f}%")
   ```
   - 60-70% is typical for good factors
   - < 55% suggests noise

3. **Middle quantiles**:
   - Should show intermediate performance
   - Abrupt jumps suggest factor threshold effects

---

## 4. Long-Short Returns

### What It Is

**Long-Short** = Top quantile return - Bottom quantile return

```python
ls_returns = res.long_short[h]  # Q_top - Q_bottom per date
```

This is your **factor spread** or **alpha**.

### How to Interpret

**Positive long-short** means:
- Going **long** high-factor assets
- Going **short** low-factor assets
- Would have generated positive returns

### Key Statistics

```python
# Summary statistics
mean_ls = ls_returns.mean()
std_ls = ls_returns.std()
sharpe = mean_ls / std_ls if std_ls > 0 else 0

print(f"Mean L/S: {mean_ls*100:.3f}%")
print(f"Volatility: {std_ls*100:.3f}%")
print(f"Sharpe: {sharpe:.2f}")

# Cumulative performance
cumulative = (1 + ls_returns).cumprod() - 1
final_return = cumulative.iloc[-1]
print(f"Total return: {final_return*100:.1f}%")
```

### Visualization

```python
from bagelfactor import plot_long_short_time_series

# Period returns
plot_long_short_time_series(res.long_short[5], cumulative=False)

# Cumulative returns (equity curve)
plot_long_short_time_series(res.long_short[5], cumulative=True)
```

**What to look for**:
- ✅ Smooth upward trend (cumulative)
- ✅ Positive mean with manageable volatility
- ⚠️ Large drawdowns
- ❌ Flat or declining equity curve

### Statistical Testing

```python
from bagelfactor import ttest_1samp, ols_alpha_tstat

# Test if mean is significantly different from 0
t_test = ttest_1samp(ls_returns, popmean=0.0)
print(f"t-statistic: {t_test.statistic:.2f}")
print(f"p-value: {t_test.pvalue:.4f}")

# Test intercept (alpha)
ols_result = ols_alpha_tstat(ls_returns)
print(f"Alpha t-stat: {ols_result.tstat:.2f}")
```

**Interpretation**:
- |t-stat| > 2: Significant at ~5% level
- |t-stat| > 3: Strong evidence
- p-value < 0.05: Reject null (mean ≠ 0)

---

## 5. Coverage

### What It Is

**Coverage** = fraction of assets with valid (non-NaN) factor values per date.

```python
coverage_pct = res.coverage.mean() * 100
print(f"Average coverage: {coverage_pct:.1f}%")
```

### How to Interpret

| Coverage | Assessment | Notes |
|----------|-----------|-------|
| > 95% | Excellent | Full universe coverage |
| 90-95% | Good | Acceptable missingness |
| 80-90% | Moderate | Check patterns |
| < 80% | Concerning | May bias results |

### What to Check

```python
from bagelfactor import plot_coverage_time_series

# Visualize over time
plot_coverage_time_series(res.coverage)

# Find problem dates
low_coverage = res.coverage[res.coverage < 0.9]
if len(low_coverage) > 0:
    print(f"Dates with <90% coverage:\n{low_coverage}")
```

**Questions to ask**:
1. Is low coverage random or systematic?
2. Does the factor only work when coverage is high?
3. Are missing values related to asset characteristics?

### Example Issue

```
date        coverage
2020-01-01  0.95
2020-01-02  0.94
...
2020-03-15  0.45  ← Sudden drop
2020-03-16  0.43
...
2020-04-01  0.93  ← Recovered
```

This suggests a data quality issue in mid-March. Results during this period may be unreliable.

---

## 6. Turnover

### What It Is

**Turnover** measures how much quantile membership changes between consecutive dates.

For each quantile q:
```
turnover_t,q = 1 - (intersection / union)
```

Where:
- intersection = assets in quantile q at both t-1 and t
- union = assets in quantile q at either t-1 or t

### How to Interpret

| Turnover | Tradability | Notes |
|----------|-------------|-------|
| < 0.2 | High | Low costs |
| 0.2-0.4 | Moderate | Manageable |
| 0.4-0.6 | Low | High costs |
| > 0.6 | Very low | Likely unprofitable |

### Why It Matters

**High turnover** = high transaction costs:
- Bid-ask spread
- Market impact
- Commissions/fees
- Operational complexity

A factor with IC=0.05 but 70% turnover may be unprofitable, while IC=0.03 with 15% turnover could be very profitable.

### Visualization

```python
from bagelfactor import plot_turnover_time_series, plot_turnover_heatmap

# Average across quantiles
plot_turnover_time_series(res.turnover, average=True)

# Per-quantile view
plot_turnover_time_series(res.turnover, average=False)

# Heatmap
plot_turnover_heatmap(res.turnover)
```

### Analysis

```python
# Average turnover per quantile
avg_turnover = res.turnover.groupby(level='quantile').mean()
print("Average turnover by quantile:")
print(avg_turnover)

# Overall average
overall_avg = res.turnover.mean()
print(f"\nOverall average turnover: {overall_avg:.2%}")
```

**Typical patterns**:
- **Extreme quantiles (Q1, Q5)** usually have lower turnover (strongest signals persist)
- **Middle quantiles (Q2-Q4)** may have higher turnover (weak signals flip easily)

---

## 7. Multi-Horizon Analysis

When you specify `horizons=(1, 5, 20)`, check:

### 1. How does IC change with horizon?

```python
ic_summary = pd.DataFrame({
    h: {
        'mean': res.ic[h].mean(),
        'std': res.ic[h].std(),
        'icir': res.icir[h]
    }
    for h in res.horizons
}).T

print(ic_summary)
```

**Typical patterns**:
- **Shorter horizons** (1-5 days): Higher IC, more noise
- **Longer horizons** (20+ days): Lower IC, smoother
- **Decay**: IC typically decays with horizon for most factors

### 2. Which horizon has best risk-adjusted returns?

```python
for h in res.horizons:
    ls = res.long_short[h]
    sharpe = ls.mean() / ls.std() if ls.std() > 0 else 0
    print(f"Horizon {h:2d}: Sharpe = {sharpe:.3f}")
```

### 3. Turnover vs IC tradeoff

```python
# Compare turnover at different horizons
# (Note: turnover is not horizon-specific in current implementation)
# But you can analyze rebalancing frequency implications
```

---

## 8. Summary Visualization

The easiest way to get an overview:

```python
from bagelfactor import plot_result_summary

# Default: shows cumulative returns
fig = plot_result_summary(res, horizon=5)
fig.savefig('factor_analysis.png', dpi=150, bbox_inches='tight')

# Alternative: show period returns
fig = plot_result_summary(res, horizon=5, cumulative=False)
```

This creates a **4×2 grid**:
- Row 0: IC time series | IC distribution
- Row 1: Quantile cumulative returns | Quantile heatmap
- Row 2: Long-short period | Long-short cumulative
- Row 3: Turnover | Coverage

**Quick assessment**:
1. IC time series: Look for consistency
2. IC histogram: Should cluster away from zero
3. Quantile cumulative: Q5 should outperform Q1
4. Heatmap: Look for vertical stripes (good) vs checkered (noisy)
5. Long-short: Should trend upward (cumulative)
6. Turnover: Should be reasonable (<40%)
7. Coverage: Should be high and stable

---

## 9. Red Flags Checklist

⚠️ **Warning signs** that suggest problems:

### Data Quality Issues
- [ ] Coverage drops suddenly
- [ ] IC correlates with coverage
- [ ] Results change dramatically when filtering missing data

### Lookahead Bias
- [ ] IC > 0.15 consistently
- [ ] Perfect quantile separation
- [ ] Unrealistic Sharpe ratios (>3 for daily)

### Overfitting
- [ ] Great in-sample, poor out-of-sample
- [ ] Works only in specific subperiods
- [ ] Sensitive to small parameter changes

### Trading Reality
- [ ] Turnover too high (>60% daily)
- [ ] Concentrated in illiquid assets
- [ ] Spread < transaction costs

### Statistical Issues
- [ ] IC sign flips across subperiods
- [ ] Non-monotonic quantile returns
- [ ] High mean IC but very low ICIR

---

## 10. Example: Complete Analysis

Here's a complete analysis workflow:

```python
from bagelfactor import (
    SingleFactorJob,
    plot_result_summary,
    ttest_1samp,
    ols_alpha_tstat
)

# Run evaluation
res = SingleFactorJob.run(
    panel,
    factor="my_alpha",
    price="close",
    horizons=(1, 5, 20),
    n_quantiles=5,
)

# 1. Quick visual check
fig = plot_result_summary(res, horizon=5)

# 2. IC analysis
h = 5
ic_mean = res.ic[h].mean()
ic_std = res.ic[h].std()
icir = res.icir[h]

print(f"IC Statistics (h={h}):")
print(f"  Mean: {ic_mean:.4f}")
print(f"  Std:  {ic_std:.4f}")
print(f"  ICIR: {icir:.2f}")

# 3. Statistical significance
ic_test = ttest_1samp(res.ic[h], popmean=0.0)
print(f"  t-stat: {ic_test.statistic:.2f}")
print(f"  p-value: {ic_test.pvalue:.4e}")

# 4. Economic significance
ls = res.long_short[h]
ls_mean = ls.mean()
ls_sharpe = ls_mean / ls.std() if ls.std() > 0 else 0
cum_ret = (1 + ls).cumprod().iloc[-1] - 1

print(f"\nLong-Short (h={h}):")
print(f"  Mean: {ls_mean*100:.3f}%")
print(f"  Sharpe: {ls_sharpe:.3f}")
print(f"  Cumulative: {cum_ret*100:.1f}%")

# 5. Tradability
avg_turnover = res.turnover.mean()
avg_coverage = res.coverage.mean()

print(f"\nTradability:")
print(f"  Avg turnover: {avg_turnover:.2%}")
print(f"  Avg coverage: {avg_coverage:.1%}")

# 6. Quantile analysis
qret = res.quantile_returns[h]
spread = (qret[5] - qret[1]).mean()
win_rate = ((qret[5] - qret[1]) > 0).mean()

print(f"\nQuantile Spread:")
print(f"  Q5-Q1: {spread*100:.3f}%")
print(f"  Win rate: {win_rate*100:.1f}%")

# 7. Decision
if icir > 0.5 and abs(ic_test.statistic) > 2 and avg_turnover < 0.4:
    print("\n✅ Factor looks promising!")
else:
    print("\n⚠️ Factor needs more investigation")
```

---

## 11. Next Steps After Evaluation

If your factor looks promising:

1. **Robustness checks**:
   - Test on different subperiods
   - Try different universes
   - Vary preprocessing parameters

2. **Cost analysis**:
   - Estimate transaction costs
   - Account for slippage and market impact
   - Calculate net returns

3. **Risk management**:
   - Check correlation with other factors
   - Analyze exposure to market regimes
   - Size positions appropriately

4. **Production**:
   - Implement real-time data pipeline
   - Set up monitoring and alerts
   - Plan rebalancing schedule

---

## Additional Resources

- [Factor Evaluation Guide](./factor_evaluation.md) - Theoretical background
- [Data Format Requirements](./data_format_requirements.md) - Avoid data issues
- [Example](./example.md) - Complete worked example
- [Module Documentation](./modules/single_factor/index.md) - API reference
