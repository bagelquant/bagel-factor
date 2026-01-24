"""Benchmark script for ic_series and coverage_by_date.

Generates synthetic panels and compares the current vectorized implementations
against groupby.apply baselines.
"""

import time
import numpy as np
import pandas as pd
from bagelfactor.metrics.ic import ic_series
from bagelfactor.metrics.coverage import coverage_by_date


def baseline_ic(panel, factor, label, method="spearman"):
    df = panel[[factor, label]].dropna()

    def _ic(g: pd.DataFrame) -> float:
        if len(g) < 2:
            return float("nan")
        x = g[factor]
        y = g[label]
        if method == "spearman":
            x = x.rank(method="average")
            y = y.rank(method="average")
        return float(x.corr(y, method="pearson"))

    return df.groupby(level="date", sort=False).apply(_ic).rename("ic")


def baseline_coverage(panel, column):
    s = panel[column]

    def _cov(x: pd.Series) -> float:
        return float(x.notna().mean()) if len(x) else float("nan")

    return s.groupby(level="date", sort=False).apply(_cov).rename("coverage")


def make_panel(n_dates, n_assets, na_prob=0.05, seed=0):
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2020-01-01", periods=n_dates, freq="D")
    assets = [f"A{i}" for i in range(n_assets)]
    mi = pd.MultiIndex.from_product([dates, assets], names=["date", "asset"])
    size = n_dates * n_assets
    factor = rng.randn(size)
    label = rng.randn(size)
    mask = rng.rand(size) < na_prob
    factor[mask] = np.nan
    mask2 = rng.rand(size) < na_prob
    label[mask2] = np.nan
    df = pd.DataFrame({"factor": factor, "label": label}, index=mi)
    return df


def time_function(fn, *args, repeats=3):
    times = []
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(*args)
        t1 = time.perf_counter()
        times.append(t1 - t0)
        result = res
    return min(times), np.median(times), result


if __name__ == "__main__":
    sizes = [(200, 100), (500, 200)]  # (n_dates, n_assets)
    for n_dates, n_assets in sizes:
        print(f"\nPanel size: dates={n_dates}, assets={n_assets} (rows={n_dates*n_assets})")
        panel = make_panel(n_dates, n_assets, na_prob=0.05, seed=42)

        # IC benchmark
        print("Benchmarking IC...")
        base_min, base_med, base_res = time_function(baseline_ic, panel, "factor", "label", "spearman", repeats=3)
        vec_min, vec_med, vec_res = time_function(lambda p: ic_series(p, factor="factor", label="label", method="spearman"), panel, repeats=3)

        # align results for comparison
        base_res = base_res.sort_index()
        vec_res = vec_res.sort_index()
        # Compare finite entries
        common_idx = base_res.index.intersection(vec_res.index)
        diffs = (base_res.loc[common_idx].fillna(0) - vec_res.loc[common_idx].fillna(0)).abs()
        max_diff = diffs.max() if len(diffs) else float('nan')

        print(f"IC baseline min/med: {base_min:.4f}s / {base_med:.4f}s")
        print(f"IC vector min/med:   {vec_min:.4f}s / {vec_med:.4f}s")
        print(f"IC max abs diff: {max_diff}")

        # Coverage benchmark
        print("Benchmarking coverage...")
        base_min, base_med, base_res = time_function(baseline_coverage, panel, "factor", repeats=3)
        vec_min, vec_med, vec_res = time_function(lambda p: coverage_by_date(p, column="factor"), panel, repeats=3)

        base_res = base_res.sort_index()
        vec_res = vec_res.sort_index()
        diffs = (base_res - vec_res).abs()
        max_diff = diffs.max() if len(diffs) else float('nan')

        print(f"Coverage baseline min/med: {base_min:.4f}s / {base_med:.4f}s")
        print(f"Coverage vector min/med:   {vec_min:.4f}s / {vec_med:.4f}s")
        print(f"Coverage max abs diff: {max_diff}")
