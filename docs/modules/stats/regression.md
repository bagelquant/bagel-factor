# `bagelfactor.stats.regression`

statsmodels-based OLS helpers.

## `OLSResult`

Frozen dataclass with:
- `alpha: float` — intercept estimate
- `tstat: float` — intercept t-statistic
- `pvalue: float` — intercept p-value
- `nobs: int` — number of observations used
- `rsquared: float`

## `ols_alpha_tstat(y, x=None, *, add_const=True) -> OLSResult`

Fit OLS and return intercept (alpha) statistics.

### Behavior
- If `x is None`, performs a mean test: `y ~ 1`.
- Else, aligns `x` to `y` by index and fits: `y ~ 1 + x`.
- Uses `sm.add_constant(..., has_constant="add")` when `add_const=True`.

### Edge cases
- If fewer than 3 observations after dropping NaNs/alignment: returns NaNs.

## `ols_summary(y, x=None, *, add_const=True) -> str`

Return `statsmodels` text summary (`str(res.summary())`).

### Notes
- Unlike `ols_alpha_tstat`, this function does not have a minimum-length guard; it will raise if statsmodels cannot fit.
