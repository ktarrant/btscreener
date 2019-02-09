import backtrader as bt
#
#
# class SummaryStrategy(bt.Strategy):
#
#     def __init__(self):
#         self.stad = SupertrendAD(self.data0)
#         self.td = TDSequential(self.data0)
#
#     def get_breakout(self):
#         was_below_resistance = (self.data0.close[-1] <
#                                 self.stad.lines.resistance[-1])
#         was_above_support = self.data0.close[-1] > self.stad.lines.support[-1]
#         is_above_resistance = (self.data0.close[0] >
#                                self.stad.lines.resistance[0])
#         is_below_support = self.data0.close[0] < self.stad.lines.support[0]
#         was_in_zone = was_below_resistance and was_above_support
#         is_long = is_above_resistance and was_in_zone
#         is_short = is_below_support and was_in_zone
#         return 1 if is_long else (-1 if is_short else 0)
#
#     def get_flip(self):
#         is_long = (self.stad.st.lines.trend[0] == 1) and (
#             self.stad.st.lines.trend[-1] != 1)
#         is_short = (self.stad.st.lines.trend[0] == -1) and (
#             self.stad.st.lines.trend[-1] != -1)
#         return 1 if is_long else (-1 if is_short else 0)
#
#     def get_summary(self):
#         wick_buy = not pd.isnull(self.stad.ad.lines.buy[0])
#         wick_sell = not pd.isnull(self.stad.ad.lines.sell[0])
#         return pd.Series(OrderedDict([
#             ("trend", float(self.stad.st.lines.trend[0])),
#             ("support", float(self.stad.lines.support[0])),
#             ("resistance", float(self.stad.lines.resistance[0])),
#             ("breakout", self.get_breakout()),
#             ("flip", self.get_flip()),
#             ("count", self.td.lines.count[0]),
#             ("reversal", self.td.lines.reversal[0]),
#             ("wick", 1 if wick_buy else (-1 if wick_sell else 0)),
#             ("prev_close", float(self.data0.close[-1])),
#             ("close", float(self.data0.close[0])),
#             ("open", float(self.data0.open[0])),
#             ("lastbar", self.data0.datetime.date()),
#         ]))