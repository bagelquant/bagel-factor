"""
Factors

input data:
- factor_data: DataFrame with factor values for each stock at each timestamp.
- stock_next_returns: DataFrame with the next period returns for each stock at each timestamp.

both data should be prepared before using the factor classes, it should be the factor rebalancing period data.

Example:

    if you want to calculate a 6 month momentum factor, you should prepare: 
        - factor_data(momentum values at time t)
        - stock_next_returns(returns from t to t+6 months)
    Both DataFrames should have same index (timestamps) and columns (tickers).

Base class Factor is an abstract class that defines the interface for all factors, the `compute` method must be implemented by subclasses to calculate the `self.factor_returns: pd.Series`.

Calculation methods(subclasses of Factor):

    - FactorSort: using the sort method, high minus low portfolio returns as factor returns.
    - RegressionFactor: using factor data as factor loadinsings in a cross-sectional regression, each timestamp factor returns are the slope coefficients of the regression.
"""


import pandas as pd
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class Factor(ABC):
    """
    Abstract base class for factors.
    """

    factor_data: pd.DataFrame
    stock_next_returns: pd.DataFrame

    name: str = field(default="Unnamed Factor")
    description: str = field(default="No description provided")
    
    factor_next_returns: pd.Series = field(init=False)

    def __post_init__(self):
        self.compute()
    
    @abstractmethod
    def compute(self) -> None:
        """
        Compute the factor returns.
        """
        pass

    def __str__(self):
        return f"{self.name}: {self.description}"



@dataclass
class FactorSort(Factor):
    """
    Factor using the sort method to calculate the factor returns.
    """

    group_number: int = field(default=10)

    # Attributes that user could access for further analysis
    portfolio_next_returns: pd.DataFrame = field(init=False)  # columns are group numbers, index is timestamps
    group_labels: pd.DataFrame = field(init=False)  # labels for each stock at each timestamp

    def compute(self) -> None:
        """
        Compute the factor value using the sort method.

        1. Ranks the factor data each timestamp
        2. Assigns stocks to groups based on their ranks, and calculates the portfolio returns(average) for each group.
        3. The factor returns are the high group number minus low group number portfolio returns.
        """
        # Rank the factor data
        ranked_data = self.factor_data.rank(axis=1, method='first', ascending=True)

        # Assign stocks to groups based on their ranks
        # add 1 to group_labels to make it start from 1 instead of 0
        group_labels = pd.qcut(ranked_data.stack(), self.group_number, labels=False) + 1  # type: ignore[assignment]

        # Reshape group_labels to match the original factor_data shape
        group_labels = group_labels.unstack()  # type: ignore
        self.group_labels = group_labels

        # Calculate portfolio returns for each group
        portfolio_next_returns = pd.DataFrame(index=self.factor_data.index, columns=range(1, self.group_number + 1), dtype=float)
        for group in range(1, self.group_number + 1):
            mask = group_labels == group
            # For each timestamp, calculate the mean return of stocks in the group
            portfolio_next_returns[group] = (self.stock_next_returns.where(mask)).mean(axis=1)

        self.portfolio_next_returns = portfolio_next_returns
        # Factor returns: high group minus low group
        self.factor_next_returns = portfolio_next_returns[self.group_number] - portfolio_next_returns[1]
