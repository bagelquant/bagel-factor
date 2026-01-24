"""bagelfactor.stats

Statistical tests and regressions used in factor research.

This module depends on SciPy and statsmodels.
"""

from .regression import OLSResult, ols_alpha_tstat, ols_summary
from .tests import TTestResult, ttest_1samp, ttest_ind

__all__ = [
    "TTestResult",
    "ttest_1samp",
    "ttest_ind",
    "OLSResult",
    "ols_alpha_tstat",
    "ols_summary",
]
