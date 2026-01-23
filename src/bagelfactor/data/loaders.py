"""bagelfactor.data.loaders
Lightweight data loaders for common formats.

v0 proposal:
- LoadConfig dataclass to specify loading options.
- DataLoader protocol with concrete implementations for CSV, JSON, Excel, Parquet, and Pick

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Protocol,
    Union,
    Literal,
)

import pandas as pd

PATHLIKE = Union[str, Path]

"""
=== Custom Error Classes ===
"""

class LoaderError(RuntimeError):
    """Custom error for loader issues."""
    ...


class UnsupportedFormatError(LoaderError):
    """Error for unsupported data formats."""

    def __init__(self, format: str) -> None:
        super().__init__(f"Unsupported data format: {format}")

"""
=== Load Config Dataclass ===
"""

@dataclass(frozen=True, slots=True)
class LoadConfig:
    """Configuration for loading data."""

    source: PATHLIKE
    format: Optional[Literal[
        "csv", 
        "json", 
        "xlsx", 
        "parquet",
        "pickle"
        ]] = None

    # Optional common behavior
    columns: Optional[list[str]] = None
    nrows: Optional[int] = None
    postprocess: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None

    # Pass-through kwargs
    read_kwargs: Optional[Dict[str, Any]] = None


def _infer_format(source: PATHLIKE) -> str:
    """Infer the data format from the file extension."""
    suffix = Path(source).suffix.lower()
    if suffix == ".csv":
        return "csv"
    elif suffix == ".json":
        return "json"
    elif suffix in [".xlsx", ".xls"]:
        return "xlsx"
    elif suffix == ".parquet":
        return "parquet"
    elif suffix in [".pkl", ".pickle"]:
        return "pickle"
    else:
        raise UnsupportedFormatError(suffix)

"""
=== Loader Protocol ===
"""

def _add_optional_common_behavior(
        config: LoadConfig
        ) -> dict[str, Any]:
    """Apply optional common behaviors like postprocessing."""
    read_kwargs = config.read_kwargs or {}
    if config.columns and "columns" not in read_kwargs:
        read_kwargs["columns"] = config.columns
    if config.nrows and "nrows" not in read_kwargs:
        read_kwargs["nrows"] = config.nrows
    return read_kwargs


class DataLoader(Protocol):
    """Protocol for data loaders."""

    def load(self) -> pd.DataFrame:
        """Load data according to the given configuration."""
        ...


class CSVLoader:
    """Loader for CSV files."""

    def __init__(self, config: LoadConfig) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        read_kwargs = _add_optional_common_behavior(self.config)
        return pd.read_csv(self.config.source, **read_kwargs)


class JSONLoader:
    """Loader for JSON files."""

    def __init__(self, config: LoadConfig) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        read_kwargs = _add_optional_common_behavior(self.config)
        return pd.read_json(self.config.source, **read_kwargs)


class ExcelLoader:
    """Loader for Excel files."""

    def __init__(self, config: LoadConfig) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        read_kwargs = _add_optional_common_behavior(self.config)
        return pd.read_excel(self.config.source, **read_kwargs)


class ParquetLoader:
    """Loader for Parquet files."""

    def __init__(self, config: LoadConfig) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        # nrows is not supported in pd.read_parquet
        read_kwargs = self.config.read_kwargs or {}
        if self.config.columns and "columns" not in read_kwargs:
            read_kwargs["columns"] = self.config.columns
        df = pd.read_parquet(self.config.source, **read_kwargs)
        if self.config.nrows is not None:
            df = df.head(self.config.nrows)
        return df


class PickleLoader:
    """Loader for Pickle files."""

    def __init__(self, config: LoadConfig) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        read_kwargs = self.config.read_kwargs or {}
        obj = pd.read_pickle(self.config.source, **read_kwargs)
        if isinstance(obj, pd.DataFrame):
            df: pd.DataFrame = obj
        else:
            try:
                df = pd.DataFrame(obj)
            except Exception as e:
                raise LoaderError("Loaded object is not a DataFrame or Series") from e

        if self.config.columns is not None:
            df = df.loc[:, self.config.columns]
        if self.config.nrows is not None:
            df = df.head(self.config.nrows)
        return df


"""
=== Loader Registry and Factory Function ===
"""

LOADER_REGISTRY: Dict[str, Callable[[LoadConfig], DataLoader]] = {
    "csv": CSVLoader,
    "json": JSONLoader,
    "xlsx": ExcelLoader,
    "parquet": ParquetLoader,
    "pickle": PickleLoader,
}


def get_loader(config: LoadConfig) -> DataLoader:
    """Get the appropriate data loader based on the configuration."""
    format = config.format or _infer_format(config.source)
    loader_cls = LOADER_REGISTRY.get(format)
    if not loader_cls:
        raise UnsupportedFormatError(format)
    return loader_cls(config)


def load_df(config: LoadConfig) -> pd.DataFrame:
    """Load data using the specified configuration."""
    loader = get_loader(config)
    df = loader.load()
    if config.postprocess:
        df = config.postprocess(df)
    return df

