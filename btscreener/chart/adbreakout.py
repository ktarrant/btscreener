import numpy as np
import pandas as pd
import backtrader as bt

from .supertrend import Supertrend
from .priceaction import WickReversalSignal

class ADBreakout(bt.Indicator):

    params = (
        ("trend_src", Supertrend),
        ("ad_src", WickReversalSignal),
    )

    lines = (
        "trend",
        "stop",
        "ad",
        "resistance",
        "support",
        "breakout",
    )


    plotinfo = dict(plot=True, subplot=False)

    def __init__(self):
        """
        Creates a breakout alert indicator using trend and wick source
        indicators
        """
        self.trend = self.p.trend_src(self.data)
        self.ad = self.p.ad_src(self.data)
        self.distribution = bt.If(
            self.trend.lines.trend > 0, self.ad.lines.wick < 0, np.NaN)
        self.accumulation = bt.If(
            self.trend.lines.trend < 0, self.ad.lines.wick > 0, np.NaN)

    def next(self):
        if self.trend.lines.trend[0] > 0:
            self.lines.support[0] = self.trend.lines.stop[0]

            if not pd.isnull(self.distribution[0]):
                if pd.isnull(self.lines.resistance[-1]):
                    self.lines.resistance[0] = self.data.high[0]
                else:
                    self.lines.resistance[0] = max(
                        self.data.high[0], self.lines.resistance[-1])

            elif self.trend.lines.trend[-1] <= 0:
                # we just flipped trends, we don't know resistance yet
                self.lines.resistance[0] = np.NaN

            else:
                self.lines.resistance[0] = self.lines.resistance[-1]

        elif self.trend.lines.trend[0] < 0:
            self.lines.resistance[0] = self.trend.lines.stop[0]

            if not pd.isnull(self.accumulation[0]):
                if pd.isnull(self.lines.support[-1]):
                    self.lines.support[0] = self.data.low[0]
                else:
                    self.lines.support[0] = min(
                        self.data.low[0], self.lines.support[-1])

            elif self.trend.lines.trend[-1] >= 0:
                # we just flipped trends, we don't know resistance yet
                self.lines.support[0] = np.NaN

            else:
                self.lines.support[0] = self.lines.support[-1]
