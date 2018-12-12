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
from filter import check_ad_breakout

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
dji_components = ["v", "xom", "wmt", "cat", "cvx", "aapl", "gs", "axp",
                  "ibm", "mcd", "mmm", "jpm", "ba", "trv", "msft", "dwdp",
                  "pg", "nke", "ko", "mrk", "dis", "csco", "intc", "jnj",
                  "pfe", "unh", "hd", "wba", "vz", "utx"]
"""list(str): List of Dow Jones Industrial Index component tickers."""

faves_components = ["aapl", "fb", "amzn", "goog", "nflx", # "FAANG"s
                    "dis", "de", "mcd", "ibm", "cpb", # grandpas
                    "nvda", "amd", "mu", "intc", # semis
                    "bac", "usb", "brk.b", # banks
                    "x", "cat", "ba", "luv", # trade wars
                    "tsla", "snap", "twtr", "spot",  # unicorns
                    "tlry", "cgc", "stz", # pot
                    "pfe", # healthcare
                    ]
"""list(str): List of liquid, optionable, and well-known tickers according
to the author """

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
def collect_stats(symbol, cache_historical=True):
    chart_stats = run_backtest(symbol, cache=cache_historical)
    calendar_stats = load_calendar(symbol)
    base = pd.concat([chart_stats, calendar_stats])
    base["breakout"] = check_ad_breakout(base)

    return base

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
    parser.add_argument("-s", "--symbol", action="append")
    parser.add_argument("-g", "--group", action="append",
                        choices=["faves", "dji"])
    parser.add_argument("-c", "--cache", action="store_true",
                        help="cache loaded data to reduce API queries")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")
    parser.add_argument("-o", "--out", default=DEFAULT_FILE_FORMAT,
                        help="output file format. default: {}".format(
                            DEFAULT_FILE_FORMAT))

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    symbols = args.symbol if args.symbol else []
    if not args.group:
        if len(symbols) == 0:
            raise ValueError("No symbols or groups provided")
    elif "faves" in args.group:
        symbols += faves_components
    elif "dji" in args.group:
        symbols += dji_components

    table = pd.DataFrame(generate_stats(symbols), index=symbols)

    # Print
    print(table)

    # Save to file
    fn = args.out.format(date=datetime.date.today())
    print("Saving to: {}".format(fn))
    table.to_csv(fn)
