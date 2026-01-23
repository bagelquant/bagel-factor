# `bagelfactor.reporting.export`

Export helpers for pandas objects.

## `to_csv(obj, path, *, index=True) -> Path`

Write a `pd.DataFrame` or `pd.Series` to CSV.

### Parameters
- `obj: pd.DataFrame | pd.Series`
- `path: str | Path`
- `index: bool` — whether to include the index in the CSV.

### Behavior
- Ensures `path.parent` exists (`mkdir(parents=True, exist_ok=True)`).
- For a `Series`, writes `obj.to_frame().to_csv(...)`.

### Returns
- `Path` to the written file.

## `to_parquet(obj, path) -> Path`

Write a `pd.DataFrame` or `pd.Series` to Parquet.

### Parameters
- `obj: pd.DataFrame | pd.Series`
- `path: str | Path`

### Dependencies
- Requires a parquet engine at runtime: `pyarrow` or `fastparquet`.

### Raises
- `ImportError` if no parquet engine is available.

### Returns
- `Path` to the written file.
