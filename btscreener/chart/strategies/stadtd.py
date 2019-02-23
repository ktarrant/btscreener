import backtrader as bt

from btscreener.chart.adbreakout import ADBreakout
from btscreener.chart.tdcount import TDSequential
from btscreener.chart.strategies.driver import BreakoutDriver

class BreakoutStrategy(bt.Strategy):
    """
    Strategy which seeks to jump on a breakout away from a support/resistance
    level. The goal of the strategy is to jump on a strong move and then take
    profit when the move is extended.

    The default implementation uses the default ADBreakout indicator (which is
    the Super-Trend variety) for establishing breakout and stop and the TD count
    indicator for establishing take-profit scenarios
    """

    params = (
        ("breakout_src", ADBreakout),
        ("take_src", TDSequential),
    )

    def __init__(self):
        self.breakout = self.p.breakout_src(self.data)
        self.take = self.p.take_src(self.data)

        self.driver = BreakoutDriver(self)

    def next(self):
        self.driver.next()

    def notify_order(self, order):
        self.driver.notify_order(order)

    @property
    def entry_signal(self):
        return self.breakout.lines.breakout

    @property
    def protect_price(self):
        return self.breakout.lines.stop

    @property
    def close_signal(self):
        return self.take.lines.reversal