from pandas import Timestamp

from investmentstk.figures.candlestick import date_gaps
from investmentstk.models.barset import barset_from_csv_string, barset_to_ohlc_dataframe


def test_date_gaps():
    ohlc = """
        2021-07-01,207.3,208.35,205.9,207.9
        2021-07-02,208.35,209.1,206.1,206.1
        2021-07-05,208.2,209.95,205.45,209.75
        2021-07-06,210.0,211.85,208.1,208.15
    """

    barset = barset_from_csv_string(ohlc)
    dataframe = barset_to_ohlc_dataframe(barset)

    result = date_gaps(dataframe)

    assert result == {Timestamp(2021, 7, 3), Timestamp(2021, 7, 4)}
