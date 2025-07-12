"""
Preprocessing - Outlier Handling

Outlier detection and handling methods for financial data.
"""

import pandas as pd
from typing import Callable

# Define type for outlier handling methods
OutlierMethod = Callable[[pd.DataFrame | pd.Series], pd.DataFrame | pd.Series]

def clip_zscore(x: pd.DataFrame | pd.Series, threshold: float = 3.0) -> pd.DataFrame | pd.Series:
    """Clip values to within a specified number of standard deviations from the mean."""
    if isinstance(x, pd.Series):
        mean = x.mean()
        std = x.std(ddof=1)
        lower = mean - threshold * std
        upper = mean + threshold * std
        return x.clip(lower=lower, upper=upper)
    elif isinstance(x, pd.DataFrame):
        def clip_col(col):
            mean = col.mean()
            std = col.std(ddof=1)
            lower = mean - threshold * std
            upper = mean + threshold * std
            return col.clip(lower=lower, upper=upper)
        return x.apply(clip_col)
    else:
        return x

def clip_iqr(x: pd.DataFrame | pd.Series, threshold: float = 1.5) -> pd.DataFrame | pd.Series:
    """Clip values to within a specified IQR range from the median."""
    if isinstance(x, pd.Series):
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return x.clip(lower=lower, upper=upper)
    elif isinstance(x, pd.DataFrame):
        def clip_col(col):
            q1 = col.quantile(0.25)
            q3 = col.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            return col.clip(lower=lower, upper=upper)
        return x.apply(clip_col)
    else:
        return x

def handle_outliers(
    data: pd.DataFrame,
    data_fields: list[str] | str,
    method: OutlierMethod = clip_zscore,
    cross_section: bool = True,
    suffix: str | None = None,
    **method_kwargs
) -> pd.DataFrame:
    """
    Handle outliers in the specified fields using the given method.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be processed.
    data_fields : list[str] | str
        The fields to process. Can be a single field or a list of fields.
    method : OutlierMethod, optional
        The outlier handling method to use, by default clip_zscore.
    cross_section : bool, optional
        If True, process across the date index for each ticker.
        If False, process across the ticker index for each date.
        Defaults to True.
    suffix : str | None, optional
        Suffix to append to the processed field names, by default None.
    **method_kwargs
        Additional keyword arguments to pass to the method.

    Returns
    -------
    pd.DataFrame
        DataFrame with processed fields.
    """
    if isinstance(data_fields, str):
        data_fields = [data_fields]
    out_fields = [f"{field}_{suffix}" if suffix else field for field in data_fields]
    result = data.copy()
    if cross_section:
        # Handle outliers across tickers for each date
        for field, out_field in zip(data_fields, out_fields):
            result[out_field] = result.groupby('date')[field].transform(lambda x: method(x, **method_kwargs))
    else:
        # Handle outliers across dates for each ticker
        for field, out_field in zip(data_fields, out_fields):
            result[out_field] = result.groupby('ticker')[field].transform(lambda x: method(x, **method_kwargs))
    return result
