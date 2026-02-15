"""bagelfactor.utils

Optional utility functions for data validation and diagnostics.
"""

from __future__ import annotations

__all__ = ["PanelDiagnostics", "diagnose_panel"]

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class PanelDiagnostics:
    """Diagnostic information about a panel's structure and quality."""

    is_valid_index: bool
    is_sorted: bool
    has_duplicates: bool
    n_dates: int
    n_assets: int
    n_rows: int
    date_range: tuple[pd.Timestamp | None, pd.Timestamp | None]
    avg_assets_per_date: float
    missing_data_pct: dict[str, float]
    warnings: list[str]

    def __str__(self) -> str:
        """Human-readable diagnostic report."""
        lines = ["Panel Diagnostics", "=" * 40]

        # Index structure
        status = "✓" if self.is_valid_index else "✗"
        lines.append(f"{status} Index structure: {'OK' if self.is_valid_index else 'INVALID'}")

        # Sorting
        status = "✓" if self.is_sorted else "✗"
        msg = "OK" if self.is_sorted else "NO - Call panel.sort_index()"
        lines.append(f"{status} Sorted: {msg}")

        # Duplicates
        status = "✓" if not self.has_duplicates else "✗"
        msg = "None found" if not self.has_duplicates else "DUPLICATES FOUND"
        lines.append(f"{status} Duplicates: {msg}")

        # Size
        lines.append(
            f"  Shape: {self.n_rows:,} rows ({self.n_dates} dates × {self.n_assets} assets)"
        )
        lines.append(f"  Date range: {self.date_range[0]} to {self.date_range[1]}")
        lines.append(f"  Avg assets/date: {self.avg_assets_per_date:.1f}")

        # Missing data
        if self.missing_data_pct:
            lines.append("\n  Missing data by column:")
            for col, pct in sorted(self.missing_data_pct.items()):
                status = "⚠" if pct > 0.1 else " "
                lines.append(f"  {status} {col}: {pct * 100:.1f}%")

        # Warnings
        if self.warnings:
            lines.append("\n⚠ Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        return "\n".join(lines)


def diagnose_panel(panel: pd.DataFrame) -> PanelDiagnostics:
    """Diagnose a panel for common data quality issues.

    This is an optional validation utility. The package does not enforce
    these checks by default, but they can help identify common mistakes.

    Parameters
    ----------
    panel : pd.DataFrame
        Panel to diagnose

    Returns
    -------
    PanelDiagnostics
        Diagnostic information including structure, sorting, duplicates, and data quality

    Examples
    --------
    >>> from bagelfactor import ensure_panel_index
    >>> from bagelfactor.utils import diagnose_panel
    >>> df = pd.DataFrame({
    ...     'date': ['2020-01-02', '2020-01-01'],  # Unsorted!
    ...     'asset': ['A', 'A'],
    ...     'close': [10.0, 11.0]
    ... })
    >>> panel = ensure_panel_index(df)
    >>> diag = diagnose_panel(panel)
    >>> print(diag)
    Panel Diagnostics
    ================
    ✓ Index structure: OK
    ✗ Sorted: NO - Call panel.sort_index()
    ...
    """

    warnings: list[str] = []

    # Check index structure
    is_valid_index = (
        isinstance(panel.index, pd.MultiIndex)
        and len(panel.index.names) == 2
        and panel.index.names == ["date", "asset"]
    )

    if not is_valid_index:
        warnings.append("Index must be MultiIndex with names ['date', 'asset']")

    # Check sorting
    is_sorted = panel.index.is_monotonic_increasing

    if not is_sorted:
        warnings.append("Panel is not sorted - call panel.sort_index()")

    # Check duplicates
    has_duplicates = panel.index.duplicated().any()

    if has_duplicates:
        n_dups = panel.index.duplicated().sum()
        warnings.append(f"Found {n_dups} duplicate (date, asset) pairs")

    # Size metrics
    n_rows = len(panel)
    n_dates = 0
    n_assets = 0
    date_range = (None, None)
    avg_assets_per_date = 0.0

    if is_valid_index and n_rows > 0:
        dates = panel.index.get_level_values("date")
        assets = panel.index.get_level_values("asset")

        n_dates = dates.nunique()
        n_assets = assets.nunique()

        if n_dates > 0:
            date_range = (dates.min(), dates.max())
            avg_assets_per_date = n_rows / n_dates

    # Missing data analysis
    missing_data_pct: dict[str, float] = {}
    for col in panel.columns:
        if pd.api.types.is_numeric_dtype(panel[col]):
            pct_missing = panel[col].isna().sum() / len(panel) if len(panel) > 0 else 0.0
            missing_data_pct[col] = pct_missing

            if pct_missing > 0.5:
                warnings.append(f"Column '{col}' is >50% NaN ({pct_missing * 100:.1f}%)")

    # Check for suspicious patterns
    if is_valid_index and n_dates > 1:
        # Check date frequency
        dates_unique = pd.Series(panel.index.get_level_values("date").unique()).sort_values()
        if len(dates_unique) > 1:
            diffs = dates_unique.diff().dropna()
            if len(diffs) > 0:
                median_diff = diffs.median()
                # Rough heuristic: if most gaps are ~1 day, it's daily data
                if pd.Timedelta(days=0.8) < median_diff < pd.Timedelta(days=1.5):
                    # Check for large gaps
                    large_gaps = diffs[diffs > pd.Timedelta(days=7)]
                    if len(large_gaps) > 0:
                        warnings.append(
                            f"Found {len(large_gaps)} gaps >7 days in what appears to be daily data"
                        )

    return PanelDiagnostics(
        is_valid_index=is_valid_index,
        is_sorted=is_sorted,
        has_duplicates=has_duplicates,
        n_dates=n_dates,
        n_assets=n_assets,
        n_rows=n_rows,
        date_range=date_range,
        avg_assets_per_date=avg_assets_per_date,
        missing_data_pct=missing_data_pct,
        warnings=warnings,
    )
