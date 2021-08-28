from dataclasses import dataclass
from datetime import datetime
from typing import Set, Mapping

import pandas as pd

BarSet = Set["Bar"]


@dataclass(frozen=True)
class Bar:
    """
    A generic representation of a price bar
    """

    time: datetime
    open: float
    close: float
    high: float
    low: float

    @classmethod
    def from_avanza(cls, ohlc: Mapping) -> "Bar":
        return cls(
            time=datetime.utcfromtimestamp(ohlc["timestamp"] / 1000),
            open=ohlc["open"],
            close=ohlc["close"],
            high=ohlc["high"],
            low=ohlc["low"],
        )

    @classmethod
    def from_cmc(cls, ohlc: Mapping) -> "Bar":
        return cls(
            time=datetime.strptime(ohlc["t"], "%Y-%m-%dT%H:%M:%S%z"),
            open=ohlc["o"],
            close=ohlc["c"],
            high=ohlc["h"],
            low=ohlc["l"],
        )


def barset_to_dataframe(barset: BarSet, asset, column: str = "close") -> pd.DataFrame:
    df = pd.DataFrame(barset)
    df = df.set_index("time")  # Assign the time as index
    df = df[[column]]  # Use only the close price
    df = df.rename(columns={column: asset.name})
    df.index = df.index.date

    return df
