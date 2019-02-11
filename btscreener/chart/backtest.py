from collections import OrderedDict

import pandas as pd
import backtrader as bt

def run_backtest(table, basket):
    '''
    Runs strategy against historical data

    Args:
        table (pd.DataFrame): table of historical data to backtest
        basket (.basket.Basket): basket strategy to use in backtest

    Returns:
        pd.Series: the result of Basket.yield_summary
    '''

    cerebro = bt.Cerebro()

    # Add an indicator that we can extract afterwards
    cerebro.addstrategy(basket)

    # Set up the data source
    data = bt.feeds.PandasData(dataname=table.set_index("date"))
    cerebro.adddata(data)

    # Run over everything
    result = cerebro.run()

    result_strategy = result[0]
    return pd.Series(OrderedDict(result_strategy.yield_summary()))