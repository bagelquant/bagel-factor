"""bagelfactor.data

v0 data layer: loaders + canonical (date, asset) panel primitives.
"""

from .calendar import (
    retrieve_trading_calendar,
    get_trading_calendar_daily,
    get_trading_calendar_weekly,
    get_trading_calendar_monthly,
    get_trading_calendar_quartly,
)

from .align import align_to_calendar, lag_by_asset
from .factors import FactorMatrix, FactorSeries
from .loaders import LoadConfig, load_df
from .panel import add_forward_returns, add_returns, ensure_panel_index, validate_panel
from .universe import Universe

__all__ = [
    "LoadConfig",
    "load_df",
    "ensure_panel_index",
    "validate_panel",
    "add_returns",
    "add_forward_returns",
    "FactorSeries",
    "FactorMatrix",
    "Universe",
    "align_to_calendar",
    "lag_by_asset",
    "retrieve_trading_calendar",
    "get_trading_calendar_daily",
    "get_trading_calendar_weekly",
    "get_trading_calendar_monthly",
    "get_trading_calendar_quartly",
]
