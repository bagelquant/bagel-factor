import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import add_forward_returns, ensure_panel_index  # noqa: E402
from bagelfactor.metrics import (  # noqa: E402
    assign_quantiles,
    coverage_by_date,
    ic_series,
    icir,
    quantile_returns,
)


def _panel() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-02"],
            "asset": ["A", "B", "A", "B"],
            "close": [10.0, 20.0, 11.0, 18.0],
            "f": [1.0, 2.0, 1.5, 0.5],
        }
    )
    panel = ensure_panel_index(df)
    return add_forward_returns(panel, price="close", horizons=(1,))


def test_ic_series_spearman() -> None:
    panel = _panel()
    ic = ic_series(panel, factor="f", label="ret_fwd_1", method="spearman")
    # last day has NaN forward returns, so only the first date is defined
    assert set(ic.index) == {pd.Timestamp("2020-01-01")}


def test_icir_basic() -> None:
    x = pd.Series([1.0, 2.0, 3.0])
    assert icir(x) == pytest.approx(x.mean() / x.std(ddof=1))


def test_assign_quantiles_and_quantile_returns() -> None:
    panel = _panel()
    q = assign_quantiles(panel, factor="f", n_quantiles=2)
    qr = quantile_returns(panel, quantile=q, label="ret_fwd_1")
    assert set(qr.columns) <= {1, 2}


def test_coverage_by_date() -> None:
    panel = ensure_panel_index(
        pd.DataFrame(
            {
                "date": ["2020-01-01", "2020-01-01"],
                "asset": ["A", "B"],
                "x": [1.0, None],
            }
        )
    )
    cov = coverage_by_date(panel, column="x")
    assert cov.loc[pd.Timestamp("2020-01-01")] == pytest.approx(0.5)
