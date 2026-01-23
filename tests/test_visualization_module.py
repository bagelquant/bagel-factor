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
