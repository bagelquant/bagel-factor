"""
Preprocessing - Missing Data

Missing data imputation methods for financial data.
"""

import pandas as pd
from typing import Callable

# Define type for imputation methods
ImputeMethod = Callable[[pd.DataFrame | pd.Series], pd.DataFrame | pd.Series]

def fill_mean(x: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Fill missing values with the mean."""
    return x.fillna(x.mean())

def fill_median(x: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Fill missing values with the median."""
    return x.fillna(x.median())

def fill_zero(x: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Fill missing values with zero."""
    return x.fillna(0)

def impute_missing(
    data: pd.DataFrame,
    data_fields: list[str] | str,
    method: ImputeMethod = fill_mean,
    cross_section: bool = True,
    suffix: str | None = None
) -> pd.DataFrame:
    """
    Impute missing values in the specified fields using the given method.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be imputed.
    data_fields : list[str] | str
        The fields to impute. Can be a single field or a list of fields.
    method : ImputeMethod, optional
        The imputation method to use, by default fill_mean.
    cross_section : bool, optional
        If True, impute across the date index for each ticker.
        If False, impute across the ticker index for each date.
        Defaults to True.
    suffix : str | None, optional
        Suffix to append to the imputed field names, by default None.

    Returns
    -------
    pd.DataFrame
        DataFrame with imputed fields.
    """
    if isinstance(data_fields, str):
        data_fields = [data_fields]
    out_fields = [f"{field}_{suffix}" if suffix else field for field in data_fields]
    result = data.copy()
    if cross_section:
        # Impute across tickers for each date
        for field, out_field in zip(data_fields, out_fields):
            result[out_field] = result.groupby('date')[field].transform(method)
    else:
        # Impute across dates for each ticker
        for field, out_field in zip(data_fields, out_fields):
            result[out_field] = result.groupby('ticker')[field].transform(method)
    return result
