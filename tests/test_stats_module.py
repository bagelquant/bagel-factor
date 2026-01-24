import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.stats import ols_alpha_tstat, ols_summary, ttest_1samp, ttest_ind  # noqa: E402


def test_ttest_1samp_detects_nonzero_mean() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(loc=0.1, scale=0.05, size=200)
    res = ttest_1samp(x, popmean=0.0)
    assert res.pvalue < 1e-8


def test_ols_alpha_tstat_smoke() -> None:
    y = np.array([0.01] * 100)
    out = ols_alpha_tstat(y)
    assert out.nobs == 100


def test_ttest_ind_smoke() -> None:
    """Test ttest_ind with basic data."""
    rng = np.random.default_rng(42)
    x = rng.normal(loc=0.1, scale=0.05, size=100)
    y = rng.normal(loc=0.0, scale=0.05, size=100)
    res = ttest_ind(x, y)
    assert res.n > 0
    assert not np.isnan(res.statistic)
    assert not np.isnan(res.pvalue)


def test_ttest_ind_with_nans() -> None:
    """Test ttest_ind handles NaN values correctly."""
    x = np.array([1.0, 2.0, np.nan, 3.0, 4.0])
    y = np.array([0.5, 1.5, 2.5, np.nan, 3.5])
    res = ttest_ind(x, y)
    assert res.n > 0  # Should have valid observations
    assert not np.isnan(res.statistic)


def test_ttest_ind_small_sample() -> None:
    """Test ttest_ind with small sample sizes."""
    x = np.array([1.0])
    y = np.array([2.0, 3.0])
    res = ttest_ind(x, y)
    # Should return NaN for insufficient data
    assert np.isnan(res.statistic)


def test_ols_summary_smoke() -> None:
    """Test ols_summary returns a summary string."""
    rng = np.random.default_rng(123)
    y = rng.normal(loc=0.05, scale=0.02, size=50)
    x = rng.normal(loc=0.0, scale=0.01, size=50)
    summary = ols_summary(y, x)
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "OLS Regression Results" in summary


def test_ols_summary_mean_test() -> None:
    """Test ols_summary for mean test (x=None)."""
    y = np.array([0.01] * 30)
    summary = ols_summary(y, x=None)
    assert isinstance(summary, str)
    assert "OLS Regression Results" in summary


def test_ols_alpha_tstat_with_array_x() -> None:
    """Test ols_alpha_tstat with array-like x that should align by position."""
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    x = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    result = ols_alpha_tstat(y, x)
    # Should not return NaN for valid aligned data
    assert not np.isnan(result.alpha)
    assert not np.isnan(result.tstat)
    assert result.nobs == 5
