from collections import OrderedDict

import pandas as pd

from .dateutil import yield_period_ydays


def make_dividend_summary(dividend_history):
    """
    Creates a summary of the provided dividend history and provides a best guess
    for the next dividend.
    :param dividend_history: table of past dividend payments
    :type: pd.DataFrame
    :return: series of summary data
    :type: pd.Series
    """
    # TODO: Make the 'after' configurable instead of using default today
    # TODO: Compute the dividend period from previous dates instead of using
    # default of quarterly
    last_ex_dates = dividend_history["exDate"]
    next_ex_dates = list(yield_period_ydays(last_ex_dates))
    next_ex_date = min(next_ex_dates)
    # we use this somewhat odd init pattern to do a key-value view
    return pd.Series(OrderedDict([
        ("last_ex_date", max(last_ex_dates)),
        ("last_dividend_amount", dividend_history.iloc[0].loc["amount"]),
        ("dividend_period", 91),
        ("next_ex_date", next_ex_date),
    ]))
