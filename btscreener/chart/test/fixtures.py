import pytest
import backtrader as bt

from btscreener.sources.iex import load_historical

@pytest.fixture(scope="module")
def historical_data(request):
    data = load_historical("AAPL", lookback="3m")
    return data

@pytest.fixture(scope="function")
def cerebro(request, historical_data):
    cerebro = bt.Cerebro()

    # Set up the data source
    data = bt.feeds.PandasData(dataname=historical_data.set_index("date"))
    cerebro.adddata(data)

    return cerebro
