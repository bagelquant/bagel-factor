# `bagelfactor.data.universe`

Universe membership masks and optional labels.

A `Universe` defines which `(date, asset)` rows are eligible for analysis.

Common uses:

- exclude untradable assets
- implement index membership (e.g., top N by market cap)
- apply survivorship / listing rules (user-provided)

## `Universe(mask, labels=None)`

### Inputs

- `mask`: `pd.Series[bool]` indexed by `(date, asset)`
- `labels` (optional): `pd.DataFrame` indexed by `(date, asset)` for metadata such as `sector`/`industry`

### Expected output

A lightweight object holding the mask (and labels).

## `Universe.apply(panel) -> pd.DataFrame`

Note: Universe masks are reindexed to match the panel and missing entries are treated as False to avoid unintentionally dropping rows.

Filters a panel down to rows where `mask == True`.

### Logic

- reindex the mask to the panel index
- treat missing mask values as `False`
- return `panel.loc[mask]`

### Expected output

- a filtered `pd.DataFrame` with a subset of the original `(date, asset)` rows
