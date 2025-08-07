import unittest
import pandas as pd
import numpy as np
from src.bagel_factor.evaluator import Evaluator
from src.bagel_factor.data_handling.factor_data import FactorData

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        # Create more complex mock data: 500 dates, 100 stocks
        dates = pd.date_range('2023-01-02', periods=500, freq='B')
        tickers = [f'STK{i:03d}' for i in range(100)]
        idx = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        rng = np.random.default_rng(42)
        factor = pd.Series(rng.standard_normal(len(idx)), index=idx, name='factor')
        future_returns_ic = pd.Series(rng.standard_normal(len(idx)), index=idx, name='returns_ic')
        future_returns_quantile = pd.Series(rng.standard_normal(len(idx)), index=idx, name='returns_quantile')
        self.factor_data = FactorData(factor_data=factor)
        self.future_returns_for_ic = FactorData(factor_data=future_returns_ic)
        self.future_returns_for_quantile = FactorData(factor_data=future_returns_quantile)
        self.evaluator = Evaluator(
            factor_data=self.factor_data,
            future_returns_for_ic=self.future_returns_for_ic,
            future_returns_for_quantile=self.future_returns_for_quantile,
            factor_name='test_factor',
            return_type='normal'  # Assuming future returns are arithmetic returns
        )
        self.evaluator.set_start_date(pd.Timestamp('2023-06-01'))
        self.evaluator.set_end_date(pd.Timestamp('2023-12-31'))

    def test_ic_mean(self):
        mean_pearson = self.evaluator.ic_mean('pearson')
        mean_spearman = self.evaluator.ic_mean('spearman')
        self.assertIsInstance(mean_pearson, float)
        self.assertIsInstance(mean_spearman, float)

    def test_ic_std(self):
        std_pearson = self.evaluator.ic_std('pearson')
        std_spearman = self.evaluator.ic_std('spearman')
        self.assertIsInstance(std_pearson, float)
        self.assertIsInstance(std_spearman, float)

    def test_ic_ir(self):
        ir_pearson = self.evaluator.ic_ir('pearson')
        ir_spearman = self.evaluator.ic_ir('spearman')
        self.assertIsInstance(ir_pearson, float)
        self.assertIsInstance(ir_spearman, float)

    def test_quantile_return_df(self):
        qret = self.evaluator.quantile_return_df()
        self.assertIsInstance(qret, pd.DataFrame)
        self.assertGreater(qret.shape[0], 0)

    def test_quantile_spread_series(self):
        spread = self.evaluator.quantile_spread_series()
        self.assertIsInstance(spread, pd.Series)
        self.assertGreater(spread.shape[0], 0)

    def test_quantile_spread_cum_return(self):
        cumret = self.evaluator.quantile_spread_cum_return()
        self.assertIsInstance(cumret, pd.Series)
        self.assertGreater(cumret.shape[0], 0)

    def test_quantile_spread_annualized_volatility(self):
        vol = self.evaluator.quantile_spread_annualized_volatility()
        self.assertIsInstance(vol, float)

    def test_quantile_spread_sharpe_ratio(self):
        sharpe = self.evaluator.quantile_spread_sharpe_ratio()
        self.assertIsInstance(sharpe, float)

    def test_quantile_spread_max_drawdown(self):
        mdd = self.evaluator.quantile_spread_max_drawdown()
        self.assertIsInstance(mdd, float)

    def test_quantile_spread_calmar_ratio(self):
        calmar = self.evaluator.quantile_spread_calmar_ratio()
        self.assertIsInstance(calmar, float)

    def test_quantile_spread_downside_risk(self):
        downside = self.evaluator.quantile_spread_downside_risk()
        self.assertIsInstance(downside, float)

    def test_quantile_spread_sortino_ratio(self):
        sortino = self.evaluator.quantile_spread_sortino_ratio()
        self.assertIsInstance(sortino, float)

if __name__ == '__main__':
    unittest.main()
