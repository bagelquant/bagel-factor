"""
Interface for evaluation

- IC
- ICIR
- Quantile Returns
    - risk metrics
- Quantile spread
    - risk metrics
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Any, Literal
from .data_handling import FactorData
from .metrics import information_coefficient, quantile_returns, quantile_spread
from .metrics import (
    accumulate_return,
    annualized_volatility,
    sharpe_ratio,
    max_drawdown,
    calmar_ratio,
    downside_risk,
    sortino_ratio
)


@dataclass(slots=True)
class Evaluator:
    """
    Evaluator for factor performance and risk metrics.
    Handles IC, ICIR, quantile returns, quantile spread, and associated risk metrics.
    """

    # === Input data ===    
    factor_data: FactorData
    future_returns_for_ic: FactorData
    future_returns_for_quantile: FactorData

    # === Default parameters ===
    factor_name: str = field(default='factor')
    return_type: Literal['log', 'normal'] = field(default='log')
    metadata: dict[str, Any] = field(default_factory=dict)
    periods_per_year: int = field(default=252)
    n_quantiles: int = field(default=10)

    # === Internal attributes ===
    _start_date: pd.Timestamp = field(init=False)
    _end_date: pd.Timestamp = field(init=False)
    _ic_series_pearson: pd.Series = field(init=False)
    _ic_series_spearman: pd.Series = field(init=False)
    _quantile_return_df: pd.DataFrame = field(init=False)
    _quantile_spread_series: pd.Series = field(init=False)
    
    # === Initialization ===
    def __post_init__(self):
        """
        Post-initialization: set date range and check data alignment.
        """
        self._start_date = self.factor_data.start_date
        self._end_date = self.factor_data.end_date
        self._check_data()
    
    def _check_data(self) -> None:
        """
        Validate and align input data for evaluation.
        - Ensures all inputs are FactorData.
        - Ensures future_returns_for_ic and future_returns_for_quantile are aligned.
        - Aligns factor_data to returns index, forward-filling per ticker.
        """
        if not isinstance(self.factor_data, FactorData):
            raise TypeError("factor_data must be an instance of FactorData")
        if not isinstance(self.future_returns_for_ic, FactorData):
            raise TypeError("future_returns_for_ic must be an instance of FactorData")
        if not isinstance(self.future_returns_for_quantile, FactorData):
            raise TypeError("future_returns_for_quantile must be an instance of FactorData")
        if not self.future_returns_for_ic.is_aligned(self.future_returns_for_quantile):
            raise ValueError("future_returns_for_ic and future_returns_for_quantile must be aligned")
        # Forward fill per ticker after aligning to returns index
        reindexed = self.factor_data.factor_data.reindex(self.future_returns_for_ic.factor_data.index)
        reindexed = (
            reindexed
            .sort_index(level=['ticker', 'date'])
            .groupby(level='ticker', group_keys=False)
            .ffill()
        )
        reindexed = reindexed.reorder_levels(['date', 'ticker']).sort_index()
        self.factor_data = FactorData(
            factor_data=reindexed,
            factor_name=self.factor_data.factor_name,
            metadata=self.factor_data.metadata,
        )
    
    # === Setters ===
    def set_start_date(self, start_date: pd.Timestamp) -> None:
        """Set the start date for evaluation."""
        # check if start_date is within the factor_data date range
        if start_date < self.factor_data.start_date:
            return
        if start_date > self._end_date:
            raise ValueError("start_date cannot be after end_date")
        self._start_date = start_date
    
    def set_end_date(self, end_date: pd.Timestamp) -> None:
        """Set the end date for evaluation."""
        # check if end_date is within the factor_data date range
        if end_date > self.factor_data.end_date:
            return
        if end_date < self._start_date:
            raise ValueError("end_date cannot be before start_date")
        self._end_date = end_date

    # === Calculate methods ===
    def _calculate_ic_series(self, method: Literal["pearson", "spearman"]) -> None:
        """Calculate and cache IC series for the given method."""
        ic_series = information_coefficient(
            self.factor_data.factor_data,
            self.future_returns_for_ic.factor_data,
            method=method
        )
        if method == "pearson":
            self._ic_series_pearson = ic_series
        elif method == "spearman":
            self._ic_series_spearman = ic_series

    def _calculate_quantile_return_df(self) -> None:
        """Calculate and cache quantile return DataFrame."""
        self._quantile_return_df = quantile_returns(
            self.factor_data.factor_data,
            self.future_returns_for_quantile.factor_data,
            n_quantiles=self.n_quantiles
        )

    def _calculate_quantile_spread_series(self) -> None:
        """Calculate and cache quantile spread series."""
        if not hasattr(self, "_quantile_return_df"):
            self._calculate_quantile_return_df()
        self._quantile_spread_series = quantile_spread(self._quantile_return_df)
    
    # === Results (IC) ===
    def ic_series(self, method: Literal["pearson", "spearman"] = "pearson") -> pd.Series:
        """
        Get IC series for the specified method.
        If not calculated, computes and caches it.
        """
        attr = f"_ic_series_{method}"
        if not hasattr(self, attr):
            self._calculate_ic_series(method)
        return getattr(self, attr).loc[self._start_date:self._end_date]

    def ic_mean(self, method: Literal["pearson", "spearman"] = "pearson") -> float:
        """Mean of IC series over evaluation period for given method."""
        return self.ic_series(method).mean()

    def ic_std(self, method: Literal["pearson", "spearman"] = "pearson") -> float:
        """Std of IC series over evaluation period for given method."""
        return self.ic_series(method).std()

    def ic_ir(self, method: Literal["pearson", "spearman"] = "pearson") -> float:
        """Information Ratio of IC series (annualized) for given method."""
        return self.ic_series(method).mean() / self.ic_series(method).std() * (self.periods_per_year ** 0.5)

    # === Results (Quantile Returns) properties ===
    def quantile_return_df(self) -> pd.DataFrame:
        """Quantile return DataFrame over evaluation period."""
        if not hasattr(self, "_quantile_return_df"):
            self._calculate_quantile_return_df()
        return self._quantile_return_df.loc[self._start_date:self._end_date]

    def quantile_spread_series(self) -> pd.Series:
        """Quantile spread series over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return self._quantile_spread_series.loc[self._start_date:self._end_date]

    def quantile_spread_cum_return(self) -> pd.Series:
        """Cumulative return of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return accumulate_return(
            returns=self._quantile_spread_series.loc[self._start_date:self._end_date], 
            return_type=self.return_type
        )

    def quantile_spread_annualized_volatility(self) -> float:
        """Annualized volatility of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return annualized_volatility(
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Sharpe ratio of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return sharpe_ratio(
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            risk_free_rate=risk_free_rate,
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_max_drawdown(self) -> float:
        """Max drawdown of quantile spread cumulative return over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return max_drawdown(
            accumulate_return(self._quantile_spread_series.loc[self._start_date:self._end_date]),
            return_type=self.return_type
        )

    def quantile_spread_calmar_ratio(self) -> float:
        """Calmar ratio of quantile spread cumulative return over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return calmar_ratio(
            accumulate_return(self._quantile_spread_series.loc[self._start_date:self._end_date]),
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_downside_risk(self, risk_free_rate: float = 0.0) -> float:
        """Downside risk of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return downside_risk(
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            risk_free_rate=risk_free_rate,
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Sortino ratio of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return sortino_ratio(
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            risk_free_rate=risk_free_rate,
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )
