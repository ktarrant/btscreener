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


# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

# SETUP HELPERS     -----------------------------------------
def configure_data(cerebro, symbol="aapl", range="1m"):
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
    print(df)
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
