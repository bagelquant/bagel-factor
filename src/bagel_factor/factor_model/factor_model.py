"""
Factor Model

Author: Yanzhong(Eric) Huang
Using cross-section (Fama-MacBeth) approach to evaluate factor models.
"""

import pandas as pd
import statsmodels.api as sm
from dataclasses import dataclass, field
from scipy import stats


@dataclass
class FactorModel:
    """
    Factor Model Evaluation

    This class represents a factor model that can be used to evaluate the performance of factors
    using cross-sectional regression (Fama-MacBeth approach).
    
    input:
    - dict of factor loadings (str: pd.DataFrame) (factor name: factor loadings)
    - Stock next returns (pd.DataFrame)
    - Risk-free rate (float, optional, default is 0.0)

    DataFrames should have the following structure:
    - index: Date
    - columns: Tickers
    - index frequency same as the rebalance frequency
    """

    factor_loadings: dict[str, pd.DataFrame]
    stock_next_returns: pd.DataFrame
    rf: float = 0.0
    regression_params: pd.DataFrame = field(init=False)
    t_test_table: pd.DataFrame = field(init=False)
    
    def __post_init__(self):
        # regression_params will have the same index as factor_returns and columns as const + factor_loadings keys 
        self.regression_params = pd.DataFrame(index=self.stock_next_returns.index, columns=['const'] + list(self.factor_loadings.keys()))
        # t_test_table index will be const + factor_loadings keys and columns: factor_return, std, t-stat, p-value
        self.t_test_table = pd.DataFrame(index=['const'] + list(self.factor_loadings.keys()), columns=['factor_return', 'std', 't-stat', 'p-value'])

        self._loop_regression()  # Perform evaluation on initialization
        self._t_test()  # Perform t-test on regression parameters

    def _loop_regression(self) -> None:
        """
        Evaluate the factor model using cross-sectional regression for each date in factor_returns.
        The results are stored in regression_params DataFrame.
        """
        for date in self.stock_next_returns.index:
            result = self._cross_sectional_regression(date)
            self.regression_params.loc[date, 'const'] = result.params['const']
            for factor in self.factor_loadings.keys():
                self.regression_params.loc[date, factor] = result.params[factor]
        
        # change type of regression_params to float
        self.regression_params = self.regression_params.astype(float)
        
    def _t_test(self) -> None:
        """
        Perform t-test on the regression parameter
        """
        self.t_test_table['factor_return'] = self.regression_params.mean()
        self.t_test_table['std'] = self.regression_params.std()
        # perform t-test for each factor
        for factor in self.regression_params.columns:
            # calculate t-statistic and p-value
            t_stat, p_value = stats.ttest_1samp(self.regression_params.loc[:, factor], 0)
            self.t_test_table.loc[factor, 't-stat'] = t_stat  # type: ignore
            self.t_test_table.loc[factor, 'p-value'] = p_value  # type: ignore


    def _cross_sectional_regression(self,
                                    date: pd.Timestamp):
        """
        Perform cross-sectional regression for a given date.

        :param date: The date for which to perform the regression.
        :returns: Regression result (statsmodels RegressionResultsWrapper)
        """
        # Prepare data for regression
        factor_loadings_date: dict[str, pd.Series] = {factor: loadings.loc[date, :] for factor, loadings in self.factor_loadings.items()}  # type: ignore
        X = pd.DataFrame(factor_loadings_date)
        y = self.stock_next_returns.loc[date]
        X = sm.add_constant(X)
        # Run OLS regression
        model = sm.OLS(y, X, missing='drop')
        return model.fit()
    
