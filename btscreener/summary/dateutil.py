import datetime


def yield_period_ydays(dates, after=datetime.date.today(), period=91):
    """
    Used to guess the day of year (yday) for an event based on the dates of
    past events. The year is divided into windows of length 'period', and for
    each window a best guess of the day of year (yday) that corresponds to
    that window is yielded
    :param dates: dates corresponding to past events
    :type: list of datetime.date
    :param after: the years of the generated dates will be adjusted to make them
        less than this date, defaults to today
    :type: datetime.date
    :param period: number of days to divide the year into, defaults to quarters
    :type: int
    :returns: dates corresponding to when the events are likely to happen in the
        next year
    :type: datetime.date
    """
    ydays = [dt.timetuple().tm_yday for dt in dates]
    last_yday = 31  # prime this with a guess based on earnings season
    freq = int(365 / period)
    after_yday = after.timetuple().tm_yday
    for i in range(freq):
        yday_min = i * period
        yday_max = (yday_min + period) if (i < (freq-1)) else 366
        matches = [yday for yday in ydays
                   if ((yday >= yday_min) and (yday < yday_max))]
        if len(matches) == 0:
            # yield a guess based on the previous period's result (or if we
            # haven't processed any results yet, will use the existing guess)
            # TODO: if we have no data for Q1 but we do for later quarters, we
            # will make a 'wild' guess for Q1 when we could use later quarter
            # data to make a much better guess!
            yday = last_yday + period
        else:
            # yield the first match we get since we think it's the most recent
            yday = matches[0]

        year = after.year if (after_yday < yday) else (after.year + 1)
        yield (datetime.date(year, 1, 1) + datetime.timedelta(yday - 1))
