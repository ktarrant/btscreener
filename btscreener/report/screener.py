import logging
from collections import OrderedDict
import datetime

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

logger = logging.getLogger(__name__)

COLOR_NEUTRAL_LIGHT = '#E6E6FF'
COLOR_NEUTRAL_MID = '#CCCCFF'
COLOR_NEUTRAL_DARK = '#4D0066'
COLOR_BULLISH_BOLD = '#99E699'
COLOR_BULLISH_LIGHT = '#CCFFDD'
COLOR_BEARISH_BOLD = '#FF8080'
COLOR_BEARISH_LIGHT = '#FFCCCC'
COLOR_REVERSAL_WARN = "#FFFF80"
COLOR_REVERSAL_ALERT = "#8080FF"

EVENT_STAD_TREND_UP = "Bull"
EVENT_STAD_TREND_DN = "Bear"
EVENT_STAD_FLIP = "Flip"
EVENT_STAD_BREAKOUT = "Breakout"
EVENT_TD_WARN = "Warn"
EVENT_TD_FRESH = "Fresh"

def get_bg_color(trend=0, flip=0, breakout=0, **kwargs):
    """
    :param trend:
    :param flip:
    :param breakout:
    :param kwargs:
    :return:
    """
    if breakout > 0 or flip > 0:
        return COLOR_BULLISH_BOLD
    elif breakout < 0 or flip < 0:
        return COLOR_BEARISH_BOLD
    elif trend == 1:
        return COLOR_BULLISH_LIGHT
    elif trend == -1:
        return COLOR_BEARISH_LIGHT
    else:
        return COLOR_NEUTRAL_LIGHT

def make_screener_row(backtest_row):
    """
    Creates a summary row from the summaries of a symbol

    Args:
        symbol (str): symbol/index value of row from backtest summary table
        backtest_row (pd.Series): row from backtest summary table

    Returns:
        pd.Series: a row containing the important summary information
    """
    # set up the events column
    flipped = 1 if ((backtest_row.stad_trend > 0) and (
            backtest_row.prev_stad_trend <= 0)) else (
        -1 if (backtest_row.stad_trend < 0) and (
                backtest_row.prev_stad_trend >= 0) else 0)

    s_events = []
    if backtest_row.stad_trend > 0: s_events += [EVENT_STAD_TREND_UP]
    if backtest_row.stad_trend < 0: s_events += [EVENT_STAD_TREND_DN]
    if flipped != 0: s_events += [EVENT_STAD_FLIP]
    if backtest_row.stad_breakout != 0: s_events += [EVENT_STAD_BREAKOUT]
    td_events = ["{:.0f}".format(backtest_row.td_count)]
    if abs(backtest_row.td_reversal) > 0: td_events += [EVENT_TD_WARN]
    if ((abs(backtest_row.td_count) == 1) and
        (abs(backtest_row.prev_td_reversal) > 0)):
        td_events += [EVENT_TD_FRESH]
    next_earnings = ("" if pd.isnull(backtest_row.next_report_date)
                     else backtest_row.next_report_date)
    next_exdiv = ("" if pd.isnull(backtest_row.next_ex_date)
                  else backtest_row.next_ex_date)
    div_amount = ("" if pd.isnull(backtest_row.last_dividend_amount)
                  else backtest_row.last_dividend_amount)
    return pd.Series(OrderedDict([
        ("SuperTrend", " ".join(s_events)),
        ("TD Count", " ".join(td_events)),
        ("Close", "{:.2f}".format(backtest_row.close)),
        ("Support", "{:.2f}".format(backtest_row.stad_support)),
        ("Resistance", "{:.2f}".format(backtest_row.stad_resistance)),
        ("Next Earnings", next_earnings),
        ("Next Ex-Div", next_exdiv),
        ("Dividend Amount", div_amount),
        ("BgColor", get_bg_color(backtest_row.stad_trend,
                                 flipped,
                                 backtest_row.stad_breakout))
    ]))

def make_screener_table(title, backtest):
    """
    Creates a giant table from the scan result

    Args:
        title (str): title to use for filename and chart title
        backtest (pd.DataFrame): backtest summary table

    Returns:
        figure
    """
    df = backtest.sort_values(by=["td_count", "stad_breakout", "stad_trend",
                                  "next_report_date", "next_ex_date"],
                              ascending=False)
    df = df.apply(make_screener_row, axis=1).reset_index()
    bgcolor = df.pop("BgColor")
    trace = go.Table(
        header=dict(values=df.columns,
                    fill=dict(color=COLOR_NEUTRAL_MID),
                    align=['left'] * 5),
        cells=dict(values=[df[col] for col in df.columns],
                   fill=dict(color=[bgcolor]),
                   align=['left'] * 5))
    last_datetime = backtest.datetime.dropna().iloc[-1].date()
    layout = dict(title="{} ({})".format(title, last_datetime))
    data = [trace]
    figure = dict(data=data, layout=layout)
    logger.info("Creating plot '{}'".format(title))
    url = py.plot(figure, filename=title, auto_open=False)
    logger.info("Plot URL: {}".format(url))
    return url
