# bagel-factor

A small, pandas-first toolkit for **single-factor evaluation/testing**.

## Scope (by design)

This package focuses on:
- canonical point-in-time data helpers (`(date, asset)` panel)
- preprocessing transforms (clip / z-score / rank)
- single-factor evaluation (IC/ICIR, quantile returns, long-short, coverage, turnover)

It intentionally does **not** implement multi-factor modeling or portfolio backtesting.

## Install

```bash
pip install bagel-factor
```

## Install (dev / from source)

This repo is managed with [`uv`](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Quickstart

### 1) Prepare a canonical panel

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
```

### 2) (Optional) preprocess the factor

```python
from bagelfactor.preprocess import Clip, Pipeline, Rank, ZScore

preprocess = Pipeline([
    Clip("alpha", lower=0.0, upper=2.0),
    ZScore("alpha"),
    Rank("alpha"),
])
```

### 3) Run single-factor evaluation

`horizons` supports multiple forward-return windows (tuple of positive integers).

```python
from bagelfactor.single_factor import SingleFactorJob

res = SingleFactorJob.run(
    panel,
    factor="alpha",
    price="close",
    horizons=(1, 5, 20),
    n_quantiles=5,
    preprocess=preprocess,
)

ic_1d = res.ic[1]
qret_5d = res.quantile_returns[5]
long_short_20d = res.long_short[20]
```

### 4) Visualize results

```python
from bagelfactor.visualization import plot_result_summary

fig = plot_result_summary(res, horizon=5)
fig.show()
```

### 5) Statistical tests

```python
from bagelfactor.stats import ols_alpha_tstat, ttest_1samp

ic_test = ttest_1samp(res.ic[5], popmean=0.0)
ls_alpha = ols_alpha_tstat(res.long_short[5])

print(ic_test)
print(ls_alpha)
```

Full example with expected outputs: see [`docs/example.md`](./docs/example.md).

## Documentation

- Getting started with a complete, reproducible example (inputs + expected outputs):
  - [`docs/example.md`](./docs/example.md)
- Module docs:
  - [`docs/modules/`](./docs/modules/)

## License

MIT (see [`LICENSE`](./LICENSE)).
