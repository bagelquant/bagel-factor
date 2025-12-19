# bagel-factor v0 Proposal (Factor Research + Modeling + Backtesting)

**Date:** 2025-12-19  
**Scope:** v0 architecture and interfaces for a comprehensive factor model research and backtesting package.

## 1. Executive summary

`bagel-factor` is a Python package for **daily equity** research (v0 default; extensible to multi-asset) that supports three **independent** user workflows:

1. **Single Factor Testing**: IC/ICIR, decay, quantile returns, turnover, and robustness checks.
2. **Multi-Factor Models**: a unified interface to combine factors using regression, ML, and neural networks; walk-forward evaluation.
3. **Any Strategy Backtesting**: a general portfolio backtesting engine that can backtest *any* strategy producing target positions/weights.

All three workflows share a common point-in-time data model, preprocessing pipeline, metrics layer, and reporting/export utilities.

## 2. Goals (v0)

### 2.1 Functional goals

- **Correct, point-in-time workflow**: avoid lookahead via explicit lagging rules and alignment.
- **Reproducible research**: deterministic splits, configuration capture, and artifact export.
- **Composable preprocessing**: winsorize/clip, zscore/rank, missing handling, neutralization.
- **Standard single-factor diagnostics**: IC/RankIC, ICIR, IC decay curves, quantile portfolios, turnover.
- **Unified multi-factor modeling interface** with interchangeable backends.
- **General backtest engine**: weights → trades → PnL with user-defined costs, slippage, and tradability rules.

### 2.2 Non-goals (initially)

- Broker connectivity / OMS, real-time execution, tick-level simulation.
- A complete risk-model suite (basic exposures supported; full Barra-like models can be layered later).

## 3. Design principles

- **Three jobs, independently runnable**: no workflow should require the others.
- **Shared primitives**: each job consumes/produces the same canonical objects.
- **Separation of concerns**:
  - research diagnostics ≠ portfolio simulation,
  - model training/evaluation ≠ execution assumptions.
- **Plugin-first**: models, cost models, and strategies are pluggable.

## 4. Canonical data model

### 4.1 Canonical “Panel”

Internal canonical representation is a panel indexed by `(date, asset)`.

**Required index**

- `date`: trading date (timezone-normalized)
- `asset`: stable identifier (ticker mapping optional)

**Common columns (recommended)**

- Pricing/returns: `close`, `open`, `vwap`, `ret_1d`, and computed `ret_fwd_{h}` labels
- Liquidity/capacity: `volume`, `adv_{n}`, `mkt_cap`
- Flags: `tradable`, `in_universe`, `halted`, `stale`
- Group labels: `sector`, `industry` (optional but strongly recommended)

### 4.2 Factors

- `FactorSeries`: one score per `(date, asset)` plus metadata (name, lookback, required fields, etc.).
- `FactorMatrix`: multiple factors aligned to `(date, asset)`.

### 4.3 Universe

- `Universe`: membership mask over `(date, asset)` with optional group labels.

## 5. Package structure (v0)

Proposed high-level layout:

```
bagel_factor/
  data/              # loaders, calendars, universe, point-in-time alignment
  preprocess/        # transforms, pipelines, neutralization, lag rules
  metrics/           # IC, quantiles, performance stats, risk metrics
  reporting/         # optional plots/exports

  single_factor/     # Job 1
    job.py

  models/            # model implementations + validation utilities
    base.py
    linear.py
    validation.py
  multi_factor/      # Job 2
    job.py

  strategy/          # strategy interface + examples
    base.py
  backtest/          # Job 3
    job.py
    engine.py
    execution.py
    costs.py
    result.py
```

## 6. Workflow definitions (the 3 jobs)

### 6.1 Job 1 — Single Factor Testing

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

### 6.2 Job 2 — Multi-Factor Models

**Purpose:** combine multiple factors using a unified `AlphaModel` interface (regression/ML/NN), with walk-forward evaluation.

**Key requirement:** one interface, many backends.

**Unified interface**
```python
class AlphaModel:
    def fit(self, X, y, sample_weight=None, groups=None):
        ...
    def predict(self, X):
        ...
    def diagnostics(self) -> dict:
        ...
```

**Training/evaluation protocol**

- Walk-forward (rolling or expanding) splits.
- Optional purged/embargo CV for leakage control.
- Labels typically `ret_fwd_h` (or residual returns).

**Outputs**

- `alpha_pred[(date, asset)]`
- prediction IC/RankIC time series
- stability diagnostics (coef drift / feature importance)

**Proposed API**

```python
MultiFactorJob.train_predict(
    panel,
    X_factors,
    y_label,
    model: AlphaModel,
    split,
    universe=None,
    preprocess=None,
) -> MultiFactorResult
```

### 6.3 Job 3 — Any Strategy Backtesting

**Purpose:** simulate performance of any strategy that produces target positions/weights. This is intentionally not limited to factor strategies.

**Strategy interface**
```python
class Strategy:
    def generate(self, panel, universe=None):
        """Return target weights indexed by (date, asset)."""
```

**Backtest engine responsibilities**

- User-defined rebalance schedule (daily data, but rebalance frequency is user-defined)
- User-provided tradability rules/filters, position limits, leverage/gross/net constraints
- User-provided transaction cost + slippage/impact models (package provides simple defaults)
- Accounting: holdings, trades, PnL, exposures, turnover

**Proposed API**

```python
BacktestJob.run(
    panel,
    target_weights,
    execution=None,
    costs=None,
    rules=None,
) -> BacktestResult
```

**BacktestResult** should minimally include

- `equity_curve`, `returns`, `holdings`, `trades`, `costs`, `turnover`
- exposure time series by group/sector (if metadata available)

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

- Single-factor: IC/RankIC, ICIR, decay, quantiles, turnover
- Portfolio: CAGR, vol, Sharpe/Sortino, max drawdown, hit rate

### 7.3 Reporting/export

- Export tables and time series to parquet/csv
- Optional plotting layer (kept out of core dependencies)

## 8. Implementation plan (v0 milestones)

1. **Core data + preprocessing**: canonical panel utilities, pipelines, return labeling.
2. **Job 1 (Single factor)**: IC/ICIR/decay/quantiles/turnover and a structured result object.
3. **Job 3 (Backtest engine)**: weights→trades→PnL with basic costs and tradability rules.
4. **Job 2 (Multi-factor)**: unified `AlphaModel`, linear baseline models, walk-forward evaluation.
5. Expand: constraints/optimizers, richer cost models, optional ML/NN backends, richer attribution.

## 9. v0 defaults + remaining questions

### 9.1 v0 defaults (based on current requirements)

- **Asset class:** equities
- **Data frequency:** daily
- **Rebalance frequency:** user-defined (e.g., daily/weekly/monthly) while consuming daily data
- **Tradability rules:** user input (engine consumes a user-provided rule/filter; package ships minimal defaults)
- **Transaction costs/slippage:** user input (engine consumes a user-provided cost model; package ships minimal defaults)

