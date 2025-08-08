
"""
FactorData class definition for managing factor data.

This module provides a robust container for factor values, with validation, cleaning, and utility methods.
Standard format: pandas Series with MultiIndex (date, ticker), sorted by date.
Optionally supports metadata for extensibility.
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Literal
from .preprocessing import PreprocessingMethod


@dataclass(slots=True)
class FactorData:
    """
    Container for factor values (Series with MultiIndex), with validation, cleaning, and metadata.
    
    Attributes:
        factor_data: pd.Series with MultiIndex (date, ticker)
        metadata: Optional dictionary for additional context
        factor_name: Optional name for the factor (used in DataFrame column)
    """
    factor_data: pd.Series
    metadata: Dict[str, Any] = field(default_factory=dict)
    factor_name: Optional[str] = 'factor'  # Optional name for the factor
    # Performance-related flags
    validate: bool = True  # when False, skip expensive validation
    enforce_sorted: bool = True  # when True, ensure sorted by date

    def _check_format(self):
        """Lightweight schema checks to avoid O(N) scans on large data."""
        if not isinstance(self.factor_data, pd.Series):
            raise ValueError("Factor data must be a pandas Series.")
        idx = self.factor_data.index
        if idx.nlevels != 2:
            raise ValueError("Factor data must have a multi-index with (date, ticker).")
        if list(idx.names) != ['date', 'ticker']:
            raise ValueError("Index names must be ['date', 'ticker'].")
        # Prefer dtype inference over element-wise checks for performance
        date_level = idx.get_level_values('date')
        ticker_level = idx.get_level_values('ticker')
        # Check datetime dtype quickly
        if not pd.api.types.is_datetime64_any_dtype(date_level.dtype):
            # Fallback sample check for small data
            if len(date_level) <= 1000 and not all(isinstance(d, pd.Timestamp) for d in date_level):
                raise ValueError("The first level of the index must be of type pandas Timestamp.")
        # Check ticker dtype (object/str acceptable). Avoid O(N) scan on large data
        inferred = ticker_level.inferred_type
        if inferred not in {"string", "unicode", "mixed", "mixed-integer", "object"}:
            if len(ticker_level) <= 1000 and not all(isinstance(t, str) for t in ticker_level):
                raise ValueError("The second level of the index must be of type str.")

    def __post_init__(self):
        if self.validate:
            self._check_format()
        # Avoid sorting if already monotonic by date level
        if self.enforce_sorted:
            try:
                # Only sort if clearly not sorted by 'date'
                if not self.factor_data.index.is_monotonic_increasing:
                    self.factor_data.sort_index(inplace=True, level='date')
            except Exception:
                # Fallback to safer path
                self.factor_data.sort_index(inplace=True, level='date')
        # Set name without triggering a copy
        self.factor_data.name = self.factor_name

    def dropna(self, how: Literal['any', 'all'] = 'any') -> 'FactorData':
        cleaned = self.factor_data.dropna(how=how)
        return FactorData(
            cleaned,
            metadata=self.metadata.copy(),
            factor_name=self.factor_name,
            validate=self.validate,
            enforce_sorted=False,  # dropna preserves order
        )

    def filter_by_universe(self, universe_mask: pd.Series) -> 'FactorData':
        """Filter factor data by a boolean universe mask (same index)."""
        if not isinstance(universe_mask, pd.Series):
            raise ValueError("Universe mask must be a pandas Series.")
        if not universe_mask.index.equals(self.factor_data.index):
            raise ValueError("Universe mask index must match factor data index.")
        filtered = self.factor_data[universe_mask]
        return FactorData(
            factor_data=filtered,
            metadata=self.metadata.copy(),
            factor_name=self.factor_name,
            validate=self.validate,
            enforce_sorted=False,
        )

    def is_aligned(self, other: 'FactorData') -> bool:
        """
        Check if indices are equal or one is a subset of the other (same (date, ticker) schema).
        """
        idx_a = self.factor_data.index
        idx_b = other.factor_data.index
        # Quick equal check
        if idx_a.equals(idx_b):
            return True
        # Subset checks without converting to Python lists
        try:
            return idx_b.difference(idx_a).empty or idx_a.difference(idx_b).empty
        except Exception:
            # Fallback to isin if difference not available
            return bool(idx_b.isin(idx_a).all() or idx_a.isin(idx_b).all())

    def standardize(self, method: PreprocessingMethod) -> 'FactorData':
        """
        Standardize factor values using a preprocessing method (callable).
        The method should accept and return a Series with the same index.
        In metadata, add PreprocessingMethod function name for reference.
        """
        if not callable(method):
            raise ValueError("method must be callable.")
        std = method(self.factor_data)
        if not isinstance(std, pd.Series) or not std.index.equals(self.factor_data.index):
            raise ValueError("PreprocessingMethod must return a Series with the same index as the input.")
        new_metadata = self.metadata.copy()
        new_metadata['preprocessing_method'] = getattr(method, '__name__', str(method))
        return FactorData(
            factor_data=std,
            metadata=new_metadata,
            factor_name=self.factor_name,
            validate=self.validate,
            enforce_sorted=False,  # preprocessing preserves grouping order
        )

    def to_series(self, copy: bool = True) -> pd.Series:
        return self.factor_data.copy() if copy else self.factor_data

    def to_frame(self, copy: bool = True) -> pd.DataFrame:
        df = self.factor_data.to_frame(self.factor_name)
        return df.copy() if copy else df

    def to_dict(self, copy: bool = True) -> Dict[str, Any]:
        return {
            'factor_data': self.factor_data.copy() if copy else self.factor_data,
            'metadata': self.metadata.copy() if copy else self.metadata,
            'factor_name': self.factor_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FactorData':
        return cls(
            factor_data=data['factor_data'].copy(),
            metadata=data.get('metadata', {}).copy(),
            factor_name=data.get('factor_name', 'factor')
        )

    def __repr__(self) -> str:
        # Lightweight repr to avoid heavy computations on large data
        try:
            n = int(self.factor_data.size)
        except Exception:
            n = -1
        return f"FactorData(name={self.factor_name}, size={n})"

    def __str__(self) -> str:
        return self.__repr__()
    
    # Properties
    @property
    def start_date(self) -> pd.Timestamp:
        return self.factor_data.index.get_level_values('date').min()

    @property
    def end_date(self) -> pd.Timestamp:
        return self.factor_data.index.get_level_values('date').max()
    
    @property
    def shape(self) -> tuple:
        return self.factor_data.shape
    
    @property
    def tickers(self) -> pd.Index:
        return self.factor_data.index.get_level_values('ticker').unique()

    # Fast-path constructor when caller guarantees schema/sort
    @classmethod
    def unsafe_from_series(
        cls,
        series: pd.Series,
        *,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'FactorData':
        series.name = name or (series.name or 'factor')
        # Ensure factor_name is a str for type safety
        factor_name: str = str(series.name)
        return cls(
            factor_data=series,
            metadata=(metadata or {}),
            factor_name=factor_name,
            validate=False,
            enforce_sorted=False,
        )


def create_factor_data_from_df(
    factor_df: pd.DataFrame,
    metadata: Optional[Dict[str, Any]] = None,
    factor_name: Optional[str] = None
) -> FactorData:
    """
    Convert a DataFrame with index (date) and columns (ticker) into a FactorData instance.
    Ensures output is a FactorData with correct index and name.
    """
    if not isinstance(factor_df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    if factor_df.index.nlevels != 1 or not isinstance(factor_df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a single-level DatetimeIndex.")
    if factor_df.empty:
        raise ValueError("Factor DataFrame cannot be empty.")

    factor_series: pd.Series = factor_df.stack()  # type: ignore
    factor_series.index.names = ['date', 'ticker']
    if factor_name:
        factor_series.name = factor_name
    else:
        factor_series.name = 'factor'
    return FactorData(
        factor_data=factor_series,
        metadata=(metadata or {}).copy(),
        factor_name=factor_series.name,
        validate=True,
        enforce_sorted=True,
    )
    