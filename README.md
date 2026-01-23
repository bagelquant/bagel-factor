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

### Table of contents

- Getting started
  - [Factor evaluation guide](./docs/factor_evaluation.md)
  - [End-to-end example](./docs/example.md)

- Modules
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

- Design docs
  - [v0 proposals](./docs/proposals/proposals_v0.md)

## License

MIT (see [`LICENSE`](./LICENSE)).
