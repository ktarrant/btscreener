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
from btscreener.chart import run_backtest
from iex import load_calendar

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

# PER-TICKER COLLECTION -----------------------------------------
def collect_stats(symbol):
    chart_stats = run_backtest(symbol)
    calendar_stats = load_calendar(symbol)
    return pd.concat([chart_stats, calendar_stats])

# COLLECTION GENERATOR -----------------------------------------
def generate_stats(index):
    """
    Collects chart and calendar data for each ticker in the index and returns
    a DataFrame containing the tabulated results
    Args:
        index (list-like): Index of tickers to use

    Yields:
        OrderedDict: A dict-like row for an array-like, with the first key
            being "symbol".
    """
    for symbol in index:
        logger.info("Collecting stats for symbol: {}".format(symbol))
        yield collect_stats(symbol)

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

    table = pd.DataFrame(generate_stats(dji_components), index=dji_components)

    # Save to file
    fn = args.out.format(date=datetime.date.today())
    print("Saving to: {}".format(fn))
    table.to_csv(fn)

    # Print
    print(table)