import pytest

from .fixtures import *

from btscreener.chart.strategies.stadtd import BreakoutStrategy

def test_breakout(cerebro):
    cerebro.addstrategy(BreakoutStrategy)

    # Run over everything
    result = cerebro.run()

    if pytest.config.getoption("--plot", False):
        cerebro.plot()