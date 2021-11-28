from operator import attrgetter
from typing import Set

import pandas as pd

from investmentstk.models.bar import Bar

BarSet = Set[Bar]


def barset_from_csv_string(csv_string: str) -> BarSet:
    """
    Expected format:
    date,open,high,low,close

    without headers
    """
    barset = set()

    rows = csv_string.strip().split("\n")

    for row in rows:
        time, open, high, low, close = [value.strip() for value in row.split(",")]
        bar = Bar(time=time, open=open, high=high, low=low, close=close)  # type: ignore
        barset.add(bar)

    return barset


def barset_to_ohlc_dataframe(barset: BarSet) -> pd.DataFrame:
    """
    Converts a set of bars into a dataframe.
    The dataframe is indexed by date and each component of the bar (OHLC) becomes a column.

    Useful for calculations that require access to more than one component of an asset.
    """
    dataframe = pd.DataFrame(barset)
    return format_ohlc_dataframe(dataframe)


def format_ohlc_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Useful for dependencies that already provide OHLC data in a dataframe.
    Converts it to our format.
    """
    dataframe = dataframe.set_index(pd.DatetimeIndex(dataframe["time"]))
    dataframe = dataframe.drop("time", axis=1)
    dataframe = dataframe.sort_index()

    return dataframe


def ohlc_to_single_column_dataframe(dataframe: pd.DataFrame, asset, column: str = "close") -> pd.DataFrame:
    """
    Converts a set of bars into a single column dataframe using `column` (like the close price) as the values.
    The dataframe is indexed by date and the column is named after the asset's name.

    Useful for converting barsets of several different assets into dataframes that will be merged
    together.
    """
    dataframe = dataframe[[column]]  # Use only the close price
    dataframe = dataframe.rename(columns={column: asset.name})
    dataframe.index = dataframe.index.date
    dataframe = dataframe.sort_index()

    return dataframe


def barset_to_sorted_list(barset: BarSet) -> list[Bar]:
    return sorted(list(barset), key=attrgetter("time"))
