import backtrader as bt

from btscreener.chart.adbreakout import ADBreakout
from btscreener.chart.tdcount import TDSequential

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

        self.entry_signal = self.breakout.lines.breakout
        self.stop_price = self.breakout.lines.stop
        self.exit_signal = self.take.lines.reversal

        self.entry_order = None
        self.stop_order = None
        self.exit_order = None

    def next(self):
        if self.exit_order:
            # TODO: Update stop price AND exit price
            pass

        elif self.stop_order:
            if ((self.stop_order.status == self.stop_order.Accepted) and
                (self.stop_order.plimit != self.stop_price[0])):
                self.cancel(self.stop_order)

        elif self.entry_order:
            # TODO: Cancel entry if conditions change.
            pass

        else:
            if self.position.size == 0:
                self.send_entry_order()

    def notify_order(self, order):
        if order == self.entry_order:
            if order.status >= order.Completed:
                self.entry_order = None

                self.send_stop_order()

        if order == self.stop_order:
            if order.status >= order.Completed:
                self.stop_order = None

            if order.status == order.Cancelled:
                self.send_stop_order()

        elif order == self.exit_order:
            if order.status >= order.Completed:
                self.exit_order = None

    def send_entry_order(self):
        if self.entry_signal[0] > 0:
            self.entry_order = self.buy()
        elif self.entry_signal[0] < 0:
            self.entry_order = self.sell()


    def send_stop_order(self):
        if self.position.size > 0:
            self.stop_order = self.sell(exectype=bt.Order.Stop, price=self.stop_price[0])
        elif self.position.size < 0:
            self.stop_order = self.buy(exectype=bt.Order.Stop, price=self.stop_price[0])