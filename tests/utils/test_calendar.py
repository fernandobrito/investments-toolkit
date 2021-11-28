import datetime
import pytest

from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.utils.calendar import (
    is_sunday,
    is_weekend,
    days_to_next_month,
    is_end_of_month,
    round_day,
    is_saturday,
    is_last_bar_closed,
)


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2021, 1, 1), False),
        (datetime.datetime(2021, 2, 28), True),
        (datetime.datetime(2021, 10, 30), False),
        (datetime.datetime(2021, 10, 31), True),
        (datetime.datetime(2021, 12, 31), True),
    ],
)
def test_is_end_of_month(date, expected):
    assert is_end_of_month(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2021, 10, 28), 4),
        (datetime.datetime(2021, 10, 29), 3),
        (datetime.datetime(2021, 10, 30), 2),
        (datetime.datetime(2021, 10, 31), 1),
        (datetime.datetime(2021, 11, 1), 30),
    ],
)
def test_days_to_next_month(date, expected):
    assert days_to_next_month(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2021, 10, 28, 0, 0, 0), datetime.datetime(2021, 10, 28, 0, 0, 0)),
        (datetime.datetime(2021, 10, 29, 4, 3, 2), datetime.datetime(2021, 10, 29, 0, 0, 0)),
        (datetime.datetime(2021, 10, 29, 16, 3, 2), datetime.datetime(2021, 10, 30, 0, 0, 0)),
    ],
)
def test_round_day(date, expected):
    assert round_day(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2021, 10, 23), True),
        (datetime.datetime(2021, 10, 24), False),
        (datetime.datetime(2021, 10, 25), False),
        (datetime.datetime(2021, 10, 26), False),
        (datetime.datetime(2021, 10, 27), False),
        (datetime.datetime(2021, 10, 28), False),
        (datetime.datetime(2021, 10, 29), False),
        (datetime.datetime(2021, 10, 30), True),
    ],
)
def test_is_saturday(date, expected):
    assert is_saturday(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2021, 10, 24), True),
        (datetime.datetime(2021, 10, 25), False),
        (datetime.datetime(2021, 10, 26), False),
        (datetime.datetime(2021, 10, 27), False),
        (datetime.datetime(2021, 10, 28), False),
        (datetime.datetime(2021, 10, 29), False),
        (datetime.datetime(2021, 10, 30), False),
        (datetime.datetime(2021, 10, 31), True),
        (datetime.datetime(2021, 11, 1), False),
    ],
)
def test_is_sunday(date, expected):
    assert is_sunday(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2021, 10, 24), True),
        (datetime.datetime(2021, 10, 25), False),
        (datetime.datetime(2021, 10, 26), False),
        (datetime.datetime(2021, 10, 27), False),
        (datetime.datetime(2021, 10, 28), False),
        (datetime.datetime(2021, 10, 29), False),
        (datetime.datetime(2021, 10, 30), True),
        (datetime.datetime(2021, 10, 31), True),
        (datetime.datetime(2021, 11, 1), False),
    ],
)
def test_is_weekend(date, expected):
    assert is_weekend(date) == expected


@pytest.mark.parametrize(
    "resolution, date, expected",
    [
        (TimeResolution.week, datetime.datetime(2021, 11, 25), False),  # Thursday
        (TimeResolution.week, datetime.datetime(2021, 11, 26), False),  # Friday
        (TimeResolution.week, datetime.datetime(2021, 11, 27), True),  # Saturday
        (TimeResolution.week, datetime.datetime(2021, 11, 28), True),  # Sunday
        (TimeResolution.month, datetime.datetime(2021, 10, 1), False),
        (TimeResolution.month, datetime.datetime(2021, 10, 30), True),  # Saturday, no more business days in the month
        (TimeResolution.month, datetime.datetime(2021, 10, 31), True),  # Sunday, no more business days in the month
    ],
)
def test_is_last_bar_closed(resolution, date, expected):
    assert is_last_bar_closed(resolution, date) == expected
