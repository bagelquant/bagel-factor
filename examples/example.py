"""End-to-end example for bagel-factor (single-factor evaluation).

Run:
  uv run python examples/example.py

This script exists to generate deterministic artifacts for docs:
- input data under ./examples/inputs/
- outputs under ./examples/outputs/
"""

from __future__ import annotations

from pathlib import Path
import random

import pandas as pd

# Allow running this example without installing the package
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bagelfactor.data import ensure_panel_index  # noqa: E402
from bagelfactor.preprocess import Clip, Pipeline, Rank, ZScore  # noqa: E402
from bagelfactor.single_factor import SingleFactorJob  # noqa: E402
from bagelfactor.stats import ols_alpha_tstat, ttest_1samp  # noqa: E402
from bagelfactor.visualization import (  # noqa: E402
    plot_ic_hist,
    plot_ic_time_series,
    plot_long_short_time_series,
    plot_quantile_returns_heatmap,
    plot_quantile_returns_time_series,
    plot_result_summary,
)


def make_synthetic_panel(*, n_assets: int = 20, n_dates: int = 100, seed: int = 0) -> pd.DataFrame:
    """Generate a deterministic synthetic panel.

    - dates: `n_dates` business days
    - assets: `n_assets`
    - `alpha` is constructed to have some predictive power for next-day returns,
      so the IC/quantile plots are non-trivial.
    """

    rng = random.Random(seed)
    dates = pd.date_range("2020-01-01", periods=n_dates, freq="B")
    assets = [f"A{i:02d}" for i in range(n_assets)]

    beta = 0.02
    noise_sd = 0.01

    rows: list[dict[str, object]] = []

    for asset in assets:
        # Generate factor values per date (with some missingness to show coverage plots)
        alpha: list[float | None] = [rng.gauss(0.0, 1.0) for _ in range(n_dates)]
        for i in range(n_dates):
            if rng.random() < 0.05:
                alpha[i] = None

        price = 100.0 + 10.0 * rng.random()
        prices: list[float] = [price]

        # Build returns so that next-day return depends on today's alpha
        for i in range(1, n_dates):
            a_prev = 0.0 if alpha[i - 1] is None else float(alpha[i - 1])
            r = beta * a_prev + rng.gauss(0.0, noise_sd)
            price = price * (1.0 + r)
            prices.append(price)

        for d, a, p in zip(dates, alpha, prices):
            rows.append({"date": d, "asset": asset, "close": float(p), "alpha": a})

    df = pd.DataFrame(rows)
    return ensure_panel_index(df)


def main() -> None:
    example_dir = ROOT / "examples"
    in_dir = example_dir / "inputs"
    out_dir = example_dir / "outputs"
    plots_dir = out_dir / "plots"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    panel = make_synthetic_panel()

    # Persist the input used by the docs
    panel.reset_index().to_csv(in_dir / "panel.csv", index=False)

    # Example pipeline with multiple preprocessing steps:
    # - Clip: reduce outlier impact
    # - ZScore: standardize cross-sectionally per date
    # - Rank: make the signal comparable across dates
    preprocess = Pipeline([
        Clip("alpha", lower=-3.0, upper=3.0),
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

    # ---
    # Plots (saved as PNGs under examples/outputs/plots)
    # ---
    fig = plot_result_summary(res, horizon=1)
    fig.savefig(plots_dir / "summary_h1.png", dpi=150, bbox_inches="tight")

    ax = plot_ic_time_series(res.ic[1], title="IC time series (h=1)")
    ax.figure.savefig(plots_dir / "ic_time_series_h1.png", dpi=150, bbox_inches="tight")

    ax = plot_ic_hist(res.ic[1], title="IC histogram (h=1)")
    ax.figure.savefig(plots_dir / "ic_hist_h1.png", dpi=150, bbox_inches="tight")

    ax = plot_quantile_returns_time_series(
        res.quantile_returns[1], title="Quantile returns (h=1)"
    )
    ax.figure.savefig(plots_dir / "quantile_returns_time_series_h1.png", dpi=150, bbox_inches="tight")

    ax = plot_quantile_returns_heatmap(
        res.quantile_returns[1], title="Quantile returns heatmap (h=1)"
    )
    ax.figure.savefig(plots_dir / "quantile_returns_heatmap_h1.png", dpi=150, bbox_inches="tight")

    ax = plot_long_short_time_series(res.long_short[1], title="Long-short (h=1)")
    ax.figure.savefig(plots_dir / "long_short_h1.png", dpi=150, bbox_inches="tight")

    # Deterministic stdout capture for docs
    print("Wrote inputs to: examples/inputs")
    print("Wrote outputs to: examples/outputs")
    print("Wrote plots to: examples/outputs/plots")
    ic_test = ttest_1samp(res.ic[1], popmean=0.0)
    ls_alpha = ols_alpha_tstat(res.long_short[1])

    print("ICIR(h=1):", res.icir[1])
    print("IC(h=1) head:")
    print(res.ic[1].head())
    print("Quantile returns (h=1) head:")
    print(res.quantile_returns[1].head())
    print("t-test mean(IC)=0:", ic_test)
    print("OLS alpha (long-short):", ls_alpha)


if __name__ == "__main__":
    main()
