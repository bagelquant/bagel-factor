from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True, slots=True)
class TTestResult:
    statistic: float
    pvalue: float
    df: float
    mean: float
    n: int


def _as_1d(x) -> np.ndarray:
    if isinstance(x, pd.Series):
        arr = x.dropna().to_numpy(dtype=float)
    else:
        arr = np.asarray(x, dtype=float)
        arr = arr[np.isfinite(arr)]
    return arr


def ttest_1samp(x, *, popmean: float = 0.0, alternative: str = "two-sided") -> TTestResult:
    """One-sample t-test."""

    arr = _as_1d(x)
    if arr.size < 2:
        m = float(np.nanmean(arr) if arr.size else np.nan)
        return TTestResult(float("nan"), float("nan"), float("nan"), m, int(arr.size))

    res = stats.ttest_1samp(arr, popmean=popmean, alternative=alternative)
    return TTestResult(float(res.statistic), float(res.pvalue), float(arr.size - 1), float(arr.mean()), int(arr.size))


def ttest_ind(
    x,
    y,
    *,
    equal_var: bool = False,
    alternative: str = "two-sided",
) -> TTestResult:
    """Two-sample t-test (Welch by default)."""

    x1 = _as_1d(x)
    y1 = _as_1d(y)
    if x1.size < 2 or y1.size < 2:
        return TTestResult(float("nan"), float("nan"), float("nan"), float("nan"), int(min(x1.size, y1.size)))

    res = stats.ttest_ind(x1, y1, equal_var=equal_var, alternative=alternative)

    if equal_var:
        df = float(x1.size + y1.size - 2)
    else:
        vx = x1.var(ddof=1) / x1.size
        vy = y1.var(ddof=1) / y1.size
        df = float((vx + vy) ** 2 / ((vx**2) / (x1.size - 1) + (vy**2) / (y1.size - 1)))

    return TTestResult(float(res.statistic), float(res.pvalue), df, float(x1.mean() - y1.mean()), int(min(x1.size, y1.size)))
