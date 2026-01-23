from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class SingleFactorResult:
    factor: str
    horizons: tuple[int, ...]

    ic: dict[int, pd.Series]
    icir: dict[int, float]

    quantile_returns: dict[int, pd.DataFrame]
    long_short: dict[int, pd.Series]

    turnover: dict[int, pd.Series]
    coverage: pd.Series
