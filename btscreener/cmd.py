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
""" Command line utilities
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging
import datetime

# Third-party imports -----------------------------------------------
import pandas as pd

# Our own imports ---------------------------------------------------
from iex import (add_subparser_historical, add_subparser_calendar,
    load_historical, load_calendar
)
from chart import add_subparser_scan, add_subparser_plot
from collector import add_subparser_collect, load_symbol_list, run_collection

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
CACHE_FILE_HISTORICAL_FORMAT = "{today}_{symbol}_{range}.csv"
CACHE_FILE_CALENDAR_FORMAT = "{today}_{symbol}_calendar.csv"
CACHE_FILE_COLLECT_FORMAT = "{today}_SuperAD_scan[{modes}].csv"

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

# CACHE UTILITIES -----------------------------------------
def load_cached(method, fn, force=False, **kwargs):
    """

    Args:
        method (function): a function returning a dataframe
        fn (str): filename format to use for caching
        force (bool): if True, will not check for cached file and get from web
        args: args object to be passed to method

    Returns:
        dataframe

    """
    today = datetime.date.today()
    fn = fn.format(today=today, **kwargs)
    if not force:
        try:
            df = pd.read_csv(fn)
            return df
        except IOError:
            logger.debug("Cache file '{}' not found".format(fn))

    df = method(**kwargs)
    try:
        df.to_csv(fn)
    except IOError:
        logger.error("Failed to save cache file '{}'".format(fn))
    return df

def load_cached_historical(args):
    """

    Args:
        args: args object

    Returns:
        dataframe
    """
    return load_cached(load_historical, CACHE_FILE_HISTORICAL_FORMAT,
                       force=args.force,
                       symbol=args.symbol, range=args.range,
                       )

def load_cached_calendar(args):
    """
    Args:
        args: args object

    Returns:
        dataframe
    """
    return load_cached(load_calendar, CACHE_FILE_CALENDAR_FORMAT,
                       force=args.force,
                       symbol=args.symbol,
                       )

def load_cached_collect(args):
    """
    Args:
        args: args object

    Returns:
        dataframe
    """
    modes = args.group if args.group else []
    modes += ["{}s".format(len(args.symbol))] if args.symbol else []
    symbols = load_symbol_list(groups=args.group if args.group else [],
                               symbols=args.symbol if args.symbol else [])
    return load_cached(run_collection, CACHE_FILE_COLLECT_FORMAT,
                       force=args.force,
                       symbols=symbols,
                       modes="-".join(modes)
                       )

# FUNCTION CATEGORY n -----------------------------------------

# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
    Loads historical data locally or from IEX if necessary and caches it.
    """)
    parser.add_argument("-f", "--force", action="store_true",
                        help="force update from web")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")

    subparsers = parser.add_subparsers()

    iex_parser = subparsers.add_parser("iex", help="""
    Loads and saves data from IEX finance
    """)
    iex_subparsers = iex_parser.add_subparsers()

    hist_parser = add_subparser_historical(iex_subparsers)
    hist_parser.set_defaults(func=load_cached_historical)

    cal_parser = add_subparser_calendar(iex_subparsers)
    cal_parser.set_defaults(func=load_cached_calendar)

    chart_parser = subparsers.add_parser("chart", help="""
    Runs backtests against OHLC data using techinical indicators
    """)
    chart_subparsers = chart_parser.add_subparsers()

    add_subparser_scan(chart_subparsers)
    add_subparser_plot(chart_subparsers)

    collector_parser = subparsers.add_parser("collector", help="""
    Collects summary data from a batch of symbols
    """)
    collector_subparsers = collector_parser.add_subparsers()

    collect_parser = add_subparser_collect(collector_subparsers)
    collect_parser.set_defaults(func=load_cached_collect)

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # execute the function
    table = args.func(args)

    # print the result for the user
    print(table)