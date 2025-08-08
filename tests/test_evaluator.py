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
        # Factor values
        factor = pd.Series(rng.standard_normal(len(idx)), index=idx, name='factor')
        self.factor_data = FactorData(factor_data=factor)
        # Simulate price data as geometric random walk per ticker
        ret = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
        # Build prices starting at 100 per ticker (preserve original index order)
        price = (1 + ret).groupby(level='ticker').cumprod() * 100
        price.name = 'price'
        price_data = FactorData(factor_data=price)
        self.evaluator = Evaluator(
            factor_data=self.factor_data,
            price_data=price_data,
            factor_name='test_factor',
            return_type='normal',  # arithmetic returns
            ic_horizon=1,
            rebalance_period=1,
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

    def test_disallow_direct_assignment(self):
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, 'ic_horizon', 2)
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, 'rebalance_period', 2)
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, 'return_type', 'log')
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, '_start_date', pd.Timestamp('2023-01-02'))
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, '_end_date', pd.Timestamp('2023-12-31'))

    def test_setters_update_and_invalidate(self):
        s1 = self.evaluator.ic_series('pearson')
        self.evaluator.set_ic_horizon(5)
        s2 = self.evaluator.ic_series('pearson')
        self.assertIsInstance(s2, pd.Series)
        self.assertFalse(s1.equals(s2))

        q1 = self.evaluator.quantile_return_df()
        self.evaluator.set_rebalance_period(5)
        q2 = self.evaluator.quantile_return_df()
        self.assertIsInstance(q2, pd.DataFrame)
        self.assertGreater(q1.shape[0], q2.shape[0])

        self.evaluator.set_return_type('log')
        s3 = self.evaluator.ic_series('pearson')
        self.assertIsInstance(s3, pd.Series)

class TestEvaluatorUsingRealData(unittest.TestCase):
    def setUp(self):
        # === Set up real data for testing ===
        factor = pd.read_csv(
            'tests/test_data/roe.csv',
            parse_dates=['date'],
            index_col=['date', 'ticker']
        )['roe'].sort_index()
        
        price = pd.read_csv(
            'tests/test_data/price.csv',
            usecols=['date', 'ticker', 'adj_close'],
            parse_dates=['date'],
            index_col=['date', 'ticker']
        )['adj_close'].sort_index()
        # Drop duplicate indices
        price = price[~price.index.duplicated(keep='first')]
        factor = factor[~factor.index.duplicated(keep='first')]
        self.factor_data = FactorData(factor_data=factor)
        price_data = FactorData(factor_data=price)
        self.evaluator = Evaluator(
            factor_data=self.factor_data,
            price_data=price_data,
            factor_name='test_factor',
            return_type='normal',
            ic_horizon=20,
            rebalance_period=20,
        )
        # self.evaluator.set_start_date(pd.Timestamp('2023-06-01'))
        # self.evaluator.set_end_date(pd.Timestamp('2023-12-31'))

    def test_ic_mean(self):
        mean_pearson = self.evaluator.ic_mean('pearson')
        mean_spearman = self.evaluator.ic_mean('spearman')
        self.assertIsInstance(mean_pearson, float)
        self.assertIsInstance(mean_spearman, float)
        print(f"\n=== Test IC Mean ===")
        print(f"Mean Pearson IC: {mean_pearson}, Mean Spearman IC: {mean_spearman}")

    def test_ic_std(self):
        std_pearson = self.evaluator.ic_std('pearson')
        std_spearman = self.evaluator.ic_std('spearman')
        self.assertIsInstance(std_pearson, float)
        self.assertIsInstance(std_spearman, float)
        print(f"\n=== Test IC Std ===")
        print(f"Std Pearson IC: {std_pearson}, Std Spearman IC: {std_spearman}")

    def test_ic_ir(self):
        ir_pearson = self.evaluator.ic_ir('pearson')
        ir_spearman = self.evaluator.ic_ir('spearman')
        self.assertIsInstance(ir_pearson, float)
        self.assertIsInstance(ir_spearman, float)
        print(f"\n=== Test IC IR ===")
        print(f"IR Pearson IC: {ir_pearson}, IR Spearman IC: {ir_spearman}")

    def test_quantile_return_df(self):
        qret = self.evaluator.quantile_return_df()
        self.assertIsInstance(qret, pd.DataFrame)
        self.assertGreater(qret.shape[0], 0)
        print(f"\n=== Test Quantile Return DataFrame ===")
        print(f"Quantile Return DataFrame shape: {qret.shape}")
        print(qret.head())

    def test_quantile_spread_series(self):
        spread = self.evaluator.quantile_spread_series()
        self.assertIsInstance(spread, pd.Series)
        self.assertGreater(spread.shape[0], 0)
        print(f"\n=== Test Quantile Spread Series ===")
        print(f"Quantile Spread Series shape: {spread.shape}")
        print(spread.head())

    def test_quantile_spread_cum_return(self):
        cumret = self.evaluator.quantile_spread_cum_return()
        self.assertIsInstance(cumret, pd.Series)
        self.assertGreater(cumret.shape[0], 0)
        print(f"\n=== Test Quantile Spread Cumulative Return ===")
        print(f"Quantile Spread Cumulative Return shape: {cumret.shape}")
        print(cumret.head())

    def test_quantile_spread_annualized_volatility(self):
        vol = self.evaluator.quantile_spread_annualized_volatility()
        self.assertIsInstance(vol, float)
        print(f"\n=== Test Quantile Spread Annualized Volatility ===")
        print(f"Quantile Spread Annualized Volatility: {vol}")

    def test_quantile_spread_sharpe_ratio(self):
        sharpe = self.evaluator.quantile_spread_sharpe_ratio()
        self.assertIsInstance(sharpe, float)
        print(f"\n=== Test Quantile Spread Sharpe Ratio ===")
        print(f"Quantile Spread Sharpe Ratio: {sharpe}")

    def test_quantile_spread_max_drawdown(self):
        mdd = self.evaluator.quantile_spread_max_drawdown()
        self.assertIsInstance(mdd, float)
        print(f"\n=== Test Quantile Spread Max Drawdown ===")
        print(f"Quantile Spread Max Drawdown: {mdd}")

    def test_quantile_spread_calmar_ratio(self):
        calmar = self.evaluator.quantile_spread_calmar_ratio()
        self.assertIsInstance(calmar, float)
        print(f"\n=== Test Quantile Spread Calmar Ratio ===")
        print(f"Quantile Spread Calmar Ratio: {calmar}")

    def test_quantile_spread_downside_risk(self):
        downside = self.evaluator.quantile_spread_downside_risk()
        self.assertIsInstance(downside, float)
        print(f"\n=== Test Quantile Spread Downside Risk ===")
        print(f"Quantile Spread Downside Risk: {downside}")

    def test_quantile_spread_sortino_ratio(self):
        sortino = self.evaluator.quantile_spread_sortino_ratio()
        self.assertIsInstance(sortino, float)

    def test_direct_assignment_blocked(self):
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, 'ic_horizon', 10)
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, 'rebalance_period', 10)
        with self.assertRaises(AttributeError):
            setattr(self.evaluator, 'return_type', 'log')


if __name__ == '__main__':
    unittest.main()
