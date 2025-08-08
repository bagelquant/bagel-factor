import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.bagel_factor.visualization import plots
from matplotlib.figure import Figure

class TestPlots(unittest.TestCase):
    def setUp(self):
        # Create mock IC series
        dates = pd.date_range('2023-01-01', periods=100, freq='B')
        self.ic_series = pd.Series(np.random.randn(100), index=dates)
        # Create mock quantile return DataFrame
        quantiles = [1, 2, 3, 4, 5]
        self.quantile_return_df = pd.DataFrame(
            np.random.randn(100, 5), index=dates, columns=quantiles
        )
        # Create mock spread series
        self.spread_series = pd.Series(np.random.randn(100), index=dates)

    def test_plot_ic_series(self):
        fig = plots.plot_ic_series(self.ic_series)
        self.assertIsInstance(fig, Figure)

    def test_plot_quantile_returns(self):
        fig = plots.plot_quantile_returns(self.quantile_return_df)
        self.assertIsInstance(fig, Figure)

    def test_plot_cumulative_spread(self):
        fig = plots.plot_cumulative_return(self.spread_series, return_type='log')
        self.assertIsInstance(fig, Figure)
        fig2 = plots.plot_cumulative_return(self.spread_series, return_type='normal')
        self.assertIsInstance(fig2, Figure)

if __name__ == '__main__':
    unittest.main()
