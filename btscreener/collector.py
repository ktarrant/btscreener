#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""
Runs backtrader on many symbols and collects the relevant outputs from each
run into a combined data table keyed on symbol.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging
from collections import OrderedDict

# Third-party imports -----------------------------------------------
import backtrader as bt
import pandas as pd

# Our own imports ---------------------------------------------------
from btscreener.chart import (
    configure_data, extract_indicators, SupertrendADStrategy)

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
dji_components = ["v", "xom", "wmt", "cat", "cvx", "aapl", "gs", "axp",
                  "ibm", "mcd", "mmm", "jpm", "ba", "trv", "msft", "dwdp",
                  "pg", "nke", "ko", "mrk", "dis", "csco", "intc", "jnj",
                  "pfe", "unh", "hd", "wba", "vz", "utx"]
"""list(str): List of Dow Jones Industrial Index component tickers."""

DEFAULT_FILE_FORMAT = "{date}_SuperAD_scan.csv"
""" str: Default path format for output CSV file when run as a script """

# -----------------------------------------------------------------------------
# LOCAL UTILITIES
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# EXCEPTIONS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

# DATA CONFIGURATION -----------------------------------------
def configure_datas(cerebro, index, range="3m"):
    """
    Configures a cerebro object with a bunch of datas objects
    The format for a parameter is::

    Args:
        cerebro (bt.Cerebro): cerebro object to configure
        index (list-like): Index of tickers to use, a data object will be
            created for each ticker.
        range (str): range of historical data to configure

    Returns:
        bt.Cerebro: updated cerebro object
    """
    for symbol in index:
        cerebro = configure_data(cerebro, symbol, range)
    return cerebro

# FUNCTION CATEGORY 2 -----------------------------------------
def collect_indicators(result, index):
    """
    Extracts the indicators from each results section and yields them as a
    row an array-like

    Args:
        results (list(bt.Strategy)): List of Strategy instances returned by the
            backtrader runs on each data source
        index (list-like): Index of tickers to use, mapping to the datas
            objects in the Strategy

    Yields:
        OrderedDict: A dict-like row for an array-like, with the first key
            being "symbol".
    """
    return pd.DataFrame(extract_indicators(result), index=index)

# FUNCTION CATEGORY n -----------------------------------------


# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse
    import datetime

    parser = argparse.ArgumentParser(description="""
    Complete description of the runtime of the script, what it does and how it
    should be used
    """)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")
    parser.add_argument("-o", "--out", default=DEFAULT_FILE_FORMAT,
                        help="output file format. default: {}".format(
                            DEFAULT_FILE_FORMAT))

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # Set up Cerebro for a backtest
    cerebro = bt.Cerebro()

    # Set up the data sources for the DJI components
    cerebro = configure_datas(cerebro, dji_components)

    # Add an indicator that we can extract afterwards
    cerebro.addstrategy(SupertrendADStrategy)

    # Run over everything
    results = cerebro.run()

    # Extract the results
    table = collect_indicators(results[0], dji_components)

    # Save to file
    fn = args.out.format(date=datetime.date.today())
    print("Saving to: {}".format(fn))
    table.to_csv(fn)

    # Print
    print(table)