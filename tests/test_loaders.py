import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

# Ensure src/ is importable when running tests without installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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
