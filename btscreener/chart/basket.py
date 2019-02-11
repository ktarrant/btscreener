from collections import OrderedDict

import backtrader as bt
import pandas as pd
import numpy as np

from .adbreakout import ADBreakout
from .tdcount import TDSequential


class BasketStrategy(bt.Strategy):

    def __init__(self):
        self.indicators = OrderedDict([
            ("stad", ADBreakout()),
            ("td", TDSequential()),
        ])

    @staticmethod
    def get_min_period():
        # TODO: Compute based on self.indicators ?
        return "3m"

    def yield_summary(self):
        for field_name in self.data.lines.getlinealiases():
            line = getattr(self.data.lines, field_name)
            yield (field_name, line[0])
            yield ("prev_" + field_name, line[-1])
        for indicator_name, indicator in self.indicators.items():
            for line_name in indicator.lines.getlinealiases():
                field_name = "{}_{}".format(indicator_name, line_name)
                line = getattr(indicator.lines, line_name)
                yield (field_name, line[0])
                yield ("prev_" + field_name, line[-1])