"""bagelfactor.data.align

Point-in-time alignment helpers.

v0 proposal: avoid lookahead via explicit lagging rules and alignment.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

import pandas as pd

from .panel import validate_panel


AlignMethod = Literal["raw", "ffill"]


def align_to_calendar(
    panel: pd.DataFrame,
    trade_calendar: pd.DatetimeIndex,
    *,
    method: AlignMethod = "raw",
) -> pd.DataFrame:
    """Align a canonical panel to a provided trading calendar."""

    validate_panel(panel)

    cal = pd.DatetimeIndex(trade_calendar)
    if cal.tz is not None:
        cal = cal.tz_localize(None)
    cal = cal.sort_values().unique()

    assets = panel.index.get_level_values("asset").unique()
    target_index = pd.MultiIndex.from_product([cal, assets], names=["date", "asset"])

    out = panel.reindex(target_index)
    if method == "ffill":
        out = out.groupby(level="asset", sort=False).ffill()
    return out


def lag_by_asset(
    panel: pd.DataFrame,
    columns: Iterable[str],
    *,
    periods: int = 1,
) -> pd.DataFrame:
    """Lag the given columns by ``periods`` within each asset."""

    validate_panel(panel)
    out = panel.copy()
    cols = list(columns)
    missing = [c for c in cols if c not in out.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    out.loc[:, cols] = out.loc[:, cols].groupby(level="asset", sort=False).shift(periods)
    return out
