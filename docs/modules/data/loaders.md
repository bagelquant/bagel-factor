# `bagelfactor.data.loaders`

Data ingestion utilities built around **pandas** readers.

The module is intentionally small:

- a `LoadConfig` dataclass defines what to load and optional behaviors
- `_infer_format()` infers format from file suffix
- `_add_optional_common_behavior()` injects `columns`/`nrows` into reader kwargs when applicable
- `get_loader()` returns a concrete loader
- `load_df()` is the canonical entrypoint

## Supported formats

- CSV: `pd.read_csv`
- JSON: `pd.read_json`
- Excel: `pd.read_excel`
- Parquet: `pd.read_parquet`
- Pickle: `pd.read_pickle`

## `LoadConfig`

```python
from bagelfactor.data.loaders import LoadConfig

cfg = LoadConfig(
    source="path/to/file.csv",
    format=None,          # optional; inferred from suffix
    columns=["a", "b"],  # optional
    nrows=1000,           # optional
    postprocess=None,     # optional callable: (df) -> df
    read_kwargs=None,     # optional dict passed to pandas reader
)
```

### Behavior and precedence

- `read_kwargs` is passed through to the underlying pandas function.
- If `columns` / `nrows` are provided and *not already present* in `read_kwargs`, they are injected.
- For **parquet**, pandas does not support `nrows`, so `nrows` is applied after reading via `df.head(nrows)`.
- `postprocess(df)` runs after loading (and after any row limiting).

## `load_df(config) -> pd.DataFrame`

Canonical entrypoint.

Expected output:

- a `pd.DataFrame` as returned by pandas
- optionally transformed by `postprocess`

```python
from bagelfactor.data.loaders import LoadConfig, load_df

cfg = LoadConfig(
    source="data/prices.csv",
    nrows=100,
    postprocess=lambda df: df.assign(ret=df["close"].pct_change()),
)

df = load_df(cfg)
```

## Internal docs

- [`loaders_internal`](./loaders_internal.md)

## Common pitfalls

- Parquet requires a parquet engine (`pyarrow` or `fastparquet`).
- Excel may require `openpyxl`.
