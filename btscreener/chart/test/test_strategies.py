import pytest

from .fixtures import *

from btscreener.chart.strategies.stadtd import BreakoutStrategy

@pytest.mark.parametrize("max_entry_td", [-1, 0, 4])
def test_breakout(cerebro, max_entry_td):
    cerebro.addstrategy(BreakoutStrategy, max_entry_td=max_entry_td)

    # Run over everything
    result = cerebro.run()

    if pytest.config.getoption("--plot", False):
        cerebro.plot()