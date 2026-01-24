# `bagelfactor.data.loaders` (internal details)

This page documents internal helpers and error types.

## Errors

### `LoaderError(RuntimeError)`
Base error type for loader problems.

### `UnsupportedFormatError(LoaderError)`
Raised when a file suffix / requested format is not supported.

## Internal helpers

### `_infer_format(source) -> str`
Infers format from `Path(source).suffix`.

Supported suffixes:
- `.csv` -> `"csv"`
- `.json` -> `"json"`
- `.xlsx`/`.xls` -> `"xlsx"`
- `.parquet` -> `"parquet"`
- `.pkl`/`.pickle` -> `"pickle"`

### `_add_optional_common_behavior(config) -> dict[str, Any]`
Returns `read_kwargs` after injecting:
- `columns` if provided and `"columns"` not already present
- `nrows` if provided and `"nrows"` not already present

Note: parquet uses special handling because `pd.read_parquet` does not accept `nrows`.

## Loader classes

All loaders take a `LoadConfig` and implement `load() -> pd.DataFrame`.

- `CSVLoader` -> `pd.read_csv`
- `JSONLoader` -> `pd.read_json`
- `ExcelLoader` -> `pd.read_excel`
- `ParquetLoader` -> `pd.read_parquet` (applies `head(nrows)` after load)
- `PickleLoader` -> `pd.read_pickle` (attempts `DataFrame(obj)` if not a DataFrame)

## Factory

### `get_loader(config) -> DataLoader`
Chooses a loader class based on `config.format` (or inferred format).

### `LOADER_REGISTRY`
Maps format strings to concrete loader classes.
