# `bagelfactor.stats`

Common statistical tests and regressions.

## Public API

```python
from bagelfactor.stats import ttest_1samp, ttest_ind, ols_alpha_tstat, ols_summary
```

## Detailed docs

- [`tests`](./tests.md)
- [`regression`](./regression.md)

## Examples

### Test if IC mean is different from 0

```python
from bagelfactor.stats import ttest_1samp

out = ttest_1samp(res.ic[1], popmean=0.0)
print(out.statistic, out.pvalue)
```

### Regression alpha (y ~ 1 + x)

```python
from bagelfactor.stats import ols_alpha_tstat

out = ols_alpha_tstat(long_short, benchmark)
print(out.alpha, out.tstat, out.pvalue)
```
