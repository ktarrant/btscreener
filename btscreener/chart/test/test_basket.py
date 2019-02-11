from btscreener.chart.basket import BasketStrategy
from btscreener.chart.backtest import run_backtest

from .fixtures import *

def test_backtest_summary(historical_data):
    summary = run_backtest(historical_data, BasketStrategy)
    print(summary)

    assert summary.low <= summary.open
    assert summary["low"] <= summary["close"]
    assert summary["low"] <= summary["high"]
    assert summary["high"] >= summary["open"]
    assert summary["high"] >= summary["close"]