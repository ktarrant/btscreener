import backtrader as bt

def run_backtest(table, cerebro=None):
    '''
    Runs strategy against historical data

    Args:
        table (pd.DataFrame): table of OHLC data to backtest
        cerebro (bt.Cerebro): cerebro object to configure, or None for default

    Returns:
        pd.Series: technical stats for symbol
    '''

    if not cerebro:
        cerebro = bt.Cerebro()

    # Add an indicator that we can extract afterwards
    # cerebro.addstrategy(SummaryStrategy)

    # Set up the data source
    data = bt.feeds.PandasDirectData(dataname=table, openinterest=-1)
    cerebro.adddata(data)

    # Run over everything
    result = cerebro.run()

    return result[0].get_summary()