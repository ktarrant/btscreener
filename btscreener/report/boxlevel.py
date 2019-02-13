import plotly.graph_objs as go
import pandas as pd
import numpy as np


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