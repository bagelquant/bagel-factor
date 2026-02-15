import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import Universe, ensure_panel_index  # noqa: E402
from bagelfactor.preprocess import Pipeline, Rank  # noqa: E402
from bagelfactor.single_factor import SingleFactorJob  # noqa: E402


def _panel() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "date": [
                "2020-01-01",
                "2020-01-01",
                "2020-01-02",
                "2020-01-02",
                "2020-01-03",
                "2020-01-03",
            ],
            "asset": ["A", "B", "A", "B", "A", "B"],
            "close": [10.0, 20.0, 11.0, 19.0, 12.0, 18.0],
            "alpha": [1.0, 2.0, 1.5, 0.5, 1.2, 0.2],
        }
    )
    return ensure_panel_index(df)


def test_single_factor_job_smoke() -> None:
    panel = _panel()
    res = SingleFactorJob.run(panel, "alpha", horizons=(1,), n_quantiles=2)
    assert 1 in res.ic
    assert 1 in res.quantile_returns
    assert res.coverage.notna().any()


def test_single_factor_job_with_universe_and_preprocess() -> None:
    panel = _panel()
    mask = pd.Series([True, False, True, False, True, False], index=panel.index)
    u = Universe(mask=mask)
    pp = Pipeline([Rank("alpha")])
    res = SingleFactorJob.run(
        panel, "alpha", horizons=(1,), universe=u, preprocess=pp, n_quantiles=2
    )
    assert res.quantile_returns[1].shape[1] <= 2
