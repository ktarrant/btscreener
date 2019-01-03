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
import os
from collections import OrderedDict

# Third-party imports -----------------------------------------------
import backtrader as bt
import pandas as pd

# Our own imports ---------------------------------------------------
from btscreener.chart import run_backtest
from iex import load_calendar, load_historical

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

# SYMBOL LOADERS -----------------------------------------
def load_sp_components(fn="sp500_weights.csv"):
    dirname = os.path.dirname(__file__)
    sp500_weights_src = os.path.join(dirname, fn)
    sp500_weights = pd.read_csv(sp500_weights_src)
    return list(sp500_weights.Symbol)

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
        hist = load_historical(symbol)
        chart_stats = run_backtest(hist)
        calendar_stats = load_calendar(symbol)
        combined = pd.concat([chart_stats, calendar_stats])
        yield combined


def run_collection(symbols, **kwargs):
    table = pd.DataFrame(generate_stats(symbols), index=symbols)
    return table

# ARGPARSE CONFIGURATION  -----------------------------------------
def load_symbol_list(groups=["faves"], symbols=[]):
    if "faves" in groups:
        symbols += faves_components
    elif "dji" in groups:
        symbols += dji_components
    elif "sp" in groups:
        symbols += load_sp_components()
    if len(symbols) == 0:
        raise ValueError("No symbols or groups provided")
    # make sure it's unique
    return list(set(symbols))

def add_subparser_collect(subparsers):
    """
    Loads historical data from IEX Finance

    Args:
        subparsers: subparsers to add to

    Returns:
        Created subparser object
    """
    def cmd_collect(args):
        symbols = load_symbol_list(groups=args.group if args.group else [],
                                   symbols=args.symbol if args.symbol else [])
        return run_collection(symbols)

    parser = subparsers.add_parser("collect", description="""
    collects summary technical and event data for a group of stock tickers
    """)
    parser.add_argument("-s", "--symbol", action="append")
    parser.add_argument("-g", "--group", action="append",
                        choices=["faves", "dji", "sp"])
    # parser.add_argument("-o", "--out", default=DEFAULT_FILE_FORMAT,
    #                     help="output file format. default: {}".format(
    #                         DEFAULT_FILE_FORMAT))

    # # Save to file
    # fn = args.out.format(date=datetime.date.today())
    # print("Saving to: {}".format(fn))
    # table.to_csv(fn)
    parser.set_defaults(func=cmd_collect)
    return parser

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

    subparsers = parser.add_subparsers()
    scan_parser = add_subparser_collect(subparsers)

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    table = args.func(args)

    # Print
    print(table)
