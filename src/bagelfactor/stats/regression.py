from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import statsmodels.api as sm


@dataclass(frozen=True, slots=True)
class OLSResult:
    alpha: float
    tstat: float
    pvalue: float
    nobs: int
    rsquared: float


def ols_alpha_tstat(y, x=None, *, add_const: bool = True) -> OLSResult:
    """OLS regression returning intercept (alpha) t-stat.

    - Mean test: y ~ 1 (x=None)
    - Alpha vs benchmark: y ~ 1 + x

    Note on index alignment:
    - If x has a RangeIndex or length matches y, uses position-based alignment
    - Otherwise uses index-based alignment with reindexing
    - This allows flexibility for common use cases (time series without explicit index)

    Parameters
    ----------
    y : array-like or pd.Series
        Dependent variable
    x : array-like or pd.Series, optional
        Independent variable (if None, performs mean test)
    add_const : bool
        Whether to add intercept term

    Returns
    -------
    OLSResult
        Regression results with alpha, t-stat, p-value, nobs, r-squared
    """

    yv = pd.Series(y).dropna().astype(float)
    if x is None:
        X = pd.DataFrame(index=yv.index)
    else:
        xv = pd.Series(x)
        # If x has a default RangeIndex or length matches y, align by position
        if isinstance(xv.index, pd.RangeIndex) or len(xv) == len(yv):
            xv = pd.Series(xv.values, index=yv.index)
        X = pd.DataFrame({"x": xv.reindex(yv.index)}).dropna()
        yv = yv.reindex(X.index)

    if add_const:
        X = sm.add_constant(X, has_constant="add")

    if len(yv) < 3:
        return OLSResult(float("nan"), float("nan"), float("nan"), int(len(yv)), float("nan"))

    res = sm.OLS(yv.to_numpy(), X.to_numpy()).fit()
    return OLSResult(
        alpha=float(res.params[0]),
        tstat=float(res.tvalues[0]),
        pvalue=float(res.pvalues[0]),
        nobs=int(res.nobs),
        rsquared=float(res.rsquared),
    )


def ols_summary(y, x=None, *, add_const: bool = True) -> str:
    """Return statsmodels summary text."""

    yv = pd.Series(y).dropna().astype(float)
    if x is None:
        X = pd.DataFrame(index=yv.index)
    else:
        xv = pd.Series(x)
        # If x has a default RangeIndex or length matches y, align by position
        if isinstance(xv.index, pd.RangeIndex) or len(xv) == len(yv):
            xv = pd.Series(xv.values, index=yv.index)
        X = pd.DataFrame({"x": xv.reindex(yv.index)}).dropna()
        yv = yv.reindex(X.index)

    if add_const:
        X = sm.add_constant(X, has_constant="add")

    res = sm.OLS(yv.to_numpy(), X.to_numpy()).fit()
    return str(res.summary())
