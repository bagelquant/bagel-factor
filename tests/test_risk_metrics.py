import unittest
import numpy as np
import pandas as pd
from src.bagel_factor.metrics import risk_metrics

class TestRiskMetrics(unittest.TestCase):
    def setUp(self):
        # Simulate daily returns for 2 years (504 trading days)
        np.random.seed(42)
        self.returns_normal = pd.Series(np.random.normal(0.001, 0.01, 504))
        self.returns_log = pd.Series(np.log1p(self.returns_normal), index=self.returns_normal.index)
        self.risk_free_rate = 0.0001
        self.periods_per_year = 252

    def test_accumulate_return_normal(self):
        cum = risk_metrics.accumulate_return(self.returns_normal, return_type='normal')
        self.assertAlmostEqual(cum.iloc[0], 1 + self.returns_normal.iloc[0], places=6)
        self.assertTrue(np.all(cum > 0))

    def test_accumulate_return_log(self):
        cum = risk_metrics.accumulate_return(self.returns_log, return_type='log')
        self.assertAlmostEqual(cum.iloc[0], np.exp(self.returns_log.iloc[0]), places=6)
        self.assertTrue(np.all(cum > 0))

    def test_annualized_volatility(self):
        vol_log = risk_metrics.annualized_volatility(self.returns_log, self.periods_per_year, 'log')
        vol_normal = risk_metrics.annualized_volatility(self.returns_normal, self.periods_per_year, 'normal')
        self.assertGreater(vol_log, 0)
        self.assertGreater(vol_normal, 0)

    def test_sharpe_ratio(self):
        sr_log = risk_metrics.sharpe_ratio(self.returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        sr_normal = risk_metrics.sharpe_ratio(self.returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(sr_log, float)
        self.assertIsInstance(sr_normal, float)

    def test_max_drawdown(self):
        mdd_log = risk_metrics.max_drawdown(self.returns_log, 'log')
        mdd_normal = risk_metrics.max_drawdown(self.returns_normal, 'normal')
        self.assertLessEqual(mdd_log, 0)
        self.assertLessEqual(mdd_normal, 0)

    def test_calmar_ratio(self):
        calmar_log = risk_metrics.calmar_ratio(self.returns_log, self.periods_per_year, 'log')
        calmar_normal = risk_metrics.calmar_ratio(self.returns_normal, self.periods_per_year, 'normal')
        self.assertIsInstance(calmar_log, float)
        self.assertIsInstance(calmar_normal, float)

    def test_downside_risk(self):
        dr_log = risk_metrics.downside_risk(self.returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        dr_normal = risk_metrics.downside_risk(self.returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertGreaterEqual(dr_log, 0)
        self.assertGreaterEqual(dr_normal, 0)

    def test_sortino_ratio(self):
        sortino_log = risk_metrics.sortino_ratio(self.returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        sortino_normal = risk_metrics.sortino_ratio(self.returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(sortino_log, float)
        self.assertIsInstance(sortino_normal, float)

    def test_empty_returns(self):
        empty = pd.Series(dtype=float)
        self.assertTrue(np.isnan(risk_metrics.annualized_volatility(empty, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.sharpe_ratio(empty, self.risk_free_rate, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.calmar_ratio(empty, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.downside_risk(empty, self.risk_free_rate, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.sortino_ratio(empty, self.risk_free_rate, self.periods_per_year, 'log')))

if __name__ == '__main__':
    unittest.main()
