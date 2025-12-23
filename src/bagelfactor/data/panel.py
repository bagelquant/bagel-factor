"""bagelfactor.data.panel

Canonical panel utilities.

v0 proposal: internal representation is a panel indexed by (date, asset).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

import pandas as pd


IndexLike = Literal["index", "columns"]


def ensure_panel_index(
    df: pd.DataFrame,
    *,
    date: str = "date",
    asset: str = "asset",
    source: IndexLike = "columns",
    sort: bool = True,
) -> pd.DataFrame:
    """Return a copy of ``df`` indexed by (date, asset)."""

    out = df.copy()

    if source == "columns":
        if date not in out.columns or asset not in out.columns:
            raise KeyError(f"Panel requires columns {date!r} and {asset!r}")
        out[date] = pd.to_datetime(out[date])
        out = out.set_index([date, asset])
    else:
        if not isinstance(out.index, pd.MultiIndex):
            raise TypeError("Panel index must be a MultiIndex")
        if out.index.names != [date, asset]:
            out.index = out.index.set_names([date, asset])

    if sort:
        out = out.sort_index()

    return out


def validate_panel(panel: pd.DataFrame, *, date: str = "date", asset: str = "asset") -> None:
    """Validate the canonical panel invariants."""

    if not isinstance(panel.index, pd.MultiIndex):
        raise TypeError("panel must be indexed by a MultiIndex")
    if panel.index.names != [date, asset]:
        raise ValueError(f"panel index names must be {[date, asset]!r}")


def add_returns(
    panel: pd.DataFrame,
    *,
    price: str = "close",
    ret_1d: str = "ret_1d",
) -> pd.DataFrame:
    """Add simple 1D returns computed from ``price`` (per-asset)."""

    validate_panel(panel)
    out = panel.copy()
    out[ret_1d] = out[price].groupby(level="asset", sort=False).pct_change().astype("float64")
    return out


def add_forward_returns(
    panel: pd.DataFrame,
    *,
    price: str = "close",
    horizons: Iterable[int] = (1, 5, 20),
    prefix: str = "ret_fwd_",
) -> pd.DataFrame:
    """Add forward return labels ``{prefix}{h}`` computed from ``price`` (per-asset)."""

    validate_panel(panel)
    out = panel.copy()
    g = out[price].groupby(level="asset", sort=False)
    for h in horizons:
        if h <= 0:
            raise ValueError("horizons must be positive")
        out[f"{prefix}{h}"] = (g.shift(-h) / out[price] - 1.0).astype("float64")
    return out
