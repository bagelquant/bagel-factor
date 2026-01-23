"""End-to-end example for bagel-factor (single-factor evaluation).

Run:
  uv run python examples/example.py

This script exists to generate deterministic artifacts for docs:
- input data under ./examples/inputs/
- outputs under ./examples/outputs/
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Allow running this example without installing the package
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import ensure_panel_index  # noqa: E402
from bagelfactor.preprocess import Clip, Pipeline, Rank, ZScore  # noqa: E402
from bagelfactor.single_factor import SingleFactorJob  # noqa: E402


def make_synthetic_panel() -> pd.DataFrame:
    """Return a tiny canonical panel (3 dates x 2 assets)."""

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


def main() -> None:
    example_dir = ROOT / "examples"
    in_dir = example_dir / "inputs"
    out_dir = example_dir / "outputs"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    panel = make_synthetic_panel()

    # Persist the input used by the docs
    panel.reset_index().to_csv(in_dir / "panel.csv", index=False)

    # Example pipeline with multiple preprocessing steps:
    # - Clip: reduce outlier impact
    # - ZScore: standardize cross-sectionally per date
    # - Rank: make the signal comparable across dates
    preprocess = Pipeline([
        Clip("alpha", lower=0.0, upper=2.0),
        ZScore("alpha"),
        Rank("alpha"),
    ])

    res = SingleFactorJob.run(
        panel,
        factor="alpha",
        horizons=(1,),
        n_quantiles=2,
        preprocess=preprocess,
    )

    # Persist outputs used by the docs
    res.ic[1].to_frame("ic").to_csv(out_dir / "ic_h1.csv", index=True)
    res.quantile_returns[1].to_csv(out_dir / "quantile_returns_h1.csv", index=True)
    res.long_short[1].to_frame("long_short").to_csv(out_dir / "long_short_h1.csv", index=True)
    res.coverage.to_frame("coverage").to_csv(out_dir / "coverage.csv", index=True)

    # Deterministic stdout capture for docs
    print("Wrote inputs to: examples/inputs")
    print("Wrote outputs to: examples/outputs")
    print("ICIR(h=1):", res.icir[1])
    print("IC(h=1):")
    print(res.ic[1])
    print("Quantile returns (h=1):")
    print(res.quantile_returns[1])


if __name__ == "__main__":
    main()
