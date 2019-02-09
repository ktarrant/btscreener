import numpy as np
import pandas as pd
import backtrader as bt


class ADBreakout(bt.Indicator):

    lines = (
        "distribution",
        "accumulation",
        "resistance",
        "support",
        "breakout",
    )


    plotinfo = dict(plot=True, subplot=False)


    plotlines = dict(
        distribution=dict(marker='o',
                          markersize=8.0,
                          color='red',
                          fillstyle='top',
                          ls=""),
        accumulation=dict(marker='o',
                          markersize=8.0,
                          color='green',
                          fillstyle='bottom',
                          ls=""),
    )

    def __init__(self, trend, wick):
        """
        Creates a breakout alert indicator using trend and wick source
        indicators
        :param trend: an indicator with lines 'trend' and 'stop'
        :param wick: an indicator with lines 'buy' and 'sell'
        """
        self.trend = trend
        self.wick = wick
        self.lines.distribution = bt.If(
            self.trend.lines.trend > 0, self.wick.lines.sell, np.NaN)
        self.lines.accumulation = bt.If(
            self.trend.lines.trend < 0, self.wick.lines.buy, np.NaN)

    def next(self):
        if self.trend.lines.trend[0] > 0:
            self.lines.support[0] = self.trend.lines.stop[0]

            if not pd.isnull(self.lines.distribution[0]):
                if pd.isnull(self.lines.resistance[-1]):
                    self.lines.resistance[0] = self.data.high[0]
                else:
                    self.lines.resistance[0] = max(
                        self.data.high[0], self.lines.resistance[-1])

            elif self.trend.lines.trend[-1] != 1.0:
                # we just flipped trends, we don't know resistance yet
                self.lines.resistance[0] = np.NaN

            else:
                self.lines.resistance[0] = self.lines.resistance[-1]

        elif self.trend.lines.trend[0] < 0:
            self.lines.resistance[0] = self.trend.lines.stop[0]

            if not pd.isnull(self.lines.accumulation[0]):
                if pd.isnull(self.lines.support[-1]):
                    self.lines.support[0] = self.data.low[0]
                else:
                    self.lines.support[0] = min(
                        self.data.low[0], self.lines.support[-1])

            elif self.st.lines.trend[-1] != -1.0:
                # we just flipped trends, we don't know resistance yet
                self.lines.support[0] = np.NaN

            else:
                self.lines.support[0] = self.lines.support[-1]
