import pytest
import pickle

from btscreener.report.screener import make_screener_row, make_screener_table

@pytest.fixture(scope="module")
def backtest(request):
    fn = request.config.getoption("--collection")
    with open(fn, "rb") as fobj:
        df = pickle.load(fobj)
    return df

def test_screener_row(backtest):
    symbol = backtest.index[0]
    row = make_screener_row(backtest.loc[symbol])
    print(row)

def test_screener_table(backtest):
    url = make_screener_table("dev", backtest)
    print(url)