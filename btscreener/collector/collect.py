import logging
from multiprocessing import Pool

import pandas as pd

from btscreener.sources.iex import (
    load_historical, load_dividends, load_earnings
)
from btscreener.summary.dividends import make_dividend_summary
from btscreener.summary.earnings import make_earnings_summary
from btscreener.chart.basket import BasketStrategy
from btscreener.chart.backtest import run_backtest

logger = logging.getLogger(__name__)

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
    hist = load_historical(symbol, lookback=BasketStrategy.get_min_period())
    chart_summary = run_backtest(hist, BasketStrategy)
    chunks = [chart_summary]
    dividend_history = load_dividends(symbol)
    if dividend_history is not None:
        chunks += [make_dividend_summary(dividend_history)]
    earnings_history = load_earnings(symbol)
    if earnings_history is not None:
        chunks += [make_earnings_summary(earnings_history)]
    combined = pd.concat(chunks)
    return combined

def run_collection(symbols, pool_size=0):
    if pool_size > 0:
        p = Pool(pool_size)
        table = pd.DataFrame(p.map(create_row, symbols), index=symbols)
        return table
    else:
        values = [create_row(symbol) for symbol in symbols]
        table = pd.DataFrame(values, index=symbols)
        return table