from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from bagelfactor.data.panel import validate_panel


@dataclass(frozen=True, slots=True)
class DropNa:
    """Drop rows where `column` is NaN."""

    column: str

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        validate_panel(panel)
        return panel.dropna(subset=[self.column])


@dataclass(frozen=True, slots=True)
class Clip:
    """Clip a column to [lower, upper]."""

    column: str
    lower: float | None = None
    upper: float | None = None

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        validate_panel(panel)
        out = panel.copy()
        out[self.column] = out[self.column].clip(lower=self.lower, upper=self.upper)
        return out


@dataclass(frozen=True, slots=True)
class ZScore:
    """Cross-sectional z-score per date for `column`.

    Uses population std (ddof=0). If std == 0, returns NaN for that date.
    """

    column: str

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        validate_panel(panel)
        out = panel.copy()

        def _z(s: pd.Series) -> pd.Series:
            mu = s.mean()
            sd = s.std(ddof=0)
            if sd == 0 or pd.isna(sd):
                return s * pd.NA
            return (s - mu) / sd

        out[self.column] = out[self.column].groupby(level="date", sort=False).transform(_z)
        return out


@dataclass(frozen=True, slots=True)
class Rank:
    """Cross-sectional rank per date for `column`.

    Ranks are scaled to [0, 1] when `pct=True` (default).

    Default `method="first"` makes ranking deterministic under ties.
    """

    column: str
    pct: bool = True
    method: str = "first"

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        validate_panel(panel)
        out = panel.copy()
        out[self.column] = out[self.column].groupby(level="date", sort=False).rank(
            pct=self.pct, method=self.method
        )
        return out
