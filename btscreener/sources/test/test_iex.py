from btscreener.sources.iex import (
    load_historical, load_dividends, load_earnings
)


symbol = "aapl"


def test_load_historical():
    data = load_historical(symbol)
    print(data)
    assert len(data.index) > 0


def test_load_dividends():
    data = load_dividends(symbol)
    print(data)
    assert len(data.index) > 0


def test_load_earnings():
    data = load_earnings(symbol)
    print(data)
    assert len(data.index) > 0
