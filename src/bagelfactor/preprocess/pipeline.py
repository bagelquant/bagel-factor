from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class Transform(Protocol):
    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Pipeline:
    """
    A simple transform pipeline.

    Each step must implement `transform(panel) -> panel`.
    """

    steps: tuple[Transform, ...]

    def __init__(self, steps: Iterable[Transform]):
        object.__setattr__(self, "steps", tuple(steps))

    def transform(self, panel: pd.DataFrame) -> pd.DataFrame:
        out = panel
        for step in self.steps:
            out = step.transform(out)
        return out
