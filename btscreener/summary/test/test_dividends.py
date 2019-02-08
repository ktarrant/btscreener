import datetime

import pytest
import pandas as pd

from btscreener.summary.dividends import make_dividend_summary


@pytest.fixture(scope="module")
def dividend_history():
    data = [
        {
            "exDate": datetime.date(year=2017, month=8, day=10),
            "paymentDate": datetime.date(year=2017, month=8, day=17),
            "recordDate": datetime.date(year=2017, month=8, day=14),
            "declaredDate": datetime.date(year=2017, month=8, day=1),
            "amount": 0.63,
            "type": "Dividend income",
            "qualified": "Q",
        }
    ]
    return pd.DataFrame(data)


def test_dividend_summary(dividend_history):
    summary = make_dividend_summary(dividend_history)
    print(summary)
    assert summary.last_ex_date == datetime.date(year=2017, month=8, day=10)
    assert summary.last_dividend_amount == 0.63
    assert summary.dividend_period == 91
    assert summary.next_ex_date > datetime.date.today()
