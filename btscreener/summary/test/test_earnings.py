import datetime

import pytest
import pandas as pd

from btscreener.summary.earnings import make_earnings_summary


@pytest.fixture(scope="module")
def earnings_history(request):
    data = [
        {
            "actualEPS": 2.1,
            "consensusEPS": 2.02,
            "estimatedEPS": 2.02,
            "announceTime": "AMC",
            "numberOfEstimates": 14,
            "EPSSurpriseDollar": 0.08,
            "EPSReportDate": datetime.date(year=2017, month=5, day=2),
            "fiscalPeriod": "Q2 2017",
            "fiscalEndDate": datetime.date(year=2017, month=3, day=31),
            "yearAgo": 1.67,
            "yearAgoChangePercent": .30,
            "estimatedChangePercent": .28,
            "symbolId": 11
        },
        {
          "actualEPS": 3.36,
          "consensusEPS": 3.22,
          "estimatedEPS": 3.22,
          "announceTime": "AMC",
          "numberOfEstimates": 15,
          "EPSSurpriseDollar": 0.14,
          "EPSReportDate": datetime.date(year=2017, month=1, day=31),
          "fiscalPeriod": "Q1 2017",
          "fiscalEndDate": datetime.date(year=2016, month=12, day=31),
          "yearAgo": 1.67,
          "yearAgoChangePercent": .30,
          "estimatedChangePercent": .28,
          "symbolId": 11
        },
    ]
    return pd.DataFrame(data)


def test_earnings_summary(earnings_history):
    summary = make_earnings_summary(earnings_history)
    print(summary)
    assert summary.last_report_date == datetime.date(year=2017, month=5, day=2)
    assert summary.next_report_date > datetime.date.today()