import logging
import datetime

import pandas as pd
import numpy as np
import requests


URL_CHART = "https://api.iextrading.com/1.0/stock/{symbol}/chart/{range}"
URL_EARNINGS = "https://api.iextrading.com/1.0/stock/{symbol}/earnings"
URL_DIVIDENDS = (
    "https://api.iextrading.com/1.0/stock/{symbol}/dividends/{range}"
)

HISTORICAL_DATE_COLUMNS = ["date"]
DIVIDEND_DATE_COLUMNS = ["declaredDate", "exDate", "paymentDate", "recordDate"]
EARNINGS_DATE_COLUMNS = ["EPSReportDate", "fiscalEndDate"]


logger = logging.getLogger(__name__)


class RequestException(Exception):
    """
    Exception for when we fail to complete a data query
    """
    pass


def parse_date(s):
    """
    Try to parse a date like 2018-02-01
    :param s: a date string that looks like "YYYY-MM-DD"
    :return: the parsed date or NaT if we fail
    :type: datetime.date
    """
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return pd.NaT


def parse_numeric(s, how=pd.to_numeric):
    """
    Try to parse a numeric string
    :param s: a string that looks like a number
    :param how: how to parse the string
    :return: the parsed number or NaN if we fail
    """
    try:
        return how(s)
    except ValueError:
        return np.NaN


def load_historical(symbol, lookback="1m"):
    """
    Loads historical data from IEX Finance
    :param symbol: stock ticker to look up
    :type: str
    :param lookback: lookback period
    :type: int
    :return: loaded DataFrame
    :type: pd.DataFrame
    """
    url = URL_CHART.format(symbol=symbol, range=lookback)
    logger.info("Loading: '{}'".format(url))
    result = requests.get(url).json()
    try:
        df = pd.DataFrame(result)
    except KeyError:
        return None
    df[HISTORICAL_DATE_COLUMNS] = df[HISTORICAL_DATE_COLUMNS].applymap(
        parse_date)
    return df


def load_earnings(symbol):
    """
    Loads earnings data from IEX Finance
    :param symbol: stock ticker to look up
    :type: str
    :return: loaded table
    :type: pd.DataFrame
    """
    url = URL_EARNINGS.format(symbol=symbol)
    logger.info("Loading: '{}'".format(url))
    result = requests.get(url).json()
    try:
        df = pd.DataFrame(result["earnings"])
    except KeyError:
        return None
    df[EARNINGS_DATE_COLUMNS] = df[EARNINGS_DATE_COLUMNS].applymap(parse_date)
    return df


def load_dividends(symbol, lookback="5y"):
    """
    Loads dividends data from IEX Finance
    :param symbol: stock ticker to look up
    :type: str
    :param lookback: lookback period
    :type: int
    :return: loaded DataFrame
    :type: pd.DataFrame
    """
    url = URL_DIVIDENDS.format(symbol=symbol, range=lookback)
    logger.info("Loading: '{}'".format(url))
    data = requests.get(url).json()
    if len(data) == 0:
        return None
    try:
        df = pd.DataFrame(data)
    except ValueError:
        return None

    df[DIVIDEND_DATE_COLUMNS] = df[DIVIDEND_DATE_COLUMNS].applymap(parse_date)
    return df
