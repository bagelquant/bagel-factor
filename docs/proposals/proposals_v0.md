# bagel-factor v0 Proposal (Single-Factor Evaluation + Testing)

**Date:** 2025-12-19  
**Scope:** v0 architecture and interfaces for a **single-factor evaluation/testing** package.

## 1. Executive summary

`bagel-factor` is a Python package for **daily equity** factor research (v0 default; extensible to multi-asset) focused on one workflow:

- **Single Factor Testing**: IC/RankIC, ICIR, decay, quantile returns, turnover, coverage, and robustness checks.

This package intentionally does **not** implement portfolio backtesting or multi-factor/model evaluation; those will live in a separate package.

## 2. Goals (v0)

### 2.1 Functional goals

- **Correct, point-in-time workflow**: avoid lookahead via explicit lagging rules and alignment.
- **Reproducible research**: deterministic configuration, stable inputs/outputs, and artifact export.
- **Composable preprocessing**: winsorize/clip, zscore/rank, missing handling, neutralization.
- **Standard single-factor diagnostics**: IC/RankIC, ICIR, IC decay curves, quantile portfolios, turnover, coverage.

### 2.2 Non-goals (v0)

- **Backtesting / portfolio simulation** (weights → trades → PnL).
- **Multi-factor modeling** (combining factors via regression/ML/NN, walk-forward evaluation).
- Broker connectivity / OMS, real-time execution, tick-level simulation.

## 3. Design principles

- **One job, done well**: the public API centers on single-factor evaluation.
- **Shared primitives**: all evaluation consumes/produces the same canonical objects.
- **Explicit point-in-time**: if a transformation could introduce lookahead, it should be explicit (e.g., lagging, calendar alignment).
- **Composable utilities**: pandas-first helpers that remain easy to integrate with other packages.

## 4. Canonical data model

### 4.1 Canonical “Panel”

Internal canonical representation is a panel indexed by `(date, asset)`.

**Required index**

- `date`: trading date (timezone-normalized)
- `asset`: stable identifier (ticker mapping optional)

**Common columns (recommended)**

- Pricing/returns: `close`, `open`, `vwap`, `ret_1d`, and computed `ret_fwd_{h}` labels
- Liquidity/capacity: `volume`, `adv_{n}`, `mkt_cap`
- Flags: `in_universe`, `halted`, `stale` (optional)
- Group labels: `sector`, `industry` (optional but useful for grouped stats)

### 4.2 Factors

- `FactorSeries`: one score per `(date, asset)` plus metadata (name, lookback, required fields, etc.).
- `FactorMatrix`: multiple factor columns aligned to `(date, asset)` (useful for batch single-factor testing).

### 4.3 Universe

- `Universe`: membership mask over `(date, asset)` with optional group labels.

## 5. Package structure (v0)

Proposed high-level layout:

```
bagelfactor/
  data/              # loaders, calendars, universe, point-in-time alignment
  preprocess/        # transforms + pipelines
  metrics/           # single-factor metrics (IC, quantiles, turnover, coverage)
  reporting/         # exports (csv/parquet)
  single_factor/     # single-factor evaluation job + result object
```

## 6. Workflow definition

### Single Factor Testing

**Purpose:** evaluate a factor signal without requiring any model training or portfolio simulation.

**Inputs**
- `panel`: canonical panel
- `factor`: `FactorSeries` or column name
- `horizons`: forward-return horizons (e.g., 1D/5D/20D)
- `universe`: optional membership mask
- `groups`: optional group labels (sector/industry) for grouped stats
- `preprocess`: optional pipeline (e.g., rank + neutralize)

**Core outputs**

- `ic_ts[h]`, `icir[h]`
- `ic_decay_curve` (IC over multiple horizons)
- `quantile_returns`, `long_short_returns`
- `turnover_by_quantile`, `coverage`, `group_ic` (if provided)

**Proposed API**
```python
SingleFactorJob.run(
    panel,
    factor,
    horizons=(1, 5, 20),
    universe=None,
    groups=None,
    preprocess=None,
) -> SingleFactorResult
```

## 7. Cross-cutting components

### 7.1 Preprocessing pipeline

Composable steps applied cross-sectionally by date:
- Missing handling (drop/impute with constraints)
- Winsorize/clip
- Z-score / rank / rank-gaussian
- Neutralization (e.g., industry, size, beta)
- Lagging rules (explicit to enforce point-in-time)

**API sketch**
```python
pipeline = Pipeline([
    Winsorize(p=0.01),
    Rank(),
    Neutralize(by=["industry"], controls=["log_mkt_cap"]),
])
```

### 7.2 Metrics

- IC/RankIC, ICIR
- IC decay
- Quantile returns / long-short returns
- Turnover
- Coverage / missingness diagnostics

### 7.3 Reporting/export

- Export tables and time series to parquet/csv
- Optional plotting layer (kept out of core dependencies)

## 8. Implementation plan (v0 milestones)

1. **Core data + preprocessing**: canonical panel utilities, pipelines, return labeling.
2. **Single-factor evaluation**: IC/ICIR/decay/quantiles/turnover and a structured result object.
3. **Reporting/export**: persist results + optional plotting hooks.

## 9. v0 defaults + remaining questions

### 9.1 v0 defaults (based on current requirements)

- **Asset class:** equities
- **Data frequency:** daily
- **Evaluation horizons:** user-provided (e.g., 1D/5D/20D)
- **Universe + group labels:** optional inputs for filtering and grouped stats

