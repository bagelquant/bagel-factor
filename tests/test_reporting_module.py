import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.reporting import to_csv, to_parquet  # noqa: E402


def test_to_csv_and_parquet(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    p1 = to_csv(df, tmp_path / "x.csv")
    assert p1.exists()

    # parquet engine is optional
    try:
        p2 = to_parquet(df, tmp_path / "x.parquet")
    except ImportError:
        return
    assert p2.exists()
