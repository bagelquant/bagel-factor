# Data Format Requirements

This document specifies the required data format for `bagel-factor` and clarifies the division of responsibilities between the user and the package.

## Philosophy

`bagel-factor` is a **precision calculation engine** that focuses on accurate computation and visualization. It expects properly formatted input data and does not perform extensive validation or cleaning.

**User Responsibility**: Data preparation, cleaning, and point-in-time integrity  
**Package Responsibility**: Accurate calculations, proper NaN handling, clear visualizations

---

## Panel Structure

### Index Requirements

A canonical panel **MUST** have:

- **Type**: `pd.MultiIndex` with exactly 2 levels
- **Names**: `["date", "asset"]` (in that order)
- **Sorted**: MUST be sorted by `(date, asset)` before use
- **No Duplicates**: MUST NOT contain duplicate `(date, asset)` pairs

```python
# ✅ Correct
panel = ensure_panel_index(df)
panel = panel.sort_index()  # CRITICAL: Must sort!

# ❌ Wrong - unsorted data will produce incorrect results
panel = ensure_panel_index(df)
result = SingleFactorJob.run(panel, ...)  # May be wrong if unsorted
```

### Column Requirements

- **Price columns** (e.g., "close"): MUST be numeric, SHOULD be non-negative
- **Factor columns**: MUST be numeric
- **NaN values**: OK - automatically excluded from calculations
- **Inf values**: Handled in statistical tests, but may cause issues in other operations

### Date Index

- **Type**: `pd.DatetimeIndex` (dates should be timezone-naive or consistently timezone-aware)
- **Frequency**: Can be irregular (daily, weekly, monthly, or mixed) - gaps are OK
- **Sorting**: MUST be monotonic increasing within each asset for `.shift()` operations to work correctly

---

## Point-in-Time Integrity

⚠️ **CRITICAL**: You are responsible for ensuring all data is point-in-time aligned.

The package assumes all data in row `(date, asset)` was **known as of that date**. Using future data will introduce lookahead bias and produce unrealistic backtest results.

### Correct Usage ✅

```python
import pandas as pd
from bagelfactor import ensure_panel_index, lag_by_asset, SingleFactorJob

# Load raw data
df = pd.read_csv("data.csv")
panel = ensure_panel_index(df)
panel = panel.sort_index()

# Lag fundamental data to avoid lookahead bias
# (Fundamental data published on date t should be used starting from t+1)
panel = lag_by_asset(panel, columns=['pe_ratio', 'book_to_market'], periods=1)

# Now safe to use
result = SingleFactorJob.run(panel, factor='pe_ratio', price='close')
```

### Incorrect Usage ❌

```python
# WRONG: Using same-day fundamental data
df = pd.read_csv("data.csv")
panel = ensure_panel_index(df)
result = SingleFactorJob.run(panel, factor='pe_ratio', price='close')
# This uses t's PE ratio to predict t's returns - LOOKAHEAD BIAS!
```

### Forward-Filling Warning

When using `align_to_calendar` with `method='ffill'`:

```python
# ⚠️ CAUTION: ffill propagates last known value forward
panel = align_to_calendar(panel, calendar, method='ffill')

# You MUST ensure factors were lagged BEFORE forward-filling
panel = lag_by_asset(panel, columns=['factor'], periods=1)
panel = align_to_calendar(panel, calendar, method='ffill')  # Now OK
```

---

## Data Preparation Workflow

Recommended workflow to ensure correctness:

```python
# 1. Load & Clean (your responsibility)
df = load_your_data()
df = df.dropna(subset=['close'])  # Remove rows with no price
df = df[df['close'] > 0]  # Remove invalid prices

# 2. Create panel index
panel = ensure_panel_index(df, date='date', asset='ticker')

# 3. CRITICAL: Sort the panel
panel = panel.sort_index()

# 4. Apply point-in-time lag to factors
# Rule: If data is "as-of" date t, lag by 1 to use it starting from t+1
panel = lag_by_asset(panel, columns=['fundamental_factor'], periods=1)

# 5. (Optional) Align to trading calendar
from bagelfactor.data import get_calendar, align_to_calendar
cal = get_calendar('NYSE', start='2020-01-01', end='2023-12-31')
panel = align_to_calendar(panel, cal, method='ffill')

# 6. Now safe to run factor evaluation
result = SingleFactorJob.run(
    panel,
    factor='fundamental_factor',
    price='close',
    horizons=(1, 5, 20),
)
```

---

## Common Data Issues

### Issue 1: Unsorted Data

**Symptom**: Forward returns are incorrect, results don't make sense  
**Cause**: Panel not sorted before calling `add_forward_returns`  
**Fix**: Always call `panel.sort_index()` after creating the panel

```python
# Before
panel = ensure_panel_index(df)

# After
panel = ensure_panel_index(df)
panel = panel.sort_index()  # Add this!
```

