# Factor evaluation guide

This document explains *why* we evaluate factors, *what* to measure, how to interpret results, and common practical thresholds.
It is written to match `bagel-factor`’s workflow and outputs (IC/ICIR, quantile returns, long-short, turnover, coverage), while also calling out real-world pitfalls.

---

## 1) Why do we need factor evaluation?

A **factor** is a numeric signal per asset per date intended to predict *future* returns (or risk, or another target). For example, in equities, it could be:

- a valuation metric (e.g. P/E ratio)
- a technical indicator (e.g. moving average crossover)
- a sentiment score (e.g. from news or social media)
- a machine learning model output (e.g. predicted return)

Normally a factor corresponds to *time* and *asset* dimensions, i.e. a panel of shape (dates × assets).

We want to evaluate factors to determine if they are useful for investment decisions (return predictions) and if they can be traded profitably.

Factor evaluation answers three questions:

1. **Does the signal contain information?**
   - Is the signal correlated with forward returns cross-sectionally?
2. **Is the signal *economically tradable*?**
   - Can you form portfolios with positive expected returns after costs (turnover, slippage)?
3. **Is the signal stable and robust?**
   - Does it work across time, across assets, and under reasonable transformations?

Without a disciplined evaluation framework, it is easy to mistake:

- **noise** for signal (data-mining / multiple testing)
- **lookahead bias** for predictability
- **non-tradable** effects (high turnover, microcap exposure) for alpha

---

## 2) What does `bagel-factor` evaluate?

`bagel-factor` is *single-factor* and *pandas-first*.
Its canonical data model is a **panel**:

- `pd.DataFrame`
- indexed by `pd.MultiIndex` named `("date", "asset")`

A typical workflow:

1. Ensure/validate panel index (`ensure_panel_index`, `validate_panel`).
2. (Optional) apply a `Universe` membership mask.
3. (Optional) preprocess the factor (clip / z-score / rank) using `Pipeline`.
4. Add forward return labels (`add_forward_returns`).
5. Compute evaluation metrics via `SingleFactorJob.run(...)`.

See:
- API: [`bagelfactor.single_factor`](./modules/single_factor/index.md)
- Example: [`docs/example.md`](./example.md)

---

## 3) A principled factor evaluation process

A robust evaluation pipeline typically includes:

### 3.1 Define the research question

- Asset class / universe (e.g. liquid US equities).
- Holding period(s) / horizon(s) (e.g. 1D, 5D, 20D).
- Rebalance frequency (often matches horizon and/or factor update frequency).
- Constraints (long-only vs long-short, sector-neutral, etc.).

### 3.2 Build a point-in-time dataset

Critical requirement: at date $t$, the factor must be computable using only information available at $t$.

Common sources of leakage:

- using fundamentals that were announced after $t$ but backfilled to $t$
- aligning quarterly data to daily prices without lagging
- accidental shifting mistakes when building labels

`bagel-factor` provides explicit helpers for point-in-time alignment:

- `align_to_calendar(panel, trade_calendar, method=...)`
- `lag_by_asset(panel, columns, periods=...)`

See: [`bagelfactor.data.align`](./modules/data/align.md)

### 3.3 Decide factor preprocessing

Raw factors often need basic conditioning:

- **clip/winsorize** outliers (robustness)
- **z-score** cross-sectionally (comparable scale)
- **rank** cross-sectionally (reduces tail sensitivity)

`bagel-factor` provides:

- `Clip`, `ZScore`, `Rank`, `DropNa`

See: [`bagelfactor.preprocess.transforms`](./modules/preprocess/transforms.md)

### 3.4 Choose evaluation metrics and diagnostics

At minimum, for a cross-sectional alpha factor you usually want:

- **coverage**: how much data is usable?
- **IC / RankIC**: does the signal order assets correctly?
- **ICIR**: is IC stable?
- **quantile returns**: does performance improve monotonically from low to high?
- **long-short spread**: is there a meaningful top-minus-bottom payoff?
- **turnover**: is it likely tradable after costs?

