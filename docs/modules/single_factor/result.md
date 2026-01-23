# `bagelfactor.single_factor.result`

Result container for single-factor evaluation.

## `SingleFactorResult`

A frozen dataclass that groups the outputs of `SingleFactorJob.run`.

### Fields
- `factor: str`
- `horizons: tuple[int, ...]`

Per-horizon outputs (keyed by horizon integer):
- `ic: dict[int, pd.Series]`
- `icir: dict[int, float]`
- `quantile_returns: dict[int, pd.DataFrame]`
- `long_short: dict[int, pd.Series]`
- `turnover: dict[int, pd.Series]`

Cross-horizon output:
- `coverage: pd.Series`

### Notes
- Series/DataFrames are typically indexed by `date` (and sometimes `quantile`), and are meant to be directly plotted/exported.
- The class contains no methods; it is a simple structured return type.
