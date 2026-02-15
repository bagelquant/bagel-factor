from __future__ import annotations

import pandas as pd


def quantile_turnover(
    quantile: pd.Series,
    *,
    n_quantiles: int,
) -> pd.Series:
    """Compute per-date turnover for each quantile.

    Turnover(q, t) = 1 - |members(q,t) ∩ members(q,t-1)| / |members(q,t) ∪ members(q,t-1)|

    Note: If a quantile has zero members on both consecutive dates, no turnover
    value is computed for that (date, quantile) pair. This results in a sparse
    series where missing values indicate "not applicable" rather than "zero turnover".

    Returns a MultiIndex Series indexed by (date, quantile).

    Parameters
    ----------
    quantile : pd.Series
        Quantile assignments indexed by (date, asset)
    n_quantiles : int
        Total number of quantiles (used to iterate over all possible quantiles)

    Returns
    -------
    pd.Series
        Turnover values indexed by (date, quantile)
    """

    if not isinstance(quantile.index, pd.MultiIndex):
        raise TypeError("quantile must be indexed by (date, asset)")

    q = quantile.dropna().astype(int)
    dates = q.index.get_level_values("date")
    if dates.nunique() < 2:
        return pd.Series(dtype="float64")

    # Build membership sets per (date, q)
    members: dict[tuple[pd.Timestamp, int], set] = {}
    for (d, a), qq in q.items():
        members.setdefault((d, int(qq)), set()).add(a)

    uniq_dates = sorted(set(dates))
    rows: list[tuple[pd.Timestamp, int]] = []
    vals: list[float] = []

    for i in range(1, len(uniq_dates)):
        d0, d1 = uniq_dates[i - 1], uniq_dates[i]
        for k in range(1, n_quantiles + 1):
            s0 = members.get((d0, k), set())
            s1 = members.get((d1, k), set())
            if not s0 and not s1:
                continue
            inter = len(s0 & s1)
            union = len(s0 | s1)
            rows.append((d1, k))
            vals.append(1.0 - inter / union)

    out = pd.Series(vals, index=pd.MultiIndex.from_tuples(rows, names=["date", "quantile"]))
    out.name = "turnover"
    return out
