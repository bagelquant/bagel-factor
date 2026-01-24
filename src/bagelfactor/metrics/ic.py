from __future__ import annotations

import pandas as pd
import numpy as np

from bagelfactor.data.panel import validate_panel


def ic_series(
    panel: pd.DataFrame,
    *,
    factor: str,
    label: str,
    method: str = "spearman",
) -> pd.Series:
    """Compute per-date information coefficient between `factor` and `label`.

    Notes:
    - `method="spearman"` is implemented via cross-sectional ranking + Pearson correlation
      (no SciPy dependency).
    """

    validate_panel(panel)
    if factor not in panel.columns:
        raise KeyError(f"Missing factor column: {factor!r}")
    if label not in panel.columns:
        raise KeyError(f"Missing label column: {label!r}")

    if method not in {"spearman", "pearson"}:
        raise ValueError("method must be 'spearman' or 'pearson'")

    df = panel[[factor, label]].dropna()

    # Vectorized per-date correlation using group aggregations for performance
    if df.empty:
        return pd.Series(dtype=float, name="ic")

    if method == "spearman":
        x = df.groupby(level="date")[factor].rank(method="average")
        y = df.groupby(level="date")[label].rank(method="average")
    else:
        x = df[factor]
        y = df[label]

    w = pd.DataFrame({"x": x, "y": y}, index=df.index)
    w["xy"] = w["x"] * w["y"]
    w["x2"] = w["x"] * w["x"]
    w["y2"] = w["y"] * w["y"]

    g = (
        w.groupby(level="date", sort=False)
        .agg(
            n=("x", "size"),
            sum_x=("x", "sum"),
            sum_y=("y", "sum"),
            sum_xy=("xy", "sum"),
            sum_x2=("x2", "sum"),
            sum_y2=("y2", "sum"),
        )
    )

    n = g["n"].astype(float)
    mean_x = g["sum_x"] / n
    mean_y = g["sum_y"] / n
    cov = g["sum_xy"] / n - mean_x * mean_y
    var_x = g["sum_x2"] / n - mean_x * mean_x
    var_y = g["sum_y2"] / n - mean_y * mean_y

    denom = np.sqrt((var_x * var_y).clip(lower=0))

    corr = cov / denom
    mask = (n < 2) | (denom == 0) | (denom.isna())
    corr[mask] = float("nan")

    return corr.rename("ic")


def icir(ic: pd.Series) -> float:
    """IC information ratio: mean(IC) / std(IC)."""

    ic = ic.dropna()
    if len(ic) == 0:
        return float("nan")
    sd = ic.std(ddof=0)
    if sd == 0 or pd.isna(sd):
        return float("nan")
    return float(ic.mean() / sd)
