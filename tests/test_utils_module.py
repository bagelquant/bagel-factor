import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import ensure_panel_index  # noqa: E402
from bagelfactor.utils import diagnose_panel  # noqa: E402


def test_diagnose_panel_valid() -> None:
    """Test diagnose_panel on a valid, well-formed panel."""
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-02"],
            "asset": ["A", "B", "A", "B"],
            "close": [10.0, 20.0, 11.0, 21.0],
            "factor": [1.0, 2.0, 1.5, 2.5],
        }
    )
    panel = ensure_panel_index(df)
    panel = panel.sort_index()

    diag = diagnose_panel(panel)

    assert diag.is_valid_index
    assert diag.is_sorted
    assert not diag.has_duplicates
    assert diag.n_dates == 2
    assert diag.n_assets == 2
    assert diag.n_rows == 4
    assert len(diag.warnings) == 0


def test_diagnose_panel_unsorted() -> None:
    """Test diagnose_panel detects unsorted data."""
    df = pd.DataFrame(
        {
            "date": ["2020-01-02", "2020-01-01"],  # Unsorted!
            "asset": ["A", "A"],
            "close": [11.0, 10.0],
        }
    )
    panel = ensure_panel_index(df, sort=False)  # Don't auto-sort

    diag = diagnose_panel(panel)

    assert diag.is_valid_index
    assert not diag.is_sorted
    assert any("not sorted" in w.lower() for w in diag.warnings)


def test_diagnose_panel_duplicates() -> None:
    """Test diagnose_panel detects duplicate indices."""
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01"],  # Same date, same asset
            "asset": ["A", "A"],
            "close": [10.0, 11.0],
        }
    )
    panel = ensure_panel_index(df)

    diag = diagnose_panel(panel)

    assert diag.is_valid_index
    assert diag.has_duplicates
    assert any("duplicate" in w.lower() for w in diag.warnings)


def test_diagnose_panel_high_missing_data() -> None:
    """Test diagnose_panel detects columns with high missing data."""
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-02"],
            "asset": ["A", "B", "A", "B"],
            "close": [10.0, 20.0, 11.0, 21.0],
            "sparse_factor": [1.0, None, None, None],  # 75% missing
        }
    )
    panel = ensure_panel_index(df)
    panel = panel.sort_index()

    diag = diagnose_panel(panel)

    assert diag.missing_data_pct["sparse_factor"] > 0.5
    assert any(">50%" in w for w in diag.warnings)


def test_diagnose_panel_invalid_index() -> None:
    """Test diagnose_panel handles invalid panel structure."""
    # Panel with wrong index names
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02"],
            "asset": ["A", "A"],
            "close": [10.0, 11.0],
        }
    )
    # Don't convert to panel format
    invalid_panel = df.set_index(["date", "asset"])
    invalid_panel.index.names = ["wrong", "names"]

    diag = diagnose_panel(invalid_panel)

    assert not diag.is_valid_index
    assert any("index must be" in w.lower() for w in diag.warnings)


def test_diagnose_panel_empty() -> None:
    """Test diagnose_panel handles empty panels."""
    panel = pd.DataFrame(
        index=pd.MultiIndex.from_tuples([], names=["date", "asset"]), columns=["close"]
    )

    diag = diagnose_panel(panel)

    assert diag.is_valid_index
    assert diag.n_rows == 0
    assert diag.n_dates == 0
    assert diag.n_assets == 0


def test_diagnose_panel_str_output() -> None:
    """Test that PanelDiagnostics.__str__ produces readable output."""
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01"],
            "asset": ["A", "B"],
            "close": [10.0, 20.0],
        }
    )
    panel = ensure_panel_index(df)
    panel = panel.sort_index()

    diag = diagnose_panel(panel)
    output = str(diag)

    # Check that output contains expected sections
    assert "Panel Diagnostics" in output
    assert "Index structure" in output
    assert "Sorted" in output
    assert "Duplicates" in output


def test_diagnose_panel_date_range() -> None:
    """Test that date range is computed correctly."""
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-01", "2020-12-31", "2020-12-31"],
            "asset": ["A", "B", "A", "B"],
            "close": [10.0, 20.0, 15.0, 25.0],
        }
    )
    panel = ensure_panel_index(df)
    panel = panel.sort_index()

    diag = diagnose_panel(panel)

    assert diag.date_range[0] == pd.Timestamp("2020-01-01")
    assert diag.date_range[1] == pd.Timestamp("2020-12-31")
