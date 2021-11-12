import datetime

import pytest

from investmentstk.utils.calendar import is_sunday, is_weekend, days_to_next_month


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
