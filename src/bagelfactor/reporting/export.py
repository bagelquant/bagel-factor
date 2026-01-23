from __future__ import annotations

from pathlib import Path

import pandas as pd


def to_csv(obj: pd.DataFrame | pd.Series, path: str | Path, *, index: bool = True) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, pd.Series):
        obj.to_frame().to_csv(p, index=index)
    else:
        obj.to_csv(p, index=index)
    return p


def to_parquet(obj: pd.DataFrame | pd.Series, path: str | Path) -> Path:
    """Write to parquet.

    Requires an optional parquet engine (pyarrow or fastparquet).
    """

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        if isinstance(obj, pd.Series):
            obj.to_frame().to_parquet(p)
        else:
            obj.to_parquet(p)
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Parquet export requires 'pyarrow' or 'fastparquet' to be installed."
        ) from e
    return p
