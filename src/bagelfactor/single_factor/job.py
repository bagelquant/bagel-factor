from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from bagelfactor.data.panel import add_forward_returns, ensure_panel_index, validate_panel
from bagelfactor.data.universe import Universe
from bagelfactor.metrics.coverage import coverage_by_date
from bagelfactor.metrics.ic import ic_series, icir
from bagelfactor.metrics.quantiles import assign_quantiles, quantile_returns
from bagelfactor.metrics.turnover import quantile_turnover
from bagelfactor.preprocess.pipeline import Pipeline

from .result import SingleFactorResult


@dataclass(frozen=True, slots=True)
class SingleFactorJob:
    """Single-factor evaluation entrypoint."""

    @staticmethod
    def run(
        panel: pd.DataFrame,
        factor: str,
        *,
        price: str = "close",
        horizons: tuple[int, ...] = (1, 5, 20),
        universe: Universe | None = None,
        preprocess: Pipeline | None = None,
        n_quantiles: int = 5,
        ic_method: str = "spearman",
    ) -> SingleFactorResult:
        panel = (
            ensure_panel_index(panel, source="index")
            if isinstance(panel.index, pd.MultiIndex)
            else ensure_panel_index(panel)
        )
        validate_panel(panel)

        if universe is not None:
            panel = universe.apply(panel)

        if preprocess is not None:
            panel = preprocess.transform(panel)

        panel = add_forward_returns(panel, price=price, horizons=horizons)

        cov = coverage_by_date(panel, column=factor)

        ics: dict[int, pd.Series] = {}
        icirs: dict[int, float] = {}
        qrets: dict[int, pd.DataFrame] = {}
        ls: dict[int, pd.Series] = {}
        to: dict[int, pd.Series] = {}

        q = assign_quantiles(panel, factor=factor, n_quantiles=n_quantiles)

        for h in horizons:
            y = f"ret_fwd_{h}"
            ic_h = ic_series(panel, factor=factor, label=y, method=ic_method)
            ics[h] = ic_h
            icirs[h] = icir(ic_h)

            qr = quantile_returns(panel, quantile=q, label=y)
            qrets[h] = qr

            if 1 in qr.columns and n_quantiles in qr.columns:
                ls[h] = (qr[n_quantiles] - qr[1]).rename("long_short")
            else:
                ls[h] = pd.Series(dtype="float64", name="long_short")

            to[h] = quantile_turnover(q, n_quantiles=n_quantiles)

        return SingleFactorResult(
            factor=factor,
            horizons=horizons,
            ic=ics,
            icir=icirs,
            quantile_returns=qrets,
            long_short=ls,
            turnover=to,
            coverage=cov,
        )
