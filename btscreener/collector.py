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
from multiprocessing import Pool

# Third-party imports -----------------------------------------------
import pandas as pd
from bs4 import BeautifulSoup

# Our own imports ---------------------------------------------------
from btscreener.chart import run_backtest, SCAN_RANGE
from btscreener.iex import load_calendar, load_historical

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
dji_components = ["v", "xom", "wmt", "cat", "cvx", "aapl", "gs", "axp",
                  "ibm", "mcd", "mmm", "jpm", "ba", "trv", "msft", "dwdp",
                  "pg", "nke", "ko", "mrk", "dis", "csco", "intc", "jnj",
                  "pfe", "unh", "hd", "wba", "vz", "utx"]
"""list(str): List of Dow Jones Industrial Index component tickers."""

default_faves = ["aapl", "fb", "amzn", "goog", "nflx", # "FAANG"s
                    "dis", "de", "mcd", "ibm", "cpb", # grandpas
                    "nvda", "amd", "mu", "intc", # semis
                    "bac", "usb", "brk.b", # banks
                    "x", "cat", "ba", "luv", # trade wars
                    "tsla", "snap", "twtr", "spot",  # unicorns
                    "tlt", "gld", "jnk", "uso", "ung", # etn's
                    "tlry", "cgc", "stz", # pot
                    "pfe", "jnj", # healthcare
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
def load_sp500_weights():
    cache_fn = "sp500_weights.csv"
    try:
        sp500_weights = pd.read_csv(cache_fn)
    except IOError:
        # "spx_page.html" is an html page manually saved from the source of
        # https://www.slickcharts.com/sp500
        with open("spx_page.html") as fobj:
            soup = BeautifulSoup(fobj.read())

        columns = [th.text.strip() for th in soup.thead.find_all('th')]
        rows = [[td.text.strip() for td in tr.find_all("td")]
                for tr in soup.tbody.find_all("tr")]
        df = pd.DataFrame(rows, columns=columns)
        df.Change = df.Change.apply(lambda s: float(s.split("  ")[0]))
        df.Price = df.Price.apply(lambda s: float(s.replace(",", "")))
        df.Weight = df.Weight.apply(float)
        df.to_csv(cache_fn)
        sp500_weights = df

    return sp500_weights

def load_faves(fn="faves-tastyworks.csv"):
    try:
        # note that the exported files from tastyworks often need some doctoring
        # tickers are added that have been long bought out or bankrupt
        # and other tickers are for indices, which IEX won't have
        faves = pd.read_csv(fn)
        return list(faves.Symbol)
    except IOError:
        return default_faves

# COLLECTION GENERATOR -----------------------------------------
def create_row(symbol):
    """
    Collects chart and calendar data for a ticker and returns a DataFrame
    containing the combined results

    Args:
        symbol (str): ticker to look up

    Yields:
        OrderedDict: A dict-like row for an array-like, with the first key
            being "symbol".
    """
    logger.info("Collecting stats for symbol: {}".format(symbol))
    hist = load_historical(symbol, range=SCAN_RANGE)
    chart_stats = run_backtest(hist)
    calendar_stats = load_calendar(symbol)
    combined = pd.concat([chart_stats, calendar_stats])
    return combined

def run_collection(symbols, pool_size=8):
    p = Pool(pool_size)
    table = pd.DataFrame(p.map(create_row, symbols), index=symbols)
    return table

# ARGPARSE CONFIGURATION  -----------------------------------------
def load_symbol_list(groups=["faves"], symbols=[]):
    if "faves" in groups:
        symbols += load_faves()
    elif "dji" in groups:
        symbols += dji_components
    elif "sp" in groups:
        weights = load_sp500_weights()
        symbols += list(weights.Symbol)
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
        groups = args.group if args.group else []
        groups += ["{}s".format(len(args.symbol))] if args.symbol else []
        args.group_label = "-".join(groups)
        symbols = load_symbol_list(groups=args.group if args.group else [],
                                   symbols=args.symbol if args.symbol else [])
        return run_collection(symbols)

    parser = subparsers.add_parser("collect", description="""
    collects summary technical and event data for a group of stock tickers
    """)
    parser.add_argument("-s", "--symbol", action="append")
    parser.add_argument("-g", "--group", action="append",
                        choices=["faves", "dji", "sp"])

    parser.set_defaults(func=cmd_collect,
                        output="{today}_[{group_label}].csv")
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
    args.today = datetime.date.today()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # execute the function
    table = args.func(args)

    # print and save the result for the user
    print(table)
    table.to_csv(args.output.format(**vars(args)))
