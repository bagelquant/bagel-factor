# `bagelfactor.single_factor.job`

Single-factor evaluation entrypoint.

## `SingleFactorJob`

A stateless runner that takes a canonical `(date, asset)` panel and produces a `SingleFactorResult` containing common factor-research diagnostics.

### `SingleFactorJob.run(panel, factor, *, price="close", horizons=(1,5,20), universe=None, preprocess=None, n_quantiles=5, ic_method="spearman") -> SingleFactorResult`

#### Parameters
- `panel: pd.DataFrame`
  - Either already indexed by `(date, asset)` or convertible via `ensure_panel_index`.
- `factor: str`
  - Factor column name (signal to evaluate).
- `price: str`
  - Price column used to build forward returns via `add_forward_returns`.
- `horizons: tuple[int, ...]`
  - Forward-return horizons (in rows/dates per asset) to evaluate.
- `universe: Universe | None`
  - Optional membership mask to filter the panel before evaluation.
- `preprocess: Pipeline | None`
  - Optional preprocessing pipeline applied before returns/metrics.
- `n_quantiles: int`
  - Number of quantiles for bucketed returns + turnover.
- `ic_method: str`
  - Correlation method for IC, forwarded to `ic_series`.

#### Computation flow
1. Ensure/normalize panel index (`ensure_panel_index`), then validate (`validate_panel`).
2. Apply `universe.apply(panel)` if provided.
3. Apply `preprocess.transform(panel)` if provided.
4. Add forward return labels `ret_fwd_{h}` using `add_forward_returns`.
5. Compute coverage: `coverage_by_date(panel, column=factor)`.
6. Assign quantiles once using `assign_quantiles(panel, factor, n_quantiles)`.
7. For each horizon `h`:
   - IC series: `ic_series(panel, factor, label=f"ret_fwd_{h}", method=ic_method)`
   - ICIR scalar: `icir(ic_h)`
   - Quantile returns: `quantile_returns(panel, quantile=q, label=ret_fwd_h)`
   - Long-short: `Q{n_quantiles} - Q1` if both exist
   - Turnover: `quantile_turnover(q, n_quantiles=n_quantiles)`

#### Returns
A `SingleFactorResult` with:
- `ic[h]`: per-date IC series
- `icir[h]`: scalar ICIR
- `quantile_returns[h]`: `date x quantile` mean returns
- `long_short[h]`: per-date long-short series
- `turnover[h]`: `(date, quantile)` turnover series
- `coverage`: per-date factor coverage

#### Example
```python
from bagelfactor.single_factor import SingleFactorJob

res = SingleFactorJob.run(panel, factor="alpha", horizons=(1, 5, 20), n_quantiles=5)
print(res.icir[5])
```