---

## 4) Metrics in detail (math + interpretation)

### 4.1 Coverage

**Coverage** is the fraction of assets with a non-missing factor value per date.

Let $N_t$ be the number of assets in the panel at date $t$, and $n_t$ the count with finite/non-null factor values.

$$
\text{coverage}_t = \frac{n_t}{N_t}
$$

**Why it matters**

- Low coverage reduces statistical power and can bias results (e.g., only a subset of assets is ever scored).
- Time-varying coverage can create artificial patterns (factor “works” only when it is defined).

**Common thresholds (rule of thumb)**

- $> 0.95$: excellent (common in price/technical factors)
- $0.80$–$0.95$: acceptable, but inspect missingness patterns
- $< 0.80$: investigate; results may be driven by a subset / selection bias

In `bagel-factor`: `coverage_by_date(panel, column=factor)`.

---

### 4.2 Information Coefficient (IC) and RankIC

**IC** is the cross-sectional correlation between the factor at date $t$ and the *forward* return label over horizon $h$:

- factor: $f_{i,t}$
- label: $r^{(h)}_{i,t}$, e.g. $\frac{P_{i,t+h}}{P_{i,t}} - 1$

Per date $t$, define the set of assets with non-missing values:

$$
\mathcal{U}_t = \{ i : f_{i,t} \text{ and } r^{(h)}_{i,t} \text{ are defined} \}
$$

Then IC is:

$$
\text{IC}_t = \mathrm{corr}\left(\{f_{i,t}\}_{i\in\mathcal{U}_t},\; \{r^{(h)}_{i,t}\}_{i\in\mathcal{U}_t}\right)
$$

**Pearson IC vs Spearman RankIC**

- **Pearson** correlation: measures linear association.
- **Spearman** correlation: Pearson correlation on ranks (RankIC), more robust to outliers and non-linear monotonic relationships.

`bagel-factor` supports:

- `method="spearman"` (default): RankIC
- `method="pearson"`

See: [`bagelfactor.metrics.ic`](./modules/metrics/ic.md)

**How to interpret IC magnitudes**

ICs are usually *small* in real markets.

Rules of thumb for daily cross-sectional equity factors (highly context dependent):

- $|\text{IC}| < 0.01$: likely noise
- $0.01$–$0.03$: weak but possibly real if stable and scalable
- $0.03$–$0.06$: solid
- $> 0.06$: strong (or suspect leakage / universe bias)

Also interpret sign:

- positive IC: higher factor predicts higher future return
- negative IC: higher factor predicts lower future return (maybe you should invert)

**Important caveats**

- IC is computed *cross-sectionally* per date; it says nothing directly about time-series predictability.
- IC depends heavily on universe definition, neutralization choices, and label definition.

---

### 4.3 ICIR (Information Coefficient Information Ratio)

ICIR measures stability of the IC series:

$$
\text{ICIR} = \frac{\mathbb{E}[\text{IC}_t]}{\mathrm{Std}[\text{IC}_t]}
$$

In `bagel-factor`, `icir(ic)` computes mean/std using population standard deviation (`ddof=0`).

**How to interpret ICIR**

- Higher is better: more stable signal.
- A high mean IC with high variance may still be hard to trade.

Rules of thumb (again context dependent):

- $\text{ICIR} < 0.2$: weak
- $0.2$–$0.5$: modest
- $0.5$–$1.0$: good
- $> 1.0$: strong

**Note on annualization**

Some teams report annualized ICIR, e.g. $\sqrt{252}\cdot\text{ICIR}$ for daily data.
`bagel-factor` reports the raw ratio; you can annualize externally if desired.

---

### 4.4 Quantile assignment

Quantile analysis converts a continuous factor into discrete buckets, usually by ranking within each date.

For each date $t$, assets are sorted by factor and split into $Q$ buckets.

