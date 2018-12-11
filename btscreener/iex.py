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
"""Methods for loading, caching, and saving IEX finance data
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging
import datetime

# Third-party imports -----------------------------------------------
import pandas as pd
import requests

# Our own imports ---------------------------------------------------

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
CACHE_FILE_HISTORICAL_FORMAT = "{today}_{symbol}_{range}.csv"
CACHE_FILE_CALENDAR_FORMAT = "{today}_{symbol}_calendar.csv"

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
URL_CHART = "https://api.iextrading.com/1.0/stock/{symbol}/chart/{range}"
URL_EARNINGS = "https://api.iextrading.com/1.0/stock/{symbol}/earnings"
URL_DIVIDENDS = (
    "https://api.iextrading.com/1.0/stock/{symbol}/dividends/{range}"
)
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

# CACHE UTILS       -----------------------------------------

# WEB LOADERS       -----------------------------------------
def load_historical(symbol, range="1m", force=False):
    '''
    Loads historical data from IEX Finance

    Args:
        symbol (str): stock ticker to look up
        range (str): lookback period
        force (bool): if True, will skip checking for cache file

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    '''
    url = URL_CHART.format(symbol=symbol, range=range)
    today = datetime.date.today()
    fn = CACHE_FILE_HISTORICAL_FORMAT.format(
        today=today, symbol=symbol, range=range)
    if not force:
        try:
            df = pd.read_csv(fn)
            return df
        except IOError:
            logger.debug("Cache file '{}' not found".format(fn))

    logger.info("Loading: '{}'".format(url))
    df = pd.DataFrame(requests.get(url).json())
    try:
        df.to_csv(fn)
    except IOError:
        logger.error("Failed to save/cache to path: {}", fn)
    return df

def load_earnings(symbol):
    '''
    Loads earnings data from IEX Finance

    Args:
        symbol (str): stock ticker to look up

    Returns:
        pd.DataFrame: loaded DataFrame
    '''
    url = URL_EARNINGS.format(symbol=symbol)
    logger.info("Loading: '{}'".format(url))
    result = requests.get(url).json()
    df = pd.DataFrame(result["earnings"])
    return df.set_index("EPSReportDate")

def load_dividends(symbol, range='1y'):
    '''
    Loads dividends data from IEX Finance

    Args:
        symbol (str): stock ticker to look up
        range (str): lookback period

    Returns:
        pd.DataFrame: loaded DataFrame
    '''
    url = URL_DIVIDENDS.format(symbol=symbol, range=range)
    logger.info("Loading: '{}'".format(url))
    df = pd.DataFrame(requests.get(url).json())
    return df.set_index("exDate")

def load_calendar(symbol, force=False):
    '''
    Loads calendar data from IEX Finance

    Args:
        symbol (str): stock ticker to look up
        force (bool): if True, will skip checking for cache file

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    '''

    today = datetime.date.today()
    fn = CACHE_FILE_CALENDAR_FORMAT.format(today=today, symbol=symbol)
    if not force:
        try:
            df = pd.read_csv(fn)
            return df
        except IOError:
            logger.debug("Cache file '{}' not found".format(fn))

    earnings = load_earnings(symbol)
    dividends = load_dividends(symbol)
    df = pd.concat([earnings, dividends])

    try:
        df.to_csv(fn)
    except IOError:
        logger.error("Failed to save/cache to path: {}", fn)
    return df

# ARGPARSE COMMANDS  -----------------------------------------
def load_historical_cmd(args):
    """
    Loads historical data from IEX Finance

    Args:
        args: parsed arguments object containing arguments for the
            load_historical method

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    """
    return load_historical(args.symbol, args.range, args.force)


def load_calendar_cmd(args):
    """
    Loads calendar (earnings and dividend) data from IEX Finance

    Args:
        args: parsed arguments object containing arguments for the
            load_earnings method

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    """
    return load_calendar(args.symbol, args.force)

# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
    Loads historical data locally or from IEX if necessary and caches it.
    """)
    parser.add_argument("-f", "--force", action="store_true",
                        help="skip cache check step")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")

    subparsers = parser.add_subparsers()

    hist_parser = subparsers.add_parser("historical")
    hist_parser.add_argument("symbol", type=str, help="stock ticker to look up")
    hist_parser.add_argument("-r", "--range", type=str, default="1m",
                             help="lookback period")
    hist_parser.set_defaults(func=load_historical_cmd)

    earnings_parser = subparsers.add_parser("calendar")
    earnings_parser.add_argument("symbol", type=str, help="stock ticker to look up")
    earnings_parser.set_defaults(func=load_calendar_cmd)

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    df = args.func(args)
    print(df)