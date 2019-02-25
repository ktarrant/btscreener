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
        ("max_entry_td", -1),
    )

    def __init__(self):
        self.breakout = self.p.breakout_src(self.data)
        self.td = TDSequential(self.data)

        self.driver = BreakoutDriver(self)

    def next(self):
        self.driver.next()

    def notify_order(self, order):
        self.driver.notify_order(order)

    @property
    def entry_signal(self):
        breakout = self.breakout.lines.breakout[0]
        td_count = self.td.count[0]
        if self.p.max_entry_td < 0:
            # a negative setting means we don't filter entry at all using TD
            return breakout
        elif self.p.max_entry_td == 0:
            # a setting of zero means we simply require the td count to have the
            # same sign as the breakout
            if td_count > 0 and breakout > 0:
                return breakout
            elif td_count < 0 and breakout < 0:
                return breakout
            else:
                return 0
        else:
            if 0 < td_count <= self.p.max_entry_td and breakout > 0:
                return breakout
            elif 0 > td_count >= -self.p.max_entry_td and breakout < 0:
                return breakout
            else:
                return 0

    @property
    def protect_price(self):
        return self.breakout.lines.stop[0]

    @property
    def close_signal(self):
        return self.td.lines.reversal[0]