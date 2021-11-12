import pandas as pd
from pandas._testing import assert_series_equal

from investmentstk.formulas.average_true_range import average_true_range, average_true_range_trailing_stop
from investmentstk.models.barset import barset_to_ohlc_dataframe


def test_average_true_range(barset_volvo_2_months):
    dataframe = barset_to_ohlc_dataframe(barset_volvo_2_months)
    atr = average_true_range(dataframe, periods=7)

    # Manually checked on TradingView
    expected = pd.Series([3.16, 2.97, 2.91, 2.86, 2.73, 2.86, 3.02])

    assert_series_equal(atr.tail(7), expected, check_index=False, atol=0.01, check_freq=False)


def test_average_true_range_trailing_stop(barset_volvo_2_months):
    dataframe = barset_to_ohlc_dataframe(barset_volvo_2_months)
    stop_loss = average_true_range_trailing_stop(dataframe, periods=3, multiplier=3)

    # Manually checked on TradingView
    expected = pd.Series(
        [206.97, 205.14, 205.14, 203.05, 203.05, 203.05, 203.05, 203.05, 203.05, 203.05, 203.05, 203.05]
    )

    assert_series_equal(
        stop_loss.stop.tail(12), expected, check_index=False, check_names=False, atol=0.01, check_freq=False
    )
