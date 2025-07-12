"""
Preprocessing - Standardize

Standardization methods for financial data.
"""

import pandas as pd
from typing import Callable

# Define type for standardization methods
StandardizeMethod = Callable[[pd.DataFrame | pd.Series], pd.DataFrame | pd.Series]

def z_score(x: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return (x - x.mean()) / x.std(ddof=1)


def min_max(x: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return (x - x.min()) / (x.max() - x.min())


def robust(x: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return (x - x.median()) / (x.quantile(0.75) - x.quantile(0.25))


def standardize(
    data: pd.DataFrame,
    data_fields: list[str] | str,
    method: StandardizeMethod = z_score,
    cross_section: bool = True,
    suffix: str | None = None
) -> pd.DataFrame:
    """
    Standardize the specified fields in the DataFrame using the given method.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be standardized.
    data_fields : list[str] | str
        The fields to standardize. Can be a single field or a list of fields.
    method : StandardizeMethod, optional
        The standardization method to use, by default z_score.
    cross_section : bool, optional
        If True, standardize across the date index for each ticker.
        If False, standardize across the ticker index for each date.
        Defaults to True.
    suffix : str | None, optional
        Suffix to append to the standardized field names, by default None.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized fields.
    """
    if isinstance(data_fields, str):
        data_fields = [data_fields]
    out_fields = [f"{field}_{suffix}" if suffix else field for field in data_fields]
    result = data.copy()
    if cross_section:
        # Standardize across tickers for each date
        for field, out_field in zip(data_fields, out_fields):
            result[out_field] = result.groupby('date')[field].transform(method)
    else:
        # Standardize across dates for each ticker
        for field, out_field in zip(data_fields, out_fields):
            result[out_field] = result.groupby('ticker')[field].transform(method)
    return result
