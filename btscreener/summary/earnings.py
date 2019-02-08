from collections import OrderedDict

import pandas as pd

from .dateutil import yield_period_ydays


def make_earnings_summary(earnings_history):
    """
    Creates a summary of the provided earnings history and provides a best guess
    for the next earnings.
    :param earnings_history: table of past earnings reports
    :type: pd.DataFrame
    :return: series of summary data
    :type: pd.Series
    """
    # TODO: Make the 'after' configurable instead of using default today
    # TODO: Compute the dividend period from previous dates instead of using
    last_report_dates = earnings_history["EPSReportDate"]
    next_report_dates = list(yield_period_ydays(last_report_dates))
    # we use this somewhat odd init pattern to do a key-value view
    return pd.Series(OrderedDict([
        ("last_report_date", max(last_report_dates)),
        ("next_report_date", min(next_report_dates)),
    ]))
