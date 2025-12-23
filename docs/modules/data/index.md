# `bagelfactor.data` (module index)

This page is an index of the public API and what each function returns.

## Public API (recommended imports)

```python
from bagelfactor.data import (
    # loaders
    LoadConfig, load_df,

    # panel
    ensure_panel_index, validate_panel,
    add_returns, add_forward_returns,

    # factors / universe
    FactorSeries, FactorMatrix,
    Universe,

    # alignment
    align_to_calendar, lag_by_asset,

    # calendars
    retrieve_trading_calendar,
    get_trading_calendar_daily,
    get_trading_calendar_weekly,
    get_trading_calendar_monthly,
    get_trading_calendar_quartly,
)
```

## What each sub-module does

- [`loaders`](./loaders.md): reads files into a `pd.DataFrame` (optionally selecting columns, limiting rows, postprocessing)
- [`panel`](./panel.md): ensures `(date, asset)` index and adds return labels
- [`align`](./align.md): aligns a panel to a calendar and provides lagging utilities
- [`factors`](./factors.md): small typed wrappers for factor series/matrices
- [`universe`](./universe.md): stores membership mask and filters panels
- [`calendar`](./calendar.md): builds + caches valid sessions and schedules for markets
