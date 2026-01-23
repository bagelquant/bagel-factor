from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd


class Transform:
    def fit(self, panel: pd.DataFrame) -> "Transform":  # pragma: no cover
        return self

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Pipeline:
    """A simple fit/transform pipeline.

    Each step must implement `transform(panel) -> panel`.
    """

    steps: tuple[Transform, ...]

    def __init__(self, steps: Iterable[Transform]):
        object.__setattr__(self, "steps", tuple(steps))

    def fit(self, panel: pd.DataFrame) -> "Pipeline":
        for step in self.steps:
            step.fit(panel)
            panel = step.transform(panel)
        return self

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        out = panel
        for step in self.steps:
            out = step.transform(out)
        return out

    def fit_transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        self.fit(panel)
        return self.transform(panel)
