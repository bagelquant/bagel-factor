"""bagelfactor.data.factors

Lightweight factor containers.

v0 proposal:
- FactorSeries: one score per (date, asset) plus metadata.
- FactorMatrix: multiple factors aligned to (date, asset).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .panel import ensure_panel_index, validate_panel


@dataclass(frozen=True, slots=True)
class FactorSeries:
    name: str
    values: pd.Series
    meta: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.values.index, pd.MultiIndex):
            raise TypeError("FactorSeries.values must be indexed by (date, asset)")
        if self.values.index.names != ["date", "asset"]:
            object.__setattr__(
                self,
                "values",
                self.values.copy().rename_axis(["date", "asset"]),
            )

    def to_frame(self, *, column: str | None = None) -> pd.DataFrame:
        """Convert to a single-column DataFrame."""

        return self.values.to_frame(name=column or self.name)


@dataclass(frozen=True, slots=True)
class FactorMatrix:
    values: pd.DataFrame
    meta: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        validate_panel(self.values)

    @classmethod
    def from_columns(
        cls, panel: pd.DataFrame, factors: list[str], *, meta: dict[str, Any] | None = None
    ) -> FactorMatrix:
        """Build a FactorMatrix from factor columns already present in a panel."""

        p = ensure_panel_index(panel, source="index")
        missing = [c for c in factors if c not in p.columns]
        if missing:
            raise KeyError(f"Missing factor columns: {missing}")
        return cls(p.loc[:, factors], meta=meta)
