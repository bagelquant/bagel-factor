from __future__ import annotations

import pandas as pd

from bagelfactor.data.panel import validate_panel


def assign_quantiles(
    panel: pd.DataFrame,
    *,
    factor: str,
    n_quantiles: int = 5,
) -> pd.Series:
    """Assign cross-sectional quantiles (1..n) per date based on factor ranks.

    Returns a Series indexed by the same (date, asset) index as `panel`.
    """

    validate_panel(panel)
    if n_quantiles < 2:
        raise ValueError("n_quantiles must be >= 2")
    if factor not in panel.columns:
        raise KeyError(f"Missing factor column: {factor!r}")

    s = panel[factor]

    def _q(x: pd.Series) -> pd.Series:
        mask = x.notna()
        if mask.sum() == 0:
            return pd.Series(pd.NA, index=x.index, dtype="Int64")

        r = x[mask].rank(method="first")
        q = pd.qcut(r, q=n_quantiles, labels=False, duplicates="drop")

        out = pd.Series(pd.NA, index=x.index, dtype="Int64")
        out.loc[mask] = (q + 1).astype("Int64")
        return out

    out = s.groupby(level="date", sort=False).transform(_q)
    out.name = "quantile"
    return out


def quantile_returns(
    panel: pd.DataFrame,
    *,
    quantile: pd.Series,
    label: str,
) -> pd.DataFrame:
    """Compute mean label return per (date, quantile)."""

    validate_panel(panel)
    if label not in panel.columns:
        raise KeyError(f"Missing label column: {label!r}")

    q = quantile.reindex(panel.index)
    df = pd.DataFrame({"q": q, "y": panel[label]}, index=panel.index).dropna()

    out = (
        df.groupby([pd.Grouper(level="date"), "q"], sort=False)["y"]
        .mean()
        .unstack("q")
        .sort_index(axis=1)
    )
    out.columns = [int(c) for c in out.columns]
    return out