### Issue 2: Lookahead Bias

**Symptom**: Unrealistically high IC, factor seems too predictive  
**Cause**: Using same-day fundamental/factor data without lagging  
**Fix**: Lag factors by appropriate periods

```python
# Before
result = SingleFactorJob.run(panel, factor='pe_ratio', ...)

# After
panel = lag_by_asset(panel, columns=['pe_ratio'], periods=1)
result = SingleFactorJob.run(panel, factor='pe_ratio', ...)
```

### Issue 3: Duplicate Index

**Symptom**: Unexpected errors in groupby operations  
**Cause**: Multiple rows with same `(date, asset)` pair  
**Fix**: Remove or aggregate duplicates before creating panel

```python
# Remove duplicates (keep last)
df = df.drop_duplicates(subset=['date', 'asset'], keep='last')

# Or aggregate
df = df.groupby(['date', 'asset']).last().reset_index()
```

### Issue 4: Zero Variance

**Symptom**: Entire dates missing after ZScore transform  
**Cause**: All assets have same factor value on that date  
**Fix**: This is expected behavior - ZScore returns NaN for zero variance dates

```python
# Expected behavior
zscore = ZScore('factor')
panel = zscore.transform(panel)
# Dates where all assets have identical factor values will be NaN
```

### Issue 5: Missing Quantiles

**Symptom**: Long-short returns show NaN for some horizons  
**Cause**: Duplicate factor values result in fewer than `n_quantiles` bins  
**Fix**: This is expected - not enough unique values to create all quantiles

---

## Edge Cases & Special Behavior

### Empty Data

Functions handle empty DataFrames gracefully:

```python
empty_panel = pd.DataFrame(index=pd.MultiIndex.from_tuples([], names=['date', 'asset']))
ic = ic_series(empty_panel, factor='f', label='y')  # Returns empty Series
```

### Single Asset

Quantile assignment with 1 asset:

```python
# With 1 asset and n_quantiles=5, only 1 quantile is created
# This is expected - cannot split 1 asset into 5 groups
```

### All NaN Factor

When factor column is all NaN:

```python
# IC calculation returns NaN for all dates
# Quantile assignment returns all NaN
# This is expected behavior
```

### Irregular Date Spacing

The package handles irregular dates correctly:

```python
# Works fine with gaps
dates = ['2020-01-01', '2020-01-05', '2020-01-20']  # 3 random dates
# Operations work, but horizon=5 may span different calendar periods
```

---

## Validation Helpers (Optional)

While the package doesn't enforce validation by default, you can optionally use helper utilities:

```python
from bagelfactor.utils import diagnose_panel

# Check your panel for common issues
issues = diagnose_panel(panel)
print(issues)
```

Output example:
```
Panel Diagnostics
=================
✓ Index structure: OK
✗ Sorted: NO - Call panel.sort_index()
✓ Duplicates: None found
✓ Date frequency: Mostly daily (253 days/year average)
⚠ Missing data: 'factor' column has 15% NaN values
```

---

## Summary Checklist

Before running factor evaluation:

- [ ] Panel has MultiIndex with names `["date", "asset"]`
- [ ] Panel is sorted: `panel = panel.sort_index()`
- [ ] Factors are lagged appropriately (typically 1 period)
- [ ] Price data is valid (non-negative, no NaN)
- [ ] No duplicate `(date, asset)` pairs
- [ ] Understand edge cases (zero variance → NaN, duplicates → fewer quantiles)

---

## FAQ

**Q: Why doesn't the package validate that my data is sorted?**  
A: We follow the numpy/pandas philosophy - assume valid input for performance. Validation is expensive and not always necessary. Use optional `diagnose_panel()` if you need checking.

**Q: Should I forward-fill missing price data?**  
A: That depends on your research design. Forward-filling can introduce stale prices. Consider using `align_to_calendar(method='raw')` and explicitly deciding how to handle gaps.

**Q: What if I have timezone-aware dates?**  
A: The package handles timezone-aware dates, but be consistent. Mixing tz-naive and tz-aware dates will cause errors. `align_to_calendar` converts to tz-naive internally.

**Q: Can I use weekly or monthly data?**  
A: Yes, horizons are in "periods" not days. With weekly data, `horizon=1` means 1 week forward return.

**Q: What does "lookahead bias" mean?**  
A: Using information that wouldn't have been available at the time. For example, using end-of-day prices to predict the same day's returns, or using quarterly earnings announced on 2020-Q1-15 for 2020-Q1-01 predictions.

---

## See Also

- [Factor Evaluation Guide](./factor_evaluation.md) - Conceptual overview
- [End-to-End Example](./example.md) - Complete working example
- [Data Module Documentation](./modules/data.md) - Detailed API reference
