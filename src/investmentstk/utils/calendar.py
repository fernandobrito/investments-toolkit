import datetime

# From: https://stackoverflow.com/a/64885601/3950305
from investmentstk.data_feeds.data_feed import TimeResolution


def is_end_of_month(dt: datetime.datetime) -> bool:
    """
    Checks if the provided datetime is the last day of the month.
    """
    provided_month = dt.month
    month_of_next_day = (dt + datetime.timedelta(days=1)).month

    return True if month_of_next_day != provided_month else False


def days_to_next_month(dt: datetime.datetime) -> int:
    """
    Read as "how many days to the next month".

    If it's the last day of the month, it will return 1.
    If it's two days before, it will return 2, and so on.
    """
    provided_month = dt.month

    days_increment = 0
    is_same_month = True

    while is_same_month:
        days_increment += 1
        month_after_increment = (dt + datetime.timedelta(days=days_increment)).month
        is_same_month = month_after_increment == provided_month

    return days_increment


def round_day(dt: datetime.datetime):
    if dt.hour > 12:
        dt = dt + datetime.timedelta(days=1)
        return dt.replace(hour=0, minute=0)

    return dt


def is_saturday(dt: datetime.datetime) -> bool:
    """
    Checks if a datetime object is Saturday
    """
    weekday = dt.date().isoweekday()

    return weekday == 6


def is_sunday(dt: datetime.datetime) -> bool:
    """
    Checks if a datetime object is Sunday
    """
    weekday = dt.date().isoweekday()

    return weekday == 7


def is_weekend(dt) -> bool:
    """
    Checks if a datetime object is Saturday or Sunday
    """
    weekday = dt.date().isoweekday()

    return weekday == 6 or weekday == 7


def is_last_bar_closed(resolution: TimeResolution) -> bool:
    """
    On weekly resolution, returns true if it's weekend (no more trading will happen)
    On monthly resolution, returns true if there are no more week days left in the month
    (no more trading will happen): either it's the last day of the month and it's Sunday,
    or it's the last or the day before the last day of the month and it's Saturday.

    This is useful for calculating a offset on the bars for my stop loss strategy.
    During the week (eg: Wednesday), I want to show the stop loss of the previous bar.
    On Saturday or Sunday, when I usually update my stop losses, I want to see the stop loss
    taking into account the current bar, since it's "over"/closed.

    :param resolution:
    :return: True if there should be no more changes expected in the last price bar
    """

    now = datetime.datetime.utcnow()

    if resolution == TimeResolution.week:
        return is_weekend(now)
    else:
        if is_sunday(now) and days_to_next_month(now) == 1:
            return True
        elif is_saturday(now) and days_to_next_month(now) <= 2:
            return True

    return False
