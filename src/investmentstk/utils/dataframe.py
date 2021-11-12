import pandas as pd
from pandas.tseries.frequencies import to_offset

RESAMPLE_LOGIC = {"open": "first", "high": "max", "low": "min", "close": "last"}


def convert_to_pct_change(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Iterates over all columns of a dataframe and converts them to
    percentage changes between the current and a prior element.
    Useful to convert asset prices to % changes before calculating
    the correlation between different assets.

    :param dataframe: input dataframe
    :return: a copy of the dataframe
    """
    dataframe = dataframe.copy()
    dataframe = dataframe.sort_index()

    for column in dataframe:
        dataframe[column] = dataframe[column].pct_change(fill_method=None)

    return dataframe


def merge_dataframes(dataframes: list[pd.DataFrame], join: str = "outer") -> pd.DataFrame:
    """
    Performs a join of a list of dataframes.

    :param dataframes: a list of dataframes
    :param join: the type of join
    :return:
    """
    dataframe = pd.concat(dataframes, axis="columns", join=join)

    return dataframe


def convert_daily_ohlc_to_weekly(dataframe: pd.DataFrame) -> pd.DataFrame:
    # From:
    # https://stackoverflow.com/questions/34597926/converting-daily-stock-data-to-weekly-based-via-pandas-in-python
    dataframe = dataframe.resample("W").apply(RESAMPLE_LOGIC)

    offset = pd.Timedelta(days=-6)
    dataframe.index = dataframe.index + to_offset(offset)

    return dataframe


def convert_daily_ohlc_to_monthly(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.resample("M").apply(RESAMPLE_LOGIC)
    dataframe.index = dataframe.index + to_offset(pd.tseries.offsets.MonthBegin(n=-1))

    return dataframe
