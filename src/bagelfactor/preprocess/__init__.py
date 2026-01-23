"""bagelfactor.preprocess

Composable preprocessing utilities for factor evaluation.

v0 goal: keep this lightweight and pandas-first.
"""

from .pipeline import Pipeline
from .transforms import Clip, DropNa, Rank, ZScore

__all__ = [
    "Pipeline",
    "Clip",
    "DropNa",
    "Rank",
    "ZScore",
]
