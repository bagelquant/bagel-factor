"""bagelfactor.data.universe

Universe membership masks and optional group labels.

v0 proposal: Universe is a membership mask over (date, asset) with optional group labels.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .panel import validate_panel


@dataclass(frozen=True, slots=True)
class Universe:
    mask: pd.Series
    labels: pd.DataFrame | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mask.index, pd.MultiIndex):
            raise TypeError("Universe.mask must be indexed by (date, asset)")
        if list(self.mask.index.names) != ["date", "asset"]:
            # normalize index names to expected order; allow None entries
            object.__setattr__(
                self,
                "mask",
                self.mask.copy().rename_axis(["date", "asset"]),
            )
        if self.labels is not None:
            validate_panel(self.labels)

    def apply(self, panel: pd.DataFrame) -> pd.DataFrame:
        """Filter a panel to universe membership (mask == True)."""

        validate_panel(panel)
        m = self.mask.reindex(panel.index).fillna(False)
        return panel.loc[m]
