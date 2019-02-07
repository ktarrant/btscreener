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
from collections import OrderedDict

# Third-party imports -----------------------------------------------
import pandas as pd
import requests
import backtrader as bt

# Our own imports ---------------------------------------------------

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

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

# DATA UTILS  -----------------------------------------
def parse_date(s):
    """ Try to parse a date like 2018-02-01, return None if we fail """
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return pd.NaT

def yield_quarter_ydays(dates):
    ydays = [dt.timetuple().tm_yday for dt in dates]
    last_yday = None
    for yday_min in range(0, 364, 91):
        yday_max = yday_min + 91
        matches = [yday for yday in ydays
                   if ((yday >= yday_min) and (yday < yday_max))]
        if len(matches) == 0:
            if last_yday:
                # yield a guess based on the previous quarter's result
                yield last_yday + 91
            else:
                # yield a guess based on when we think earnings season is
                yield yday_min + 31
        else:
            # yield the first match we get since we think it's the most recent
            yield matches[0]


def estimate_next(prev_dates):
    """
    Estimates the most likely next date based on previous dates
    Args:
        prev_dates (list(datetime.datetime)): List of previous dates to use
            for our guesses

    Returns:
        datetime.datetime: Best guess for next event
    """
    today = datetime.datetime.today()
    today_yday = today.timetuple().tm_yday
    ydays = list(yield_quarter_ydays(prev_dates))
    to_dt = lambda yday, year: (datetime.date(year, 1, 1)
                                + datetime.timedelta(yday - 1))
    dates = [to_dt(yday,
                   today.year if (today_yday < yday) else (today.year + 1))
             for yday in ydays
             ]
    return dates

# WEB LOADERS       -----------------------------------------
def load_historical(symbol, range="1m"):
    '''
    Loads historical data from IEX Finance

    Args:
        symbol (str): stock ticker to look up
        range (str): lookback period

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    '''
    url = URL_CHART.format(symbol=symbol, range=range)
    logger.info("Loading: '{}'".format(url))
    df = pd.DataFrame(requests.get(url).json())
    df["datetime"] = pd.to_datetime(df["date"])
    df = df.set_index("datetime")
    numeric_cols = [c for c in bt.feeds.PandasDirectData.datafields if c in df.columns]
    df = df[numeric_cols].apply(pd.to_numeric)
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
    try:
        df = pd.DataFrame(result["earnings"])
    except KeyError:
        return None
    df[["EPSReportDate", "fiscalEndDate"]] = (
        df[["EPSReportDate", "fiscalEndDate"]].applymap(parse_date))
    return df

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
    data = requests.get(url).json()
    try:
        df = pd.DataFrame(data)
    except ValueError:
        return None
    if "exDate" in df.columns:
        date_cols = ["declaredDate", "exDate", "paymentDate", "recordDate"]
        df[date_cols] = df[date_cols].applymap(parse_date)
        return df
    else:
        return None

def load_calendar(symbol):
    '''
    Loads calendar data from IEX Finance

    Args:
        symbol (str): stock ticker to look up

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    '''
    earnings = load_earnings(symbol)
    if earnings is not None:
        last_reportDates = earnings["EPSReportDate"]
        last_reportDate = max(last_reportDates)
        next_reportDates = estimate_next(last_reportDates)
        next_reportDate = min(next_reportDates)
    else:
        last_reportDate = None
        next_reportDate = None

    dividends = load_dividends(symbol)
    if dividends is not None:
        last_exDates = dividends["exDate"]
        last_exDate = max(last_exDates)
        next_exDates = estimate_next(last_exDates)
        next_exDate = min(next_exDates)
        last_dividend = dividends.iloc[0].loc["amount"]
    else:
        last_exDate = None
        last_dividend = None
        next_exDate = None

    calendar = pd.Series(OrderedDict([
        ("lastEPSReportDate", last_reportDate),
        ("nextEPSReportDate", next_reportDate),
        ("lastExDate", last_exDate),
        ("lastDividend", last_dividend),
        ("nextExDate", next_exDate),
    ]))
    return calendar

# ARGPARSE CONFIGURATION  -----------------------------------------
def add_subparser_historical(subparsers):
    """
    Loads historical data from IEX Finance

    Args:
        subparsers: subparsers to add to

    Returns:
        Created subparser object
    """
    def cmd_hist(args):
        return load_historical(args.symbol, args.range)

    hist_parser = subparsers.add_parser("historical", description="""
    loads historical OHLC data for a stock symbol 
    """)
    hist_parser.add_argument("symbol", type=str, help="stock ticker to look up")
    hist_parser.add_argument("-r", "--range", type=str, default="1m",
                             help="lookback period, default: 1m")
    hist_parser.set_defaults(func=cmd_hist,
                             output="{today}_{symbol}_{range}_ohlc.csv")
    return hist_parser


def add_subparser_calendar(subparsers):
    """
    Loads calendar (earnings and dividend) data from IEX Finance

    Args:
        args: parsed arguments object containing arguments for the
            load_earnings method

    Returns:
        pd.DataFrame: cached or loaded DataFrame
    """
    def cmd_calendar(args):
        return load_calendar(args.symbol)
    earnings_parser = subparsers.add_parser("calendar", description="""
    loads calendar earnings and dividend data with estimates for next event
    """)
    earnings_parser.add_argument("symbol", type=str,
                                 help="stock ticker to look up")
    earnings_parser.set_defaults(func=cmd_calendar,
                                 output="{today}_{symbol}_calendar.csv")
    return earnings_parser

# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
    Loads historical data locally or from IEX if necessary and caches it.
    """)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")
    parser.add_argument("-o", "--output",
                        help="output file format")

    subparsers = parser.add_subparsers()

    add_subparser_historical(subparsers)
    add_subparser_calendar(subparsers)

    args = parser.parse_args()
    args.today = datetime.date.today()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # execute the function
    table = args.func(args)

    # print and save the result for the user
    print(table)
    fn = args.output.format(**vars(args))
    logger.info("Saving to: {}".format(fn))
    table.to_csv(fn)
