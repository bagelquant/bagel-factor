"""
Interface for evaluation

- IC
- ICIR
- Quantile Returns
    - risk metrics
- Quantile spread
    - risk metrics

Change (v2.0.1):
Users now provide price data, and Evaluator computes future returns internally.
Two horizons are supported:
 - ic_horizon: horizon (in index periods) for IC future returns
 - rebalance_period: horizon (in index periods) and sampling step for quantile tests
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Literal, Optional
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
    price_data: FactorData

    # === Default parameters ===
    factor_name: str = field(default='factor')
    return_type: Literal['log', 'normal'] = field(default='log')
    metadata: dict[str, Any] = field(default_factory=dict)
    periods_per_year: int = field(default=252)
    n_quantiles: int = field(default=10)
    # Horizons
    ic_horizon: int = field(default=1)
    rebalance_period: int = field(default=1)

    # === Internal attributes ===
    _start_date: pd.Timestamp = field(init=False)
    _end_date: pd.Timestamp = field(init=False)
    _ic_series_pearson: pd.Series = field(init=False)
    _ic_series_spearman: pd.Series = field(init=False)
    _quantile_return_df: pd.DataFrame = field(init=False)
    _quantile_spread_series: pd.Series = field(init=False)
    # Internally computed data
    _future_returns_ic: Optional[FactorData] = field(init=False, default=None)
    _future_returns_quantile: Optional[FactorData] = field(init=False, default=None)
    _factor_data_for_quantile: Optional[FactorData] = field(init=False, default=None)
    _ic_horizon_cached: Optional[int] = field(init=False, default=None)
    _rebal_period_cached: Optional[int] = field(init=False, default=None)
    _inited: bool = field(init=False, default=False, repr=False)
    
    # === Initialization ===
    def __post_init__(self):
        """
        Post-initialization: set date range and check data alignment.
        """
        # Basic data preparation only (no heavy computations)
        self._prepare_data()
        self._start_date = self.factor_data.start_date
        self._end_date = self.factor_data.end_date
        # Mark object as initialized; further protected assignments must use setters
        object.__setattr__(self, '_inited', True)

    # Enforce setters for protected fields after initialization
    def __setattr__(self, name, value):
        if name in {'_inited'}:
            object.__setattr__(self, name, value)
            return
        if getattr(self, '_inited', False):
            protected = {'ic_horizon', 'rebalance_period', 'return_type', '_start_date', '_end_date'}
            if name in protected:
                raise AttributeError(
                    f"Direct assignment to '{name}' is not allowed after initialization. "
                    f"Use the corresponding setter method."
                )
        object.__setattr__(self, name, value)
    
    def _prepare_data(self) -> None:
        """
        Validate inputs and align factor to price index by forward-filling per ticker.
        Heavy computations (future returns, quantile sampling) are deferred until needed.
        """
        if not isinstance(self.factor_data, FactorData):
            raise TypeError("factor_data must be an instance of FactorData")
        if not isinstance(self.price_data, FactorData):
            raise TypeError("price_data must be an instance of FactorData")
        if self.ic_horizon <= 0:
            raise ValueError("ic_horizon must be a positive integer")
        if self.rebalance_period <= 0:
            raise ValueError("rebalance_period must be a positive integer")

        # Align factor data to price index; forward-fill within ticker
        price_idx = self.price_data.factor_data.index
        if not self.factor_data.factor_data.index.equals(price_idx):
            aligned_factor = self.factor_data.factor_data.reindex(price_idx)
            aligned_factor = aligned_factor.groupby(level='ticker', sort=False).ffill()
            self.factor_data = FactorData(
                factor_data=aligned_factor,
                factor_name=self.factor_data.factor_name,
                metadata=self.factor_data.metadata,
                validate=False,
                enforce_sorted=False,
            )
        # Invalidate caches since alignment may have changed
        self._invalidate_ic_cache()
        self._invalidate_quantile_cache()

    def _future_return_from_price(self, price: pd.Series, periods: int) -> pd.Series:
        """Compute future returns from price for each (date, ticker) assigned to current date.
        If return_type == 'normal', use arithmetic returns; else use log returns.
        """
        # price_fwd is price at t+periods for each ticker
        price_fwd = price.groupby(level='ticker', sort=False).shift(-periods)
        if self.return_type == 'normal':
            with np.errstate(divide='ignore', invalid='ignore'):
                fut_ret = price_fwd / price - 1.0
        else:
            with np.errstate(divide='ignore', invalid='ignore'):
                fut_ret = np.log(price_fwd.astype(float)) - np.log(price.astype(float))
        # Ensure pandas Series type and name
        fut_ret = pd.Series(fut_ret, index=price.index, name='future_return')
        return fut_ret
    
    # === Setters ===
    def _invalidate_ic_cache(self) -> None:
        object.__setattr__(self, '_future_returns_ic', None)
        object.__setattr__(self, '_ic_horizon_cached', None)

    def _invalidate_quantile_cache(self) -> None:
        object.__setattr__(self, '_future_returns_quantile', None)
        object.__setattr__(self, '_factor_data_for_quantile', None)
        object.__setattr__(self, '_rebal_period_cached', None)

    def set_ic_horizon(self, horizon: int) -> None:
        if horizon <= 0:
            raise ValueError("ic_horizon must be a positive integer")
        object.__setattr__(self, 'ic_horizon', horizon)
        self._invalidate_ic_cache()

    def set_rebalance_period(self, period: int) -> None:
        if period <= 0:
            raise ValueError("rebalance_period must be a positive integer")
        object.__setattr__(self, 'rebalance_period', period)
        self._invalidate_quantile_cache()

    def set_return_type(self, return_type: Literal['log', 'normal']) -> None:
        if return_type not in ('log', 'normal'):
            raise ValueError("return_type must be 'log' or 'normal'")
        if self.return_type != return_type:
            object.__setattr__(self, 'return_type', return_type)
            # Return type impacts computed future returns; invalidate all
            self._invalidate_ic_cache()
            self._invalidate_quantile_cache()

    def set_start_date(self, start_date: pd.Timestamp) -> None:
        """Set the start date for evaluation."""
        # check if start_date is within the factor_data date range
        if start_date < self.factor_data.start_date:
            return
        if start_date > self._end_date:
            raise ValueError("start_date cannot be after end_date")
        object.__setattr__(self, '_start_date', start_date)
    
    def set_end_date(self, end_date: pd.Timestamp) -> None:
        """Set the end date for evaluation."""
        # check if end_date is within the factor_data date range
        if end_date > self.factor_data.end_date:
            return
        if end_date < self._start_date:
            raise ValueError("end_date cannot be before start_date")
        object.__setattr__(self, '_end_date', end_date)

    # === Calculate methods ===
    def _ensure_ic_inputs(self) -> None:
        """Compute and cache IC future returns if needed based on current horizon and data."""
        if self._future_returns_ic is not None and self._ic_horizon_cached == self.ic_horizon:
            return
        price_series = self.price_data.factor_data
        fut = self._future_return_from_price(price_series, self.ic_horizon)
        self._future_returns_ic = FactorData.unsafe_from_series(fut, name='future_return_ic')
        self._ic_horizon_cached = self.ic_horizon

    def _ensure_quantile_inputs(self) -> None:
        """Compute and cache quantile factor snapshot and future returns per rebalance period."""
        if (self._future_returns_quantile is not None and
            self._factor_data_for_quantile is not None and
            self._rebal_period_cached == self.rebalance_period):
            return
        price_series = self.price_data.factor_data
        future_q = self._future_return_from_price(price_series, self.rebalance_period)
        # Build rebalanced factor and aligned returns for quantile calculations
        date_index = self.factor_data.factor_data.index.get_level_values('date')
        unique_dates = date_index.unique()
        rebal_dates = unique_dates[:: self.rebalance_period]
        factor_rebal = self.factor_data.factor_data.loc[(rebal_dates, slice(None))]
        future_q_rebal = future_q.loc[(rebal_dates, slice(None))]
        self._factor_data_for_quantile = FactorData.unsafe_from_series(
            factor_rebal.rename(self.factor_data.factor_name),
            name=self.factor_data.factor_name
        )
        self._future_returns_quantile = FactorData.unsafe_from_series(
            future_q_rebal.rename('future_return_quantile'),
            name='future_return_quantile'
        )
        self._rebal_period_cached = self.rebalance_period

    def _calculate_ic_series(self, method: Literal["pearson", "spearman"]) -> None:
        """Calculate and cache IC series for the given method."""
        self._ensure_ic_inputs()
        ic_series = information_coefficient(
            self.factor_data.factor_data,
            self._future_returns_ic.factor_data,  # type: ignore[union-attr]
            method=method
        )
        if method == "pearson":
            self._ic_series_pearson = ic_series
        elif method == "spearman":
            self._ic_series_spearman = ic_series

    def _calculate_quantile_return_df(self) -> None:
        """Calculate and cache quantile return DataFrame."""
        self._ensure_quantile_inputs()
        self._quantile_return_df = quantile_returns(
            self._factor_data_for_quantile.factor_data,  # type: ignore[union-attr]
            self._future_returns_quantile.factor_data,   # type: ignore[union-attr]
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
        return accumulate_return(  # type: ignore
            returns=self._quantile_spread_series.loc[self._start_date:self._end_date],
            return_type=self.return_type
        )

    def quantile_spread_annualized_volatility(self) -> float:
        """Annualized volatility of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return annualized_volatility(  # type: ignore
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Sharpe ratio of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return sharpe_ratio(  # type: ignore
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            risk_free_rate=risk_free_rate,
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_max_drawdown(self) -> float:
        """Max drawdown of quantile spread cumulative return over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return max_drawdown(  # type: ignore
            accumulate_return(self._quantile_spread_series.loc[self._start_date:self._end_date]),
            return_type=self.return_type
        )

    def quantile_spread_calmar_ratio(self) -> float:
        """Calmar ratio of quantile spread cumulative return over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return calmar_ratio(  # type: ignore
            accumulate_return(self._quantile_spread_series.loc[self._start_date:self._end_date]),
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_downside_risk(self, risk_free_rate: float = 0.0) -> float:
        """Downside risk of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return downside_risk(  # type: ignore
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            risk_free_rate=risk_free_rate,
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )

    def quantile_spread_sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Sortino ratio of quantile spread over evaluation period."""
        if not hasattr(self, "_quantile_spread_series"):
            self._calculate_quantile_spread_series()
        return sortino_ratio(  # type: ignore
            self._quantile_spread_series.loc[self._start_date:self._end_date],
            risk_free_rate=risk_free_rate,
            periods_per_year=self.periods_per_year,
            return_type=self.return_type
        )
