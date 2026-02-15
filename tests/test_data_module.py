import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

# Ensure src/ is importable when running tests without installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import (  # noqa: E402
    FactorMatrix,
    FactorSeries,
    Universe,
    add_forward_returns,
    add_returns,
    align_to_calendar,
    ensure_panel_index,
    get_trading_calendar_daily,
    get_trading_calendar_monthly,
    get_trading_calendar_quartly,
    get_trading_calendar_weekly,
    lag_by_asset,
    retrieve_trading_calendar,
    validate_panel,
)
from bagelfactor.data.loaders import (  # noqa: E402
    CSVLoader,
    ExcelLoader,
    JSONLoader,
    LoadConfig,
    ParquetLoader,
    PickleLoader,
    UnsupportedFormatError,
    _add_optional_common_behavior,
    _infer_format,
    get_loader,
    load_df,
)


def _base_panel() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2020-01-01", "2020-01-02"],
            "asset": ["A", "A", "B", "B"],
            "close": [10.0, 11.0, 20.0, 18.0],
            "alpha": [1.0, 2.0, 3.0, 4.0],
        }
    )


# -----------------
# panel / align
# -----------------


def test_ensure_panel_index_from_columns() -> None:
    panel = ensure_panel_index(_base_panel())
    assert isinstance(panel.index, pd.MultiIndex)
    assert panel.index.names == ["date", "asset"]


def test_ensure_panel_index_raises_if_missing_keys() -> None:
    with pytest.raises(KeyError):
        ensure_panel_index(pd.DataFrame({"date": ["2020-01-01"], "close": [1.0]}))


def test_validate_panel_raises_for_wrong_index() -> None:
    with pytest.raises(TypeError):
        validate_panel(pd.DataFrame({"a": [1]}))


def test_add_returns_computes_per_asset() -> None:
    panel = ensure_panel_index(_base_panel())
    out = add_returns(panel, price="close")
    assert out.loc[(pd.Timestamp("2020-01-02"), "A"), "ret_1d"] == pytest.approx(0.1)
    assert out.loc[(pd.Timestamp("2020-01-02"), "B"), "ret_1d"] == pytest.approx(-0.1)


def test_add_forward_returns_h1() -> None:
    panel = ensure_panel_index(_base_panel())
    out = add_forward_returns(panel, price="close", horizons=(1,))
    assert out.loc[(pd.Timestamp("2020-01-01"), "A"), "ret_fwd_1"] == pytest.approx(0.1)
    assert pd.isna(out.loc[(pd.Timestamp("2020-01-02"), "A"), "ret_fwd_1"])


def test_add_forward_returns_rejects_non_positive_horizon() -> None:
    panel = ensure_panel_index(_base_panel())
    with pytest.raises(ValueError):
        add_forward_returns(panel, horizons=(0,))


def test_lag_by_asset_shifts_selected_columns_only() -> None:
    panel = ensure_panel_index(_base_panel())
    out = lag_by_asset(panel, ["alpha"], periods=1)
    assert pd.isna(out.loc[(pd.Timestamp("2020-01-01"), "A"), "alpha"])
    assert out.loc[(pd.Timestamp("2020-01-02"), "A"), "alpha"] == pytest.approx(1.0)
    assert out.loc[(pd.Timestamp("2020-01-01"), "A"), "close"] == 10.0


def test_align_to_calendar_raw_and_ffill() -> None:
    df = pd.DataFrame({"date": ["2020-01-01", "2020-01-03"], "asset": ["A", "A"], "x": [1.0, 3.0]})
    panel = ensure_panel_index(df)
    cal = pd.DatetimeIndex(pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]))

    raw = align_to_calendar(panel, cal, method="raw")
    assert pd.isna(raw.loc[(pd.Timestamp("2020-01-02"), "A"), "x"])

    ff = align_to_calendar(panel, cal, method="ffill")
    assert ff.loc[(pd.Timestamp("2020-01-02"), "A"), "x"] == pytest.approx(1.0)


# -----------------
# factors / universe
# -----------------


def test_factor_series_renames_index_axes() -> None:
    idx = pd.MultiIndex.from_product([pd.to_datetime(["2020-01-01"]), ["A"]], names=["d", "a"])
    fs = FactorSeries(name="x", values=pd.Series([1.0], index=idx))
    assert fs.values.index.names == ["date", "asset"]


def test_factor_matrix_from_columns_and_missing() -> None:
    panel = ensure_panel_index(_base_panel())
    fm = FactorMatrix.from_columns(panel, ["alpha"])
    assert list(fm.values.columns) == ["alpha"]
    with pytest.raises(KeyError):
        FactorMatrix.from_columns(panel, ["nope"])


def test_universe_apply_filters_panel() -> None:
    panel = ensure_panel_index(_base_panel())
    mask = pd.Series([True, False, True, False], index=panel.index, name="in_universe")
    out = Universe(mask=mask).apply(panel)
    assert len(out) == 2
    assert set(out.index.get_level_values("asset")) == {"A"}


# -----------------
# loaders
# -----------------


def test_infer_format_known_suffixes() -> None:
    assert _infer_format("data.csv") == "csv"
    assert _infer_format("data.json") == "json"
    assert _infer_format("data.xlsx") == "xlsx"
    assert _infer_format("data.xls") == "xlsx"
    assert _infer_format("data.parquet") == "parquet"
    assert _infer_format("data.pkl") == "pickle"
    assert _infer_format("data.pickle") == "pickle"


def test_infer_format_unsupported() -> None:
    with pytest.raises(UnsupportedFormatError):
        _infer_format("data.txt")


def test_add_optional_common_behavior_prefers_existing_kwargs() -> None:
    cfg = LoadConfig(
        source="x.csv",
        columns=["a"],
        nrows=10,
        read_kwargs={"columns": ["b"], "nrows": 5},
    )
    kw = _add_optional_common_behavior(cfg)
    assert kw["columns"] == ["b"]
    assert kw["nrows"] == 5


def test_add_optional_common_behavior_sets_when_missing() -> None:
    cfg = LoadConfig(source="x.csv", columns=["a"], nrows=10, read_kwargs={})
    kw = _add_optional_common_behavior(cfg)
    assert kw["columns"] == ["a"]
    assert kw["nrows"] == 10


def test_get_loader_by_explicit_format() -> None:
    assert isinstance(get_loader(LoadConfig(source="x.any", format="csv")), CSVLoader)
    assert isinstance(get_loader(LoadConfig(source="x.any", format="json")), JSONLoader)
    assert isinstance(get_loader(LoadConfig(source="x.any", format="xlsx")), ExcelLoader)
    assert isinstance(get_loader(LoadConfig(source="x.any", format="parquet")), ParquetLoader)
    assert isinstance(get_loader(LoadConfig(source="x.any", format="pickle")), PickleLoader)


def test_get_loader_by_inferred_format() -> None:
    assert isinstance(get_loader(LoadConfig(source="x.csv")), CSVLoader)
    assert isinstance(get_loader(LoadConfig(source="x.parquet")), ParquetLoader)
    assert isinstance(get_loader(LoadConfig(source="x.pkl")), PickleLoader)


def test_get_loader_unsupported() -> None:
    with pytest.raises(UnsupportedFormatError):
        get_loader(LoadConfig(source="x.any", format="nope"))


def test_csv_load_df_applies_postprocess_and_nrows(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("a,b\n1,10\n2,20\n3,30\n", encoding="utf-8")

    cfg = LoadConfig(
        source=path,
        nrows=2,
        postprocess=lambda df: df.assign(c=df["a"] + df["b"]),
    )
    df = load_df(cfg)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b", "c"]
    assert df.loc[0, "c"] == 11


def test_parquet_loader_passes_columns_and_applies_nrows() -> None:
    base = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [10, 20, 30, 40, 50]})
    with patch("bagelfactor.data.loaders.pd.read_parquet", return_value=base) as rp:
        cfg = LoadConfig(source="x.parquet", columns=["a"], nrows=3)
        df = load_df(cfg)

    rp.assert_called_once()
    _, kwargs = rp.call_args
    assert kwargs.get("columns") == ["a"]
    assert len(df) == 3


def test_pickle_loader_dataframe_roundtrip_columns_and_nrows(tmp_path: Path) -> None:
    path = tmp_path / "data.pkl"
    pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]}).to_pickle(path)

    df = load_df(LoadConfig(source=path, columns=["b"], nrows=2))
    assert list(df.columns) == ["b"]
    assert len(df) == 2


def test_pickle_loader_non_dataframe_object(tmp_path: Path) -> None:
    path = tmp_path / "obj.pickle"
    pd.to_pickle([{"a": 1}, {"a": 2}, {"a": 3}], path)

    df = load_df(LoadConfig(source=path, nrows=2))
    assert list(df.columns) == ["a"]
    assert len(df) == 2


def test_json_loader_smoke_via_mock() -> None:
    base = pd.DataFrame({"a": [1, 2]})
    with patch("bagelfactor.data.loaders.pd.read_json", return_value=base) as rj:
        df = load_df(LoadConfig(source="x.json"))
    rj.assert_called_once()
    assert df.equals(base)


def test_excel_loader_smoke_via_mock() -> None:
    base = pd.DataFrame({"a": [1, 2]})
    with patch("bagelfactor.data.loaders.pd.read_excel", return_value=base) as rx:
        df = load_df(LoadConfig(source="x.xlsx"))
    rx.assert_called_once()
    assert df.equals(base)


# -----------------
# calendar
# -----------------


def test_calendar_daily_retrieves_and_caches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("BAGELFACTOR_CALENDAR_DIR", str(tmp_path))
    path = retrieve_trading_calendar(
        market="US", start="2020-01-01", end="2020-01-31", overwrite=True
    )
    assert path.exists()

    idx = get_trading_calendar_daily(market="US", start="2020-01-02", end="2020-01-10")
    assert len(idx) > 0
    assert idx.is_monotonic_increasing


def test_calendar_weekly_start_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BAGELFACTOR_CALENDAR_DIR", str(tmp_path))
    retrieve_trading_calendar(market="US", start="2020-01-01", end="2020-02-15", overwrite=True)

    w_start = get_trading_calendar_weekly(market="US", option="start")
    w_end = get_trading_calendar_weekly(market="US", option="end")
    assert len(w_start) > 0 and len(w_end) > 0
    assert (w_start <= w_end).all()


def test_calendar_monthly_and_quartly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BAGELFACTOR_CALENDAR_DIR", str(tmp_path))
    retrieve_trading_calendar(market="US", start="2020-01-01", end="2020-06-30", overwrite=True)

    m_end = get_trading_calendar_monthly(market="US", option="end")
    q_end = get_trading_calendar_quartly(market="US", option="end")
    assert len(m_end) > 0
    assert len(q_end) > 0
