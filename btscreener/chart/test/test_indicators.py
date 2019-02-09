
import pytest
import backtrader as bt

from btscreener.sources.iex import load_historical

from btscreener.chart.priceaction import WickReversalSignal
from btscreener.chart.supertrend import Supertrend
from btscreener.chart.tdcount import TDSequential
from btscreener.chart.adbreakout import ADBreakout

@pytest.fixture(scope="module")
def historical_data(request):
    data = load_historical("AAPL", lookback="3m")
    return data.set_index("date")

@pytest.fixture(scope="function")
def cerebro(request, historical_data):
    print(historical_data)
    cerebro = bt.Cerebro()

    # Set up the data source
    data = bt.feeds.PandasDirectData(dataname=historical_data, openinterest=-1)
    cerebro.adddata(data)

    return cerebro


class SimpleStrategy(bt.Strategy):

    def __init__(self, indicatorClass):
        """

        :param indicatorClass: type of indicator to use with the strategy
        """
        self.indicatorClass = indicatorClass
        self.indicator = indicatorClass()

def test_sanity_check(cerebro):
    """ Perform a cerebro run without any indicators to make sure our fixture
    is properly configured
    """
    # Run over everything
    result = cerebro.run()
    print(result)

@pytest.mark.parametrize("indicatorClass", [
    WickReversalSignal, Supertrend, TDSequential,
])
def test_simple(cerebro, indicatorClass):
    cerebro.addstrategy(SimpleStrategy, indicatorClass=indicatorClass)

    # Run over everything
    result = cerebro.run()
    print(result)

# TODO: Test ADBreakout