- Bottom bucket: Q1 (lowest factor values)
- Top bucket: Q$Q$ (highest factor values)

`bagel-factor` uses:

- deterministic tie-breaking (`rank(method="first")`)
- `pd.qcut(..., duplicates="drop")` to handle repeated values

This means some dates may realize fewer than `n_quantiles` buckets if the factor has too many identical values.

See: [`bagelfactor.metrics.quantiles`](./modules/metrics/quantiles.md)

---

### 4.5 Quantile returns

Given quantile bucket $q_{i,t}\in\{1,\dots,Q\}$, define the mean forward return within each bucket:

$$
\bar r_{t}^{(h)}(q) = \frac{1}{|\{i: q_{i,t}=q\}|} \sum_{i: q_{i,t}=q} r^{(h)}_{i,t}
$$

This produces a time series per quantile and answers:

- Do higher-factor buckets have higher average returns?
- Is the relationship monotonic across buckets?

**What to look for**

- **Monotonicity**: Q1 < Q2 < ... < QQ (not strictly required, but desirable).
- **Consistency**: top bucket and bottom bucket behavior stable over time.
- **Spread**: how large is the difference between top and bottom?

---

### 4.6 Long-short (top minus bottom)

A common single-factor payoff proxy is:

$$
\text{LS}_t^{(h)} = \bar r_{t}^{(h)}(Q) - \bar r_{t}^{(h)}(1)
$$

This is the **factor spread**.

- Positive long-short suggests you can go long high-factor assets and short low-factor assets.
- If your mandate is long-only, you still care because it indicates cross-sectional separation.

`bagel-factor` computes this when both Q1 and Q$Q$ exist.

**Common follow-up diagnostics** (not all built-in, but easy to compute)

- mean, volatility, Sharpe of long-short
- cumulative returns: $\prod_t (1+\text{LS}_t) - 1$
- drawdowns

---

### 4.7 Turnover

Turnover approximates how much the membership of each quantile changes from one date to the next.
High turnover implies higher transaction costs.

`bagel-factor` defines turnover using a Jaccard-style set overlap:

Let $S_{t,q}$ be the set of assets in quantile $q$ at date $t$.

$$
\text{turnover}_{t,q} = 1 - \frac{|S_{t,q}\cap S_{t-1,q}|}{|S_{t,q}\cup S_{t-1,q}|}
$$

Properties:

- 0.0: identical membership to previous date
- 1.0: completely different membership

**How to interpret turnover**

- Low turnover is generally more tradable.
- A factor can have good IC but be untradable if it reshuffles constantly.

Rules of thumb (daily rebalancing):

- $< 0.2$: low
- $0.2$–$0.5$: moderate
- $> 0.5$: high (costs likely dominate unless spreads are large)

See: [`bagelfactor.metrics.turnover`](./modules/metrics/turnover.md)

---

## 5) Statistical testing (what it means and what it doesn’t)

### 5.1 t-test for mean IC or mean long-short

A common question: “Is the mean IC significantly different from 0?”

Given an IC series $\{\text{IC}_t\}$, a one-sample t-test evaluates:

- $H_0: \mathbb{E}[\text{IC}] = 0$

`bagel-factor` provides:

- `ttest_1samp(x, popmean=0.0)`

and for comparing two samples:

- `ttest_ind(x, y, equal_var=False)` (Welch by default)

See: [`bagelfactor.stats.tests`](./modules/stats/tests.md)

**Caveats**

Financial time series often violate classical t-test assumptions:

- autocorrelation
- heteroskedasticity
- non-stationarity

So p-values can be optimistic.
For production research, consider robust standard errors (e.g., Newey–West) and subperiod stability checks.

### 5.2 Regression alpha (OLS intercept t-stat)

Another lens: regress a return series on a benchmark and test intercept (alpha).

Model:

$$
 y_t = \alpha + \beta x_t + \varepsilon_t
$$

