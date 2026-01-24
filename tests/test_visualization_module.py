import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

mpl = pytest.importorskip("matplotlib")

from bagelfactor.visualization import (  # noqa: E402
    plot_coverage_time_series,
    plot_ic_hist,
    plot_ic_time_series,
    plot_long_short_time_series,
    plot_quantile_returns_heatmap,
    plot_quantile_returns_time_series,
    plot_result_summary,
    plot_turnover_heatmap,
    plot_turnover_time_series,
)


def test_plot_helpers_smoke() -> None:
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    ic = pd.Series([0.1, -0.2, 0.05, 0.0, 0.3], index=idx, name="ic")
    ax1 = plot_ic_time_series(ic)
    assert ax1.figure is not None

    ax2 = plot_ic_hist(ic)
    assert ax2.figure is not None

    qr = pd.DataFrame({1: [0.01, 0.02, -0.01, 0.00, 0.03], 2: [0.02, 0.01, 0.00, 0.01, 0.04]}, index=idx)
    ax3 = plot_quantile_returns_time_series(qr)
    assert ax3.figure is not None

    ax4 = plot_quantile_returns_heatmap(qr)
    assert ax4.figure is not None

    ls = pd.Series([0.01, -0.02, 0.01, 0.0, 0.02], index=idx, name="long_short")
    ax5 = plot_long_short_time_series(ls)
    assert ax5.figure is not None

    cov = pd.Series([1.0, 0.9, 0.95, 0.8, 1.0], index=idx, name="coverage")
    ax6 = plot_coverage_time_series(cov)
    assert ax6.figure is not None

    mpl.pyplot.close("all")


def test_plot_turnover_time_series_smoke() -> None:
    """Test plot_turnover_time_series with basic data."""
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    # Create multi-index turnover data (date, quantile)
    dates = idx.repeat(3)
    quantiles = [1, 2, 3] * 5
    turnover = pd.Series(
        [0.1, 0.2, 0.15, 0.12, 0.18, 0.16, 0.11, 0.19, 0.14, 0.13, 0.17, 0.15, 0.12, 0.20, 0.16],
        index=pd.MultiIndex.from_arrays([dates, quantiles], names=["date", "quantile"]),
        name="turnover",
    )
    
    # Test default behavior
    ax1 = plot_turnover_time_series(turnover)
    assert ax1.figure is not None
    
    # Test with quantiles filter
    ax2 = plot_turnover_time_series(turnover, quantiles=[1, 3])
    assert ax2.figure is not None
    
    # Test with average mode
    ax3 = plot_turnover_time_series(turnover, average=True)
    assert ax3.figure is not None
    
    mpl.pyplot.close("all")


def test_plot_turnover_heatmap_smoke() -> None:
    """Test plot_turnover_heatmap with basic data."""
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    dates = idx.repeat(3)
    quantiles = [1, 2, 3] * 5
    turnover = pd.Series(
        [0.1, 0.2, 0.15, 0.12, 0.18, 0.16, 0.11, 0.19, 0.14, 0.13, 0.17, 0.15, 0.12, 0.20, 0.16],
        index=pd.MultiIndex.from_arrays([dates, quantiles], names=["date", "quantile"]),
        name="turnover",
    )
    
    ax = plot_turnover_heatmap(turnover)
    assert ax.figure is not None
    
    mpl.pyplot.close("all")


def test_plot_result_summary_smoke() -> None:
    """Test plot_result_summary with a mock SingleFactorResult."""
    from collections import namedtuple
    
    # Create a mock result object with required attributes
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    
    MockResult = namedtuple("MockResult", ["factor", "horizons", "ic", "quantile_returns", "long_short", "coverage"])
    
    result = MockResult(
        factor="test_factor",
        horizons=[1, 5],
        ic={
            1: pd.Series([0.1, -0.2, 0.05, 0.0, 0.3, 0.15, -0.1, 0.2, 0.1, 0.05], index=idx, name="ic"),
            5: pd.Series([0.2, -0.1, 0.1, 0.05, 0.25, 0.1, -0.05, 0.15, 0.12, 0.08], index=idx, name="ic"),
        },
        quantile_returns={
            1: pd.DataFrame(
                {1: [0.01, 0.02, -0.01, 0.00, 0.03, 0.01, -0.01, 0.02, 0.01, 0.00],
                 2: [0.02, 0.01, 0.00, 0.01, 0.04, 0.02, 0.00, 0.03, 0.02, 0.01]},
                index=idx
            ),
            5: pd.DataFrame(
                {1: [0.02, 0.03, -0.02, 0.01, 0.04, 0.02, -0.02, 0.03, 0.02, 0.01],
                 2: [0.03, 0.02, 0.01, 0.02, 0.05, 0.03, 0.01, 0.04, 0.03, 0.02]},
                index=idx
            ),
        },
        long_short={
            1: pd.Series([0.01, -0.02, 0.01, 0.0, 0.02, 0.01, -0.01, 0.02, 0.01, 0.00], index=idx, name="long_short"),
            5: pd.Series([0.02, -0.01, 0.02, 0.01, 0.03, 0.02, -0.02, 0.03, 0.02, 0.01], index=idx, name="long_short"),
        },
        coverage=pd.Series([1.0, 0.9, 0.95, 0.8, 1.0, 0.95, 0.9, 0.85, 0.9, 0.95], index=idx, name="coverage"),
    )
    
    # Test with default horizon (should pick first available)
    fig1 = plot_result_summary(result)
    assert fig1 is not None
    
    # Test with explicit horizon
    fig2 = plot_result_summary(result, horizon=5)
    assert fig2 is not None
    
    mpl.pyplot.close("all")
