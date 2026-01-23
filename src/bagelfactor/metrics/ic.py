from __future__ import annotations

import pandas as pd

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

    def _ic(g: pd.DataFrame) -> float:
        if len(g) < 2:
            return float("nan")
        x = g[factor]
        y = g[label]
        if method == "spearman":
            x = x.rank(method="average")
            y = y.rank(method="average")
        return float(x.corr(y, method="pearson"))

    return df.groupby(level="date", sort=False).apply(_ic).rename("ic")


def icir(ic: pd.Series) -> float:
    """IC information ratio: mean(IC) / std(IC)."""

    ic = ic.dropna()
    if len(ic) == 0:
        return float("nan")
    sd = ic.std(ddof=0)
    if sd == 0 or pd.isna(sd):
        return float("nan")
    return float(ic.mean() / sd)
