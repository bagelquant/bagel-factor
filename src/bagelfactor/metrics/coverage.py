from __future__ import annotations

import pandas as pd

from bagelfactor.data.panel import validate_panel


def coverage_by_date(panel: pd.DataFrame, *, column: str) -> pd.Series:
    """Fraction of non-NaN observations per date for `column`."""

    validate_panel(panel)
    if column not in panel.columns:
        raise KeyError(f"Missing column: {column!r}")

    s = panel[column]
    # Vectorized: compute fraction of non-NA per date using groupby mean on boolean mask
    return s.notna().groupby(level="date", sort=False).mean().astype(float).rename("coverage")
