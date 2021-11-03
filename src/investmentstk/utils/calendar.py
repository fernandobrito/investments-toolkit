import datetime


# From: https://stackoverflow.com/a/64885601/3950305
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
