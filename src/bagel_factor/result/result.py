"""
A dataclass to hold the results of factor return calculations.
"""

from dataclasses import dataclass, field

import pandas as pd
import numpy as np
# t test for factor return
from scipy import stats

from ..evaluation.factor_return import calculate_factor_return_regression, calculate_factor_return_grouping
from ..evaluation.ic import calculate_ic_s


@dataclass(slots=True)
class Result:
    """
    A dataclass to hold the results of factor return calculations.
    
    Attributes
    ----------
    data : pd.DataFrame
        The input data used for calculations.
    target : str
        The target factor name.
    prediction : str
        The prediction column name.
    rebalance_date_index : pd.DatetimeIndex
        The index of rebalance dates.
    group_num : int, optional
        The number of groups for grouping calculations, default is 5.
    """
    
    data: pd.DataFrame
    target: str
    prediction: str
    rebalance_date_index: pd.DatetimeIndex
    description: str = field(default="Factor return results")
    group_num: int = field(default=5)
    rlm_weight: pd.Series = field(default_factory=pd.Series)

    def summary(self, included_fields: list[str]) -> pd.Series:
        """
        Generate a summary of the results.

        Parameters
        ----------
        included_fields : list[str]
            List of fields to include in the summary.

        Returns
        -------
        pd.Series
            A series containing the summary of the results.

        Raises
        ------
        ValueError
            If a field in `included_fields` is not a valid attribute of the class.
        """
        summary = pd.Series(dtype=float)
        for field in included_fields:
            if hasattr(self, field):
                attr = getattr(self, field)
                if isinstance(attr, pd.Series):
                    summary[field] = attr.mean()
                elif isinstance(attr, (int, float, np.number)):
                    summary[field] = float(attr)
                # Skip DataFrame or unsupported types
            else:
                raise ValueError(f"Field '{field}' is not a valid attribute of Result.")
        return summary

    @property
    def spearman_ic(self) -> pd.Series:
        return calculate_ic_s(
            data=self.data,
            target=self.target,
            prediction=self.prediction,
            rebalance_date_index=self.rebalance_date_index,
            method='spearman'
        )
    
    @property
    def pearson_ic(self) -> pd.Series:
        return calculate_ic_s(
            data=self.data,
            target=self.target,
            prediction=self.prediction,
            rebalance_date_index=self.rebalance_date_index,
            method='pearson'
        )
    
    @property
    def spearman_icir(self) -> float:
        """
        Calculate the Information Coefficient (IC) ratio using Spearman method.

        Returns
        -------
        float
            The mean divided by the standard deviation of Spearman IC.

        Raises
        ------
        ZeroDivisionError
            If the standard deviation of Spearman IC is zero.
        """
        std = self.spearman_ic.std()
        if std == 0:
            raise ZeroDivisionError("Standard deviation of Spearman IC is zero.")
        return self.spearman_ic.mean() / std

    @property
    def pearson_icir(self) -> float:
        """
        Calculate the Information Coefficient (IC) ratio using Pearson method.

        Returns
        -------
        float
            The mean divided by the standard deviation of Pearson IC.

        Raises
        ------
        ZeroDivisionError
            If the standard deviation of Pearson IC is zero.
        """
        std = self.pearson_ic.std()
        if std == 0:
            raise ZeroDivisionError("Standard deviation of Pearson IC is zero.")
        return self.pearson_ic.mean() / std
    
    @property
    def factor_return_grouping(self) -> pd.DataFrame:
        return calculate_factor_return_grouping(
            data=self.data,
            target=self.target,
            prediction=self.prediction,
            rebalance_date_index=self.rebalance_date_index,
            group_num=self.group_num
        )
    
    @property
    def factor_return_grouping_hml(self) -> pd.Series:
        return self.factor_return_grouping['HML']
    
    @property
    def factor_return_grouping_t_test(self) -> tuple[np.float64, np.float64]:
        """
        Perform a t-test on the HML (High Minus Low) factor returns from grouping.

        Returns
        -------
        tuple[np.float64, np.float64]
            The t-statistic and p-value of the t-test.

        Raises
        ------
        ValueError
            If 'HML' column is missing in factor_return_grouping.
        """
        if 'HML' not in self.factor_return_grouping:
            raise ValueError("'HML' column is missing in factor_return_grouping.")
        return stats.ttest_1samp(self.factor_return_grouping['HML'], 0)
    
    @property
    def factor_return_ols(self) -> pd.Series:
        return calculate_factor_return_regression(
            data=self.data,
            target=self.target,
            prediction=self.prediction,
            rebalance_date_index=self.rebalance_date_index
        )
    
    @property
    def factor_return_ols_t_test(self) -> tuple[np.float64, np.float64]:
        return stats.ttest_1samp(self.factor_return_ols, 0)

    @property
    def factor_return_ols_t_stat(self) -> float:
        return self.factor_return_ols_t_test[0]

    @property
    def factor_return_ols_p_value(self) -> float:
        return self.factor_return_ols_t_test[1]

    @property
    def factor_return_wls(self) -> pd.Series:
        return calculate_factor_return_regression(
            data=self.data,
            target=self.target,
            prediction=self.prediction,
            rebalance_date_index=self.rebalance_date_index,
            method='WLS',
            weights=self.rlm_weight
        )

    @property
    def factor_return_wls_t_test(self) -> tuple[np.float64, np.float64]:
        return stats.ttest_1samp(self.factor_return_wls, 0)

    @property
    def factor_return_rlm(self) -> pd.Series:
        """
        Calculate factor returns using Robust Linear Model (RLM).

        Returns
        -------
        pd.Series
            The factor returns calculated using RLM method.
        """
        return calculate_factor_return_regression(
            data=self.data,
            target=self.target,
            prediction=self.prediction,
            rebalance_date_index=self.rebalance_date_index,
            method='RLM',
        )

    @property
    def factor_return_rlm_t_test(self) -> tuple[np.float64, np.float64]:
        return stats.ttest_1samp(self.factor_return_rlm, 0)

    @property
    def factor_return_rlm_t_stat(self) -> float:
        return self.factor_return_rlm_t_test[0]

    @property
    def factor_return_rlm_p_value(self) -> float:
        return self.factor_return_rlm_t_test[1]
