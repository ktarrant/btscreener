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
from btscreener.iex import add_subparser_historical, add_subparser_calendar
from btscreener.chart import add_subparser_scan, add_subparser_plot
from btscreener.collector import add_subparser_collect
from btscreener.vis import add_subparser_table
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
    parser.add_argument("-o", "--output",
                        help="output file format")
    parser.add_argument("-c", "--csv", action="store_true",
                        help="save csv copy using output name")

    subparsers = parser.add_subparsers()

    iex_parser = subparsers.add_parser("iex", help="""
    Loads and saves data from IEX finance
    """)
    iex_subparsers = iex_parser.add_subparsers()

    hist_parser = add_subparser_historical(iex_subparsers)
    cal_parser = add_subparser_calendar(iex_subparsers)

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

    vis_parser = subparsers.add_parser("vis", help="""
    Collects summary data from a batch of symbols
    """)
    vis_subparsers = vis_parser.add_subparsers()

    table_parser = add_subparser_table(vis_subparsers)

    args = parser.parse_args()
    args.today = datetime.date.today()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # execute the function
    table = args.func(args)

    # print and save the result for the user
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(table)

    if args.csv:
        fn = args.output.format(**vars(args))
        logger.info("Saving to: {}".format(fn))
        table.to_csv(fn)
