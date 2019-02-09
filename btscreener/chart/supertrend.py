import numpy as np
import backtrader as bt


class Supertrend(bt.Indicator):
    params = (
        ('factor', 3.0),
        ('period', 7),
        ('use_wick', True),
    )

    lines = ('trend', 'stop')
    plotinfo = dict(plot=True, subplot=False)

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.p.period)
        self.highest = bt.indicators.Highest(
            self.data.high, period=self.p.period)
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.p.period)
        self.hl2 = (self.highest.lines.highest + self.lowest.lines.lowest) / 2.0
        self.up = self.hl2 - self.p.factor * self.atr
        self.down = self.hl2 + self.p.factor * self.atr
        # for next
        self.last_trend_up = np.NaN
        self.last_trend_down = np.NaN

    def next(self):
        trend_up = (
            max(self.up[0], self.last_trend_up)
            if self.data.close[-1] > self.last_trend_up
            else self.up[0]
        )

        trend_down = (
            min(self.down[0], self.last_trend_down)
            if self.data.close[-1] < self.last_trend_down
            else self.down[0]
        )

        top_value = self.data.high[0] if self.p.use_wick else self.data.close[0]
        bottom_value = self.data.low[0] if self.p.use_wick else self.data.close[0]
        if top_value > self.last_trend_down:
            trend = 1
        elif bottom_value < self.last_trend_up:
            trend = -1
        elif np.isnan(self.lines.trend[-1]):
            trend = 1
        else:
            trend = self.lines.trend[-1]

        self.last_trend_up = trend_up
        self.last_trend_down = trend_down

        self.lines.trend[0] = trend
        self.lines.stop[0] = trend_up if self.lines.trend[0] == 1.0 else trend_down