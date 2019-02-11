import pytest
import time
import pandas as pd

from btscreener.collector.collect import create_row, run_collection

TEST_TICKERS = ["SPY", "QQQ", "IWM", "AAPL", "FB", "NFLX", "AMZN", "GOOGL"]


def test_create_row():
    start_time = time.perf_counter()
    row = create_row("AAPL")
    print("Row creation took {}s".format(time.perf_counter() - start_time))

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(row)

@pytest.mark.parametrize("pool_size", [0, 1, 4, 8])
def test_collect(pool_size):
    start_time = time.perf_counter()
    scan = run_collection(TEST_TICKERS, pool_size=pool_size)
    print("Collection took {}s".format(time.perf_counter() - start_time))

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(scan)