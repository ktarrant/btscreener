#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Technical Analysis
Using backtrader we can apply indicators to price data. These indicators
provide information and signals that can help the user make decisions.
"""
# -----------------------------------------------------------------------------
# Copyright (c) 2018, Kevin Tarrant (@ktarrant)
#
# Distributed under the terms of the MIT License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#
# REFERENCES:
# http://ipython.org/ipython-doc/rel-0.13.2/development/coding_guide.html
# https://www.python.org/dev/peps/pep-0008/
# -----------------------------------------------------------------------------
'''
OPTIONS ------------------------------------------------------------------
A description of each option that can be passed to this script
ARGUMENTS -------------------------------------------------------------
A description of each argument that can or must be passed to this script
'''

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging

# Third-party imports -----------------------------------------------
import backtrader as bt
import pandas as pd
import numpy as np

# Our own imports ---------------------------------------------------
from iex import load_historical

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# LOCAL UTILITIES
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------
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
        self.highest = bt.indicators.Highest(self.data.high, period=self.p.period)
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



class WickReversalSignal(bt.Indicator):
    """
    Pattern Summary
    1. The body is used to determine the size of the reversal wick. A wick that is between 2.5 to 3.5 times larger than
    the size of the body is ideal.
    2. For a bullish reversal wick to exist, the close of the bar should fall within the top 35 percent of the overall
    range of the candle.
    3. For a bearish reversal wick to exist, the close of the bar should fall within the bottom 35 percent of the
    overall range of the candle.
    """

    lines = (
        "buy",
        "sell",
    )

    params = (
        ("wick_multiplier_min", 2.5),
        ("close_percent_max", 0.35)
    )

    plotinfo = dict(
        plot=True, subplot=False, plotlinelabels=True
    )

    plotlines = dict(
        buy=dict(marker='o', markersize=8.0, color='blue', fillstyle='bottom', ls=""),
        sell=dict(marker='o', markersize=8.0, color='red', fillstyle='top', ls=""),
    )

    def __init__(self):
        wick_range = self.data.high - self.data.low
        body_high = bt.Max(self.data.close, self.data.open)
        body_low = bt.Min(self.data.close, self.data.open)
        body_range = body_high - body_low
        wick_buy = (body_low - self.data.low) >= (self.p.wick_multiplier_min * body_range)
        wick_sell = (self.data.high - body_high) >= (self.p.wick_multiplier_min * body_range)
        # be careful, if wick range = 0 then close-low = 0 ; so avoiding divide by zero list this is correct
        close_percent = (self.data.close - self.data.low) / bt.If(wick_range == 0.0, 0.1, wick_range)
        close_buy = (close_percent >= (1 - self.p.close_percent_max))
        close_sell = (close_percent <= self.p.close_percent_max)
        self.lines.buy = bt.If(bt.And(wick_buy, close_buy), self.data.low, np.NaN)
        self.lines.sell = bt.If(bt.And(wick_sell, close_sell), self.data.high, np.NaN)


class SupertrendAD(bt.Strategy):

    def __init__(self):
        self.st = Supertrend()
        self.ad = WickReversalSignal()
        
# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

# SETUP HELPERS     -----------------------------------------
def configure_data(cerebro, symbol="aapl", range="6m"):
    '''
    Runs strategy against historical data
    :param cerebro: bt.Cerebro - cerebro object to configure
    :param symbol: str - symbol of historical data to configure
    :param range: str - range of historical data to configure
    :return: type - description of the value returned
    '''
    df = load_historical(symbol, range=range)
    df["datetime"] = pd.to_datetime(df["date"])
    df = df.set_index("datetime")
    numeric_cols = [c for c in bt.feeds.PandasDirectData.datafields if c in df.columns]
    df = df[numeric_cols].apply(pd.to_numeric)
    data = bt.feeds.PandasDirectData(dataname=df, openinterest=-1)
    cerebro.adddata(data)
    cerebro.addstrategy(SupertrendAD)
    return cerebro


# FUNCTION CATEGORY 2 -----------------------------------------


# FUNCTION CATEGORY n -----------------------------------------


# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
    Complete description of the runtime of the script, what it does and how it
    should be used
    """)
    parser.add_argument("--symbol", type=str, default="aapl", help="stock ticker to look up")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # Set up Cerebro for a backtest
    cerebro = bt.Cerebro()

    # Set up the data source
    cerebro = configure_data(cerebro)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    result = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(style='candle')