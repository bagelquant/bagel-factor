from __future__ import annotations

import pandas as pd

from bagelfactor.data.panel import validate_panel


def coverage_by_date(panel: pd.DataFrame, *, column: str) -> pd.Series:
    """Fraction of non-NaN observations per date for `column`."""

    validate_panel(panel)
    if column not in panel.columns:
        raise KeyError(f"Missing column: {column!r}")

    s = panel[column]
    def _cov(x: pd.Series) -> float:
        return float(x.notna().mean()) if len(x) else float("nan")

    return s.groupby(level="date", sort=False).apply(_cov).rename("coverage")
