# `bagelfactor.metrics` (module index)

Single-factor evaluation metrics.

## Public API

```python
from bagelfactor.metrics import (
    ic_series,
    icir,
    assign_quantiles,
    quantile_returns,
    quantile_turnover,
    coverage_by_date,
)
```

## Detailed docs

- [`ic`](./ic.md)
- [`quantiles`](./quantiles.md)
- [`turnover`](./turnover.md)
- [`coverage`](./coverage.md)

## What’s included (v0)
- IC / RankIC time series per horizon
- ICIR summary
- Quantile return tables
- Long-short (top minus bottom quantile)
- Quantile turnover
- Coverage (non-missing fraction)
