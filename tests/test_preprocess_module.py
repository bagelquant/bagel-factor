import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import ensure_panel_index  # noqa: E402
from bagelfactor.preprocess import Clip, DropNa, Pipeline, Rank, ZScore  # noqa: E402


def _panel() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-02"],
            "asset": ["A", "B", "A", "B"],
            "x": [1.0, None, 3.0, 4.0],
        }
    )
    return ensure_panel_index(df)


def test_pipeline_applies_steps_in_order() -> None:
    panel = _panel()
    p = Pipeline([DropNa("x"), Clip("x", upper=3.0), Rank("x")])
    out = p.transform(panel)
    assert out.loc[(pd.Timestamp("2020-01-02"), "B"), "x"] == pytest.approx(1.0)


def test_zscore_cross_sectional() -> None:
    panel = ensure_panel_index(
        pd.DataFrame(
            {
                "date": ["2020-01-01", "2020-01-01"],
                "asset": ["A", "B"],
                "x": [0.0, 2.0],
            }
        )
    )
    out = ZScore("x").transform(panel)
    assert out.loc[(pd.Timestamp("2020-01-01"), "A"), "x"] == pytest.approx(-1.0)
    assert out.loc[(pd.Timestamp("2020-01-01"), "B"), "x"] == pytest.approx(1.0)
