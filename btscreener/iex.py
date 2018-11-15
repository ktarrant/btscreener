#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Methods for loading, caching, and saving IEX finance data

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
-v, --verbose : use verbose logging
-l, --live : use live updating
ARGUMENTS -------------------------------------------------------------
symbol : stock ticker to look up
interval : for example '5m' or 'D'
'''

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging
import datetime

# Third-party imports -----------------------------------------------
import pandas as pd
import backtrader as bt
import requests

# Our own imports ---------------------------------------------------

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
CACHE_FILE_FORMAT = "{today}_{symbol}_{range}.csv"

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
URL_CHART = "https://api.iextrading.com/1.0/stock/{symbol}/chart/{range}"

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
def load_cached_df(fn, url, force=False):
    '''
    Loads a DataFrame from a URL. If a cached DataFrame is already present
    locally, returns that instead.
    :param fn: str - filename of expected cached file
    :param url: str - url of the source data
    :param force: bool - if True, will skip checking for cache file
    :return: pd.DataFrame - cached or loaded DataFrame
    '''
    if not force:
        try:
            df = pd.read_csv(fn)
            return df
        except IOError:
            logger.debug("Cache file '{}' not found".format(fn))

    logger.info("Loading: '{}'".format(url))
    df = pd.DataFrame(requests.get(url).json())
    df.to_csv(fn)
    return df

# WEB LOADERS       -----------------------------------------
def load_historical(symbol, range="1m", force=False):
    '''
    Loads historical data from IEX Finance
    :param symbol: str - stock ticker to look up
    :param range: str - lookback period
    :param force: bool - if True, will skip checking for cache file
    :return: pd.DataFrame - DataFrame suitable for use with backtrader
    '''
    url = URL_CHART.format(symbol=symbol, range=range)
    today = datetime.date.today()
    fn = CACHE_FILE_FORMAT.format(today=today, symbol=symbol, range=range)
    return load_cached_df(fn, url, force)


# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
    Loads historical data locally or from IEX if necessary and caches it.
    """)
    parser.add_argument("symbol", type=str, help="stock ticker to look up")
    parser.add_argument("-r", "--range", type=str, default="1m",
                        help="lookback period")
    parser.add_argument("-f", "--force", action="store_true",
                        help="skip cache check step")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")

    args = parser.parse_args()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    df = load_historical(args.symbol, args.range, args.force)
    print(df)