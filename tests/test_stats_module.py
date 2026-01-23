import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.stats import ols_alpha_tstat, ttest_1samp  # noqa: E402


def test_ttest_1samp_detects_nonzero_mean() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(loc=0.1, scale=0.05, size=200)
    res = ttest_1samp(x, popmean=0.0)
    assert res.pvalue < 1e-8


def test_ols_alpha_tstat_smoke() -> None:
    y = np.array([0.01] * 100)
    out = ols_alpha_tstat(y)
    assert out.nobs == 100
