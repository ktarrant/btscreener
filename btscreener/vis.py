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
"""
Visualize the results of scans and analysis
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging
import datetime

# Third-party imports -----------------------------------------------
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Our own imports ---------------------------------------------------
from collector import load_symbol_list, run_collection

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------
COLOR_NEUTRAL_LIGHT = '#E6E6FF'
COLOR_NEUTRAL_MID = '#CCCCFF'
COLOR_NEUTRAL_DARK = '#4D0066'
COLOR_BULLISH_BOLD = '#99E699'
COLOR_BULLISH_LIGHT = '#CCFFDD'
COLOR_BEARISH_BOLD = '#FF8080'
COLOR_BEARISH_LIGHT = ' #FFCCCC'

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
# HELPER FUNCTIONS -----------------------------------------
def create_annotations(scan_result, pct_table, level="resistance"):
    """
    Args:
        scan_result (pd.DataFrame): full scan results table
        pct_table (pd.DataFrame): table of perecentages made from scan_result
        level (str): which level to place the label

    Returns:
        list(dict): for use with layout.annotations
    """
    ay = -40 if level is "resistance" else 40
    return [
        dict(x=x,
             y=pct_table.loc[x, "close"],
             xref='x',
             yref='y',
             text='breakout ({})'.format(scan_result.loc[x, level]),
             showarrow=True,
             arrowhead=3,
             ax=0,
             ay=ay,
             )
        for x in pct_table.index
        if not pd.isnull(scan_result.loc[x, "breakout"])
    ]

# FUNCTION CATEGORY 1 -----------------------------------------
def create_master_table(group, output, scan_result):
    """
    Creates a giant table from the scan result

    Args:
        input (str): name of group to collect
        output (str): format of output file
        scan_result (pd.DataFrame): table to plot

    Returns:
        figure
    """
    # TODO: the third "by" should probably be the TDS#
    df = scan_result.reset_index()
    df.support = df.support.round(2)
    df.resistance = df.resistance.round(2)
    df = df.sort_values(by=["breakout", "flip", "trend",
                            "nextEPSReportDate", "nextExDate",
                            "index"],
                        ascending=False)#[False, False])
    bgcolor = lambda row: (
        COLOR_BULLISH_BOLD if row.breakout == 1.0 else (
        COLOR_BEARISH_BOLD if row.breakout == -1.0 else (
        COLOR_BULLISH_LIGHT if row.trend == 1.0 else (
        COLOR_BEARISH_LIGHT if row.trend == -1.0 else (
        COLOR_NEUTRAL_LIGHT)))))
    df["BgColor"] = df[["trend", "breakout"]].apply(bgcolor, axis=1)
    dcols = [
        "index",
        "trend", "flip", "breakout",
        "support", "resistance",
        "close", "wick",
        "nextEPSReportDate", "lastDividend", "nextExDate",
    ]
    trace = go.Table(
        header=dict(values=dcols,
                    fill=dict(color=COLOR_NEUTRAL_MID),
                    align=['left'] * 5),
        cells=dict(values=[df[col] for col in dcols],
                   fill=dict(color=[df.BgColor]),
                   align=['left'] * 5))

    layout = dict(title="{} ({})".format(group, datetime.date.today()))
    data = [trace]
    figure = dict(data=data, layout=layout)
    fn = output.format(group=group)
    py.plot(figure, filename=fn)
    return scan_result

def create_bar_graph(scan_result):
    """
    Plots the results of the scan as box graphs

    Args:
        scan_result (pd.DataFrame): table to plot

    Returns:
        figure
    """
    prices = scan_result[["prev_close", "close", "support", "resistance"]]
    off_close = prices.subtract(prices.close, axis=0)
    off_fixed = off_close.apply(np.nan_to_num)
    off_sup = off_fixed.subtract(off_fixed.support, axis=0)
    off_res = off_fixed.subtract(off_fixed.resistance, axis=0)
    pct_sup = off_sup.divide(scan_result.support, axis=0)
    pct_res = off_res.divide(scan_result.resistance, axis=0)
    final_bulls = pct_sup[scan_result.trend == 1.0].sort_values(by='close')
    final_bears = pct_res[scan_result.trend == -1.0].sort_values(by='close')
    #
    # trace_bulls = go.Ohlc(
    #                 x=final_bulls.index,
    #                 open=final_bulls.prev_close,
    #                 high=final_bulls.resistance,
    #                 low=[0] * len(final_bulls.index),
    #                 close=final_bulls.close,
    #                 name="bullish",
    #                 increasing=dict(line=dict(color=COLOR_BULL_UP)),
    #                 decreasing=dict(line=dict(color=COLOR_BULL_DOWN)))
    # trace_bears = go.Ohlc(
    #                 x=final_bears.index,
    #                 open=final_bears.prev_close,
    #                 high=[0] * len(final_bears.index),
    #                 low=final_bears.support,
    #                 close=final_bears.close,
    #                 name="bearish",
    #                 increasing=dict(line=dict(color=COLOR_BEAR_UP)),
    #                 decreasing=dict(line=dict(color=COLOR_BEAR_DOWN)))

    bull_annotations = create_annotations(scan_result, final_bulls)
    bear_annotations = create_annotations(scan_result, final_bears, level="support")
    layout = go.Layout(
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        ),
        yaxis=dict(title="% from Stop"),
        font=dict(family="Overpass", size=12),
        annotations=bull_annotations+bear_annotations,
    )
    data = [] # [trace_bulls, trace_bears]

    fig = go.Figure(data=data, layout=layout)
    return fig

# ARGPARSE CONFIGURATION  -----------------------------------------
def add_subparser_bar(subparsers):
    """
    Creates a bar chart from a scan table

    Args:
        subparsers: subparsers to add to

    Returns:
        Created subparser object
    """
    def cmd_bar(args):
        scan_result = pd.read_csv(args.input)
        fig = create_bar_graph(scan_result)
        fig["layout"]["title"] = args.input
        return fig

    parser = subparsers.add_parser("bar", description="""
    Creates a bar chart from a scan table
    """)
    parser.add_argument("-i", "--input",
                        help="input scan file to visualize or group to collect")
    parser.set_defaults(func=cmd_bar,
                        output="{input}-bar-latest")
    return parser

def add_subparser_table(subparsers):
    """
    Creates a plotly table from a scan table

    Args:
        subparsers: subparsers to add to

    Returns:
        Created subparser object
    """
    def cmd_table(args):
        symbol_list = load_symbol_list(groups=[args.group])
        scan_result = run_collection(symbol_list)
        chart_name = "{group}-table-latest".format(group=args.group)
        fig = create_master_table(args.group, chart_name, scan_result)
        return fig

    parser = subparsers.add_parser("table", description="""
    Creates a plotly table from a scan table
    """)
    parser.add_argument("-g", "--group",
                        help="group name to pass to collector")
    parser.set_defaults(func=cmd_table,
                        output="{today}-{group}-table.csv")
    return parser

# -----------------------------------------------------------------------------
# RUNTIME PROCEDURE
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse
    import datetime
    import pandas as pd

    parser = argparse.ArgumentParser(description="""
    Visualizes a scan generated by the collector
    """)
    parser.add_argument("-o", "--output",
                        help="output name format")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="use verbose logging")

    subparsers = parser.add_subparsers()

    bar_parser = add_subparser_bar(subparsers)
    table_parser = add_subparser_table(subparsers)

    args = parser.parse_args()
    args.today = datetime.date.today()

    # configure logging
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)

    # create a figure from the scan and plot it
    table = args.func(args)

