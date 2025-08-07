
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

    def _check_format(self):
        if not isinstance(self.factor_data, pd.Series):
            raise ValueError("Factor data must be a pandas Series.")
        if self.factor_data.index.nlevels != 2:
            raise ValueError("Factor data must have a multi-index with (date, ticker).")
        if list(self.factor_data.index.names) != ['date', 'ticker']:
            raise ValueError("Index names must be ['date', 'ticker'].")
        if not all(isinstance(idx, pd.Timestamp) for idx in self.factor_data.index.get_level_values('date')):
            raise ValueError("The first level of the index must be of type pandas Timestamp.")
        if not all(isinstance(idx, str) for idx in self.factor_data.index.get_level_values('ticker')):
            raise ValueError("The second level of the index must be of type str.")

    def __post_init__(self):
        self._check_format()
        self.factor_data.sort_index(inplace=True, level='date')
        self.factor_data.name = self.factor_name

    def dropna(self, how: Literal['any', 'all'] = 'any') -> 'FactorData':
        cleaned = self.factor_data.dropna(how=how)
        return FactorData(cleaned, metadata=self.metadata.copy(), factor_name=self.factor_name)

    def filter_by_universe(self, universe_mask: pd.Series) -> 'FactorData':
        """Filter factor data by a boolean universe mask (same index)."""
        if not isinstance(universe_mask, pd.Series):
            raise ValueError("Universe mask must be a pandas Series.")
        if not universe_mask.index.equals(self.factor_data.index):
            raise ValueError("Universe mask index must match factor data index.")
        filtered = self.factor_data[universe_mask]
        return FactorData(factor_data=filtered, metadata=self.metadata.copy(), factor_name=self.factor_name)

    def is_aligned(self, other: 'FactorData') -> bool:
        """
        Check if the factor data index is aligned with another FactorData object.
        """
        return self.factor_data.index.equals(other.factor_data.index)

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
        return FactorData(factor_data=std, metadata=new_metadata, factor_name=self.factor_name)

    def to_series(self) -> pd.Series:
        return self.factor_data.copy()

    def to_frame(self) -> pd.DataFrame:
        return self.factor_data.to_frame(self.factor_name).copy()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'factor_data': self.factor_data.copy(),
            'metadata': self.metadata.copy(),
            'factor_name': self.factor_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FactorData':
        return cls(
            factor_data=data['factor_data'].copy(),
            metadata=data.get('metadata', {}).copy(),
            factor_name=data.get('factor_name', 'factor')
        )

    def __repr__(self) -> str:
        return f"""
name: {self.factor_name}, 
ticker count: {self.tickers.size}, 
datetime range: {self.start_date} to {self.end_date},
metadata: {self.metadata}
        """

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
    return FactorData(factor_data=factor_series, metadata=(metadata or {}).copy(), factor_name=factor_series.name)
    