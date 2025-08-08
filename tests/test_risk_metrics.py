import unittest
import numpy as np
import pandas as pd
from typing import cast
from src.bagel_factor.metrics import risk_metrics


class TestRiskMetrics(unittest.TestCase):
    def setUp(self):
        # Simulate daily returns for 2 years (504 trading days)
        np.random.seed(42)
        self.returns_normal = pd.Series(np.random.normal(0.001, 0.01, 504))
        self.returns_log = pd.Series(np.log1p(self.returns_normal), index=self.returns_normal.index)
        self.risk_free_rate = 0.0001
        self.periods_per_year = 252
        # Create DataFrame variants (two columns)
        noise = np.random.normal(0, 0.005, len(self.returns_normal))
        self.df_returns_normal = pd.DataFrame({
            'A': self.returns_normal,
            'B': self.returns_normal * 0.5 + noise
        })
        # Use pandas apply to keep DataFrame type for static checkers
        self.df_returns_log = self.df_returns_normal.apply(np.log1p)

    def test_accumulate_return_normal(self):
        cum = risk_metrics.accumulate_return(self.returns_normal, return_type='normal')
        # First cumulative value equals the first period return for arithmetic returns
        self.assertLess(abs(float(cum.iloc[0]) - float(self.returns_normal.iloc[0])), 1e-6)  # type: ignore
        self.assertEqual(len(cum), len(self.returns_normal))

    def test_accumulate_return_log(self):
        cum = risk_metrics.accumulate_return(self.returns_log, return_type='log')
        self.assertAlmostEqual(cum.iloc[0], np.exp(self.returns_log.iloc[0]), places=6)
        self.assertTrue(np.all(cum > 0))

    def test_accumulate_return_dataframe(self):
        cum_df = risk_metrics.accumulate_return(self.df_returns_normal, return_type='normal')
        self.assertIsInstance(cum_df, pd.DataFrame)
        self.assertEqual(cum_df.shape, self.df_returns_normal.shape)

    def test_annualized_volatility(self):
        vol_log = risk_metrics.annualized_volatility(self.returns_log, self.periods_per_year, 'log')
        vol_normal = risk_metrics.annualized_volatility(self.returns_normal, self.periods_per_year, 'normal')
        self.assertIsInstance(vol_log, float)
        self.assertIsInstance(vol_normal, float)

    def test_annualized_volatility_dataframe(self):
        vol_df_log = risk_metrics.annualized_volatility(self.df_returns_log, self.periods_per_year, 'log')
        vol_df_normal = risk_metrics.annualized_volatility(self.df_returns_normal, self.periods_per_year, 'normal')
        self.assertIsInstance(vol_df_log, pd.Series)
        self.assertIsInstance(vol_df_normal, pd.Series)
        self.assertEqual(len(cast(pd.Series, vol_df_log)), self.df_returns_log.shape[1])
        self.assertEqual(len(cast(pd.Series, vol_df_normal)), self.df_returns_normal.shape[1])

    def test_sharpe_ratio(self):
        sr_log = risk_metrics.sharpe_ratio(self.returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        sr_normal = risk_metrics.sharpe_ratio(self.returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(sr_log, float)
        self.assertIsInstance(sr_normal, float)

    def test_sharpe_ratio_dataframe(self):
        sr_df_log = risk_metrics.sharpe_ratio(self.df_returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        sr_df_normal = risk_metrics.sharpe_ratio(self.df_returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(sr_df_log, pd.Series)
        self.assertIsInstance(sr_df_normal, pd.Series)
        self.assertEqual(len(cast(pd.Series, sr_df_log)), self.df_returns_log.shape[1])
        self.assertEqual(len(cast(pd.Series, sr_df_normal)), self.df_returns_normal.shape[1])

    def test_max_drawdown(self):
        mdd_log = risk_metrics.max_drawdown(self.returns_log, 'log')
        mdd_normal = risk_metrics.max_drawdown(self.returns_normal, 'normal')
        self.assertLessEqual(cast(float, mdd_log), 0)
        self.assertLessEqual(cast(float, mdd_normal), 0)

    def test_max_drawdown_dataframe(self):
        mdd_df_log = risk_metrics.max_drawdown(self.df_returns_log, 'log')
        mdd_df_normal = risk_metrics.max_drawdown(self.df_returns_normal, 'normal')
        self.assertIsInstance(mdd_df_log, pd.Series)
        self.assertIsInstance(mdd_df_normal, pd.Series)
        self.assertTrue((cast(pd.Series, mdd_df_log) <= 0).all())
        self.assertTrue((cast(pd.Series, mdd_df_normal) <= 0).all())

    def test_calmar_ratio(self):
        calmar_log = risk_metrics.calmar_ratio(self.returns_log, self.periods_per_year, 'log')
        calmar_normal = risk_metrics.calmar_ratio(self.returns_normal, self.periods_per_year, 'normal')
        self.assertIsInstance(calmar_log, float)
        self.assertIsInstance(calmar_normal, float)

    def test_calmar_ratio_dataframe(self):
        calmar_df_log = risk_metrics.calmar_ratio(self.df_returns_log, self.periods_per_year, 'log')
        calmar_df_normal = risk_metrics.calmar_ratio(self.df_returns_normal, self.periods_per_year, 'normal')
        self.assertIsInstance(calmar_df_log, pd.Series)
        self.assertIsInstance(calmar_df_normal, pd.Series)
        self.assertEqual(len(cast(pd.Series, calmar_df_log)), self.df_returns_log.shape[1])
        self.assertEqual(len(cast(pd.Series, calmar_df_normal)), self.df_returns_normal.shape[1])

    def test_downside_risk(self):
        dr_log = risk_metrics.downside_risk(self.returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        dr_normal = risk_metrics.downside_risk(self.returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertGreaterEqual(cast(float, dr_log), 0)
        self.assertGreaterEqual(cast(float, dr_normal), 0)

    def test_downside_risk_dataframe(self):
        dr_df_log = risk_metrics.downside_risk(self.df_returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        dr_df_normal = risk_metrics.downside_risk(self.df_returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(dr_df_log, pd.Series)
        self.assertIsInstance(dr_df_normal, pd.Series)
        self.assertTrue((cast(pd.Series, dr_df_log) >= 0).all())
        self.assertTrue((cast(pd.Series, dr_df_normal) >= 0).all())

    def test_sortino_ratio(self):
        sortino_log = risk_metrics.sortino_ratio(self.returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        sortino_normal = risk_metrics.sortino_ratio(self.returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(sortino_log, float)
        self.assertIsInstance(sortino_normal, float)

    def test_sortino_ratio_dataframe(self):
        sortino_df_log = risk_metrics.sortino_ratio(self.df_returns_log, self.risk_free_rate, self.periods_per_year, 'log')
        sortino_df_normal = risk_metrics.sortino_ratio(self.df_returns_normal, self.risk_free_rate, self.periods_per_year, 'normal')
        self.assertIsInstance(sortino_df_log, pd.Series)
        self.assertIsInstance(sortino_df_normal, pd.Series)
        self.assertEqual(len(cast(pd.Series, sortino_df_log)), self.df_returns_log.shape[1])
        self.assertEqual(len(cast(pd.Series, sortino_df_normal)), self.df_returns_normal.shape[1])

    def test_empty_returns(self):
        empty = pd.Series(dtype=float)
        self.assertTrue(np.isnan(risk_metrics.annualized_volatility(empty, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.sharpe_ratio(empty, self.risk_free_rate, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.calmar_ratio(empty, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.downside_risk(empty, self.risk_free_rate, self.periods_per_year, 'log')))
        self.assertTrue(np.isnan(risk_metrics.sortino_ratio(empty, self.risk_free_rate, self.periods_per_year, 'log')))


if __name__ == '__main__':
    unittest.main()
