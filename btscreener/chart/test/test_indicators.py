import backtrader as bt

from btscreener.chart.priceaction import WickReversalSignal
from btscreener.chart.supertrend import Supertrend
from btscreener.chart.tdcount import TDSequential
from btscreener.chart.adbreakout import ADBreakout

from .fixtures import *

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
    WickReversalSignal, Supertrend, TDSequential, ADBreakout
])
def test_simple(cerebro, indicatorClass):
    cerebro.addstrategy(SimpleStrategy, indicatorClass=indicatorClass)

    # Run over everything
    result = cerebro.run()
    print(result)