"""
"The average true range (ATR) is a technical analysis indicator, introduced by market technician J. Welles Wilder Jr.
The true range indicator is taken as the greatest of the following: current high less the current low; the absolute
value of the current high less the previous close; and the absolute value of the current low less the previous close.
The ATR is then a moving average, generally using 14 days, of the true ranges.

* The average true range (ATR) is a market volatility indicator used in technical analysis.
* It is typically derived from the 14-day simple moving average of a series of true range indicators.
* The ATR was originally developed for use in commodities markets but has since been applied to all
  types of securities."

From: https://www.investopedia.com/terms/a/atr.asp

Extra readings:
* https://www.tradingview.com/support/solutions/43000501823-average-true-range-atr/
* https://en.wikipedia.org/wiki/Average_true_range

= Which moving average?
TradingView uses RMA (Relative Moving Average) by default.
Wikipedia calls it smoothed moving average (SMMA) and links to
https://en.wikipedia.org/wiki/Moving_average#Modified_moving_average. This page also calls it
"modified moving average (MMA), running moving average (RMA), or smoothed moving average (SMMA)".
It is a special case of EMA where alpha = 1 / N.

"Because an exponential moving average (EMA) uses an exponentially weighted multiplier to give more weight to recent
prices, some believe it is a better indicator of a trend compared to a WMA or SMA."
https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp

Very nice summary and comparison between SMMA and EMA:
https://www.macroption.com/atr-period/

I ended up implementing both on TradingView to compare my strategy and I will stick to the
SSMA. The EMA felt too fast. Example: on the start of trends, SSMA gave me a larger stop (more cautious)
and after a long and strong in the trend, SSMA gave me tighter stops.

"""
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame

from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.asset import Asset
from investmentstk.models.barset import barset_to_ohlc_dataframe
from investmentstk.models.source import Source
from investmentstk.utils.calendar import is_weekend, days_to_next_month


def average_true_range(dataframe: DataFrame, periods: int = 14) -> pd.Series:
    """
    Calculates the ATR.

    See the documentation above for more information about the ATR indicator.

    Python implementations:
    * https://www.learnpythonwithrune.org/calculate-the-average-true-range-atr-easy-with-pandas-dataframes/
    * https://stackoverflow.com/questions/40256338/calculating-average-true-range-atr-on-ohlc-data-with-python
    """
    high_low = dataframe["high"] - dataframe["low"]
    high_close = np.abs(dataframe["high"] - dataframe["close"].shift())
    low_close = np.abs(dataframe["low"] - dataframe["close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    # TODO: I didn't bother parametrizing this as I will always use SSMA
    # Not 100% sure what adjust means. When True, it matches CMC sources. For Avanza,
    # it doesn't make much of a difference.
    # For best results with CMC and Trading View:
    # adjust=True, ignore_na=True

    # For SMA:  .rolling(periods).sum() / periods
    # For EMA:  .ewm(periods).mean()
    # For SSMA: .ewm(alpha=1 / periods, min_periods=periods, adjust=False).mean()
    atr = true_range.ewm(alpha=1 / periods, min_periods=periods, adjust=True, ignore_na=True).mean()

    return atr


def average_true_range_trailing_stop(dataframe: pd.DataFrame, periods: int = 14, multiplier: float = 3) -> pd.DataFrame:
    """
    Calculates a trailing stop using the ATR formula.
    If on "long" mode, never moves the stop down, and if on "short" mode, never move the stop up.

    Returns a copy of the original dataframe with extra columns (atr, stop_distance, stop).

    Similar to: https://www.tradingview.com/script/VP32b3aR-Average-True-Range-Trailing-Stops-Colored/
    """
    # Naive implementation. I'm not that familiar with pandas to come up with a more elegant solution
    # I could later try using numba to optimize it: https://stackoverflow.com/a/54420250/3950305

    dataframe = dataframe.copy()

    atr = average_true_range(dataframe, periods)

    # Add extra columns
    dataframe["atr"] = atr
    dataframe["stop_distance"] = atr * multiplier
    dataframe["stop"] = np.nan

    for index_i, index_df in enumerate(dataframe.index[1:], start=1):
        previous = dataframe.iloc[index_i - 1]
        current = dataframe.iloc[index_i]

        # No ATR available (first periods)
        if not current["atr"]:
            continue

        # If the current price is above the previous stop and the previous price was also above (no-cross),
        # take either the previous stop or the current one, whatever is higher
        # (when long, stop never goes down)
        if current["close"] > previous["stop"] and previous["close"] > previous["stop"]:
            new_stop = max(previous["stop"], current["close"] - current["stop_distance"])

        # If the current price is below the previous stop and the previous price was also below (no-cross),
        # take either the previous stop or the current one, whatever is lower
        # (when short, stop never goes up)
        elif current["close"] < previous["stop"] and previous["close"] < previous["stop"]:
            new_stop = min(previous["stop"], current["close"] + current["stop_distance"])

        # Otherwise, there was a cross. Check the direction and add the stop accordingly
        else:
            if current["close"] > previous["stop"]:
                new_stop = current["close"] - current["stop_distance"]
            else:
                new_stop = current["close"] + current["stop_distance"]

        # Store the stop value
        dataframe.at[index_df, "stop"] = new_stop

    return dataframe


def atr_stop_loss_from_asset(asset: Asset) -> pd.DataFrame:
    """
    Convenience function to calculate the ATR stop loss from an asset.

    Retrieves the barset with the appropriate resolution depending on the source
    and excludes the current bar if it's not the end of the week/month.

    :return: a BarSet dataframe with the ATR and ATR stop loss
    """

    now = datetime.utcnow()

    # TODO: Very specific to my trade system
    # Consider moving the default time resolution to a configuration file

    if asset.source == Source.CMC:
        multiplier = 3.0
        resolution = TimeResolution.week

        # If it's a weekend, take the current bar. Otherwise, the one before
        offset = None if is_weekend(now) else -1
    else:
        multiplier = 2.5
        resolution = TimeResolution.month

        # If it's the last 2 days of the month and a weekend, take the current bar.
        # Otherwise, the one before
        offset = None if is_weekend(now) and days_to_next_month(now) <= 2 else -1

    barset = asset.retrieve_bars(resolution=resolution)
    dataframe = barset_to_ohlc_dataframe(barset)
    dataframe = average_true_range_trailing_stop(dataframe, periods=21, multiplier=multiplier)
    return dataframe[0:offset]
