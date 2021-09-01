import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from investmentstk.models.asset import Asset
from investmentstk.models.bar import Bar
from investmentstk.models.barset import barset_to_ohlc_dataframe, barset_to_single_column_dataframe, BarSet, \
    barset_from_csv_string
from investmentstk.models.source import Source


@pytest.fixture
def asset():
    return Asset(source=Source.Avanza, name='ASSET', source_id='1234')


@pytest.fixture
def barset_upward_trend() -> BarSet:
    csv_string = """
    2021-01-01 00:00:00,10,12,9,11
    2021-01-02 00:00:00,11,13,10,12
    2021-01-03 00:00:00,12,14,11,13
    2021-01-04 00:00:00,13,15,12,14
    """

    return barset_from_csv_string(csv_string)


def test_barset_from_csv_string(barset_upward_trend):
    barset = set([
        Bar(time='2021-01-01 00:00:00', open=10, close=11, low=9, high=12),
        Bar(time='2021-01-02 00:00:00', open=11, close=12, low=10, high=13),
        Bar(time='2021-01-03 00:00:00', open=12, close=13, low=11, high=14),
        Bar(time='2021-01-04 00:00:00', open=13, close=14, low=12, high=15),
    ])

    assert barset == barset_upward_trend


def test_barset_to_ohlc_dataframe(barset_upward_trend):
    dataframe = barset_to_ohlc_dataframe(barset_upward_trend)

    expected_data = dict(
        open=[10.0, 11.0, 12.0, 13.0],
        close=[11.0, 12.0, 13.0, 14.0],
        low=[9.0, 10.0, 11.0, 12.0],
        high=[12.0, 13.0, 14.0, 15.0]
    )
    expected = pd.DataFrame(expected_data,
                            index=['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04'])
    expected.index = pd.to_datetime(expected.index).date

    # Fine that the order of the columns are different (check_like)
    assert_frame_equal(dataframe, expected, check_like=True)


def test_barset_to_single_column_dataframe(asset, barset_upward_trend):
    dataframe = barset_to_single_column_dataframe(barset_upward_trend, asset)
    expected = pd.DataFrame({asset.name: [11.0, 12.0, 13.0, 14.0]},
                            index=['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04'])
    expected.index = pd.to_datetime(expected.index).date

    assert_frame_equal(dataframe, expected)
