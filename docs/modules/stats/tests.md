# `bagelfactor.stats.tests`

SciPy-based t-tests.

## `TTestResult`

Frozen dataclass capturing common fields:
- `statistic: float`
- `pvalue: float`
- `df: float`
- `mean: float` — for one-sample: sample mean; for two-sample: mean difference (`x - y`)
- `n: int` — sample size (one-sample) or `min(len(x), len(y))` (two-sample)

## Internal helper

### `_as_1d(x) -> np.ndarray`

Normalizes input into a 1D finite float array.

- If `x` is a `pd.Series`, drops NaNs.
- Otherwise uses `np.asarray` then filters finite values.

## `ttest_1samp(x, *, popmean=0.0, alternative="two-sided") -> TTestResult`

One-sample t-test wrapper around `scipy.stats.ttest_1samp`.

### Edge cases
- If fewer than 2 finite observations: returns NaNs for test stats and p-value, and reports `n`.

## `ttest_ind(x, y, *, equal_var=False, alternative="two-sided") -> TTestResult`

Two-sample t-test wrapper around `scipy.stats.ttest_ind`.

### Notes
- Defaults to Welch's t-test (`equal_var=False`).
- Degrees of freedom are reported as:
  - `n_x + n_y - 2` for equal-variance
  - Welch-Satterthwaite approximation otherwise

### Edge cases
- If either sample has fewer than 2 observations: returns NaNs.
