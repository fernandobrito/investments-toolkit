from typing import Set

import pandas as pd

from investmentstk.models.bar import Bar

BarSet = Set[Bar]


def barset_from_csv_string(csv_string) -> BarSet:
    """
    Expected format:
    date,open,high,low,close

    without headers
    """
    barset = set()

    rows = csv_string.strip().split("\n")

    for row in rows:
        time, open, high, low, close = row.split(',')
        bar = Bar(time=time.strip(), open=open.strip(), high=high.strip(), low=low.strip(), close=close.strip())
        barset.add(bar)

    return barset


def barset_to_ohlc_dataframe(barset: BarSet) -> pd.DataFrame:
    """
    Converts a set of bars into a dataframe.
    The dataframe is indexed by date and each component of the bar (OHLC) becomes a column.

    Useful for calculations that require access to more than one component of an asset.
    """
    df = pd.DataFrame(barset)
    df = df.set_index("time")
    df.index = df.index.date
    df = df.sort_index()

    return df


def barset_to_single_column_dataframe(barset: BarSet, asset, column: str = "close") -> pd.DataFrame:
    """
    Converts a set of bars into a single column dataframe using `column` (like the close price) as the values.
    The dataframe is indexed by date and the column is named after the asset's name.

    Useful for converting barsets of several different assets into dataframes that will be merged
    together.
    """
    df = pd.DataFrame(barset)
    df = df.set_index("time")  # Assign the time as index
    df = df[[column]]  # Use only the close price
    df = df.rename(columns={column: asset.name})
    df.index = df.index.date
    df = df.sort_index()

    return df