- If `x` is omitted: mean test $y_t = \alpha + \varepsilon_t$

`bagel-factor` provides:

- `ols_alpha_tstat(y, x=None)`
- `ols_summary(y, x=None)`

See: [`bagelfactor.stats.regression`](./modules/stats/regression.md)

**Common thresholds**

- |t-stat| > 2 is often treated as “significant” at ~5% (under ideal assumptions).
- In finance research, you usually want stronger evidence due to data mining risk.

---

## 6) Practical robustness checks (recommended)

Even if headline metrics look good, do these checks:

1. **Subperiod analysis**
   - Does the factor work across regimes (pre/post crises, rate regimes, etc.)?
2. **Universe sensitivity**
   - Does it depend on microcaps, illiquid names, or a narrow sector?
3. **Preprocessing sensitivity**
   - Does ranking vs z-scoring change conclusions?
4. **Outlier sensitivity**
   - Does clipping materially change IC/long-short?
5. **Capacity / costs**
   - High turnover signals poor net performance.

---

## 7) Common pitfalls (and how this project helps)

### 7.1 Lookahead bias

- Always ensure factor uses information available at date $t$.
- Use explicit lagging (`lag_by_asset`) and calendar alignment (`align_to_calendar`).

### 7.2 Survivorship and selection bias

- If your panel only includes assets that survive to the end, results will be inflated.
- Universe masks (`Universe`) make inclusion rules explicit.

### 7.3 Multiple testing / data snooping

- Trying many factors/hyperparameters will produce false positives.
- Use holdouts, cross-validation (careful for time series), and corrections when appropriate.

### 7.4 Mis-specified labels

- Ensure forward return labels match tradable holding periods.
- Handle corporate actions / splits properly in price data.

---

## 8) How to do it with `bagel-factor` (end-to-end)

```python
from bagelfactor.data import ensure_panel_index
from bagelfactor.preprocess import Clip, Pipeline, Rank, ZScore
from bagelfactor.single_factor import SingleFactorJob
from bagelfactor.visualization import plot_result_summary
from bagelfactor.stats import ttest_1samp, ols_alpha_tstat

panel = ensure_panel_index(raw_df)

preprocess = Pipeline([
    Clip("alpha", lower=-5, upper=5),
    ZScore("alpha"),
    Rank("alpha"),
])

res = SingleFactorJob.run(
    panel,
    factor="alpha",
    price="close",
    horizons=(1, 5, 20),
    n_quantiles=5,
    preprocess=preprocess,
)

# Quick plots
fig = plot_result_summary(res, horizon=5)

# Statistical tests
ic_test = ttest_1samp(res.ic[5], popmean=0.0)
ls_alpha = ols_alpha_tstat(res.long_short[5])

print(ic_test)
print(ls_alpha)
```

---

## 9) Suggested “acceptance” checklist

A factor is rarely “good” or “bad” from a single number.
Still, a pragmatic checklist might be:

- Coverage stable and generally high.
- IC has the expected sign and is reasonably stable (ICIR not tiny).
- Quantile returns show sensible ordering and a persistent Q$Q$-Q1 spread.
- Turnover is not so high that it plausibly overwhelms gross returns.
- Basic tests (t-test / OLS intercept) support non-zero mean, *and* subperiod results are not wildly inconsistent.

---

## 10) What this project does *not* cover (yet)

`bagel-factor` intentionally keeps scope small.
You may still need external tooling for:

- portfolio construction and constraints
- transaction cost models
- risk model / factor neutralization (sector/industry, beta, size)
- Newey–West or other robust inference
- walk-forward evaluation and proper research governance

---

## References / further reading

- Grinold & Kahn — *Active Portfolio Management* (IC/IR concepts)
- Harvey, Liu, Zhu — multiple testing in finance (“...and the Cross-Section of Expected Returns”)
- General research best practices: subperiod checks, out-of-sample validation, and cost-aware evaluation
