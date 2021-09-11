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
import numpy as np
import pandas as pd
from pandas import DataFrame


def average_true_range(dataframe: DataFrame, periods: int = 14) -> pd.Series:
    """
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

    # TODO: I didn't bother parametizing this as I will always use SSMA
    # For SMA:  .rolling(periods).sum() / periods
    # For EMA:  .ewm(periods).mean()
    # For SSMA: .ewm(alpha=1 / periods, min_periods=periods, adjust=False).mean()
    atr = true_range.ewm(alpha=1 / periods, min_periods=periods, adjust=False).mean()

    return atr


def average_true_range_trailing_stop(dataframe: pd.DataFrame, periods: int = 14, multiplier: float = 3) -> pd.DataFrame:
    """
    Uses the ATR as a trailing stop.
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
