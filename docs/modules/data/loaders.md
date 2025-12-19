# `bagelfactor.data.loaders`

Data ingestion utilities built around **pandas**. The module provides a small `LoadConfig` dataclass, format inference, a loader registry, and a single convenience entrypoint `load_df()`.

## Supported formats

- CSV: `pd.read_csv`
- JSON: `pd.read_json`
- Excel: `pd.read_excel`
- Parquet: `pd.read_parquet`
- Pickle: `pd.read_pickle`

## Public API

### `LoadConfig`

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

Notes:
- `columns`/`nrows` are applied where supported.
- For **parquet**, `nrows` is implemented via `df.head(nrows)` after reading.
- `postprocess` runs after loading (and after any `nrows` truncation).

### `load_df(config: LoadConfig) -> pd.DataFrame`

Canonical entrypoint.

```python
from bagelfactor.data.loaders import LoadConfig, load_df

# Load a CSV and apply a transformation
cfg = LoadConfig(
    source="data/prices.csv",
    nrows=100,
    postprocess=lambda df: df.assign(ret=df["close"].pct_change()),
)

df = load_df(cfg)
```

### `get_loader(config: LoadConfig) -> DataLoader`

Returns the concrete loader instance based on `config.format` or inferred format.

```python
from bagelfactor.data.loaders import LoadConfig, get_loader

loader = get_loader(LoadConfig(source="data/features.parquet"))
df = loader.load()
```

## Format inference

`_infer_format(source)` infers based on `Path(source).suffix`:

- `.csv` → `csv`
- `.json` → `json`
- `.xlsx`/`.xls` → `xlsx`
- `.parquet` → `parquet`
- `.pkl`/`.pickle` → `pickle`

If the suffix is unknown, `UnsupportedFormatError` is raised.

## Dependencies and caveats

- Parquet support typically requires an engine such as **pyarrow** or **fastparquet** installed; pandas will raise at runtime if no engine is available.
- Excel support may require `openpyxl` (for `.xlsx`) depending on your environment.

