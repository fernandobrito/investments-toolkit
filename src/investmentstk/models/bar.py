from datetime import datetime
from typing import Mapping

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Bar:
    """
    A generic representation of a price bar
    """

    time: datetime
    open: float
    high: float
    low: float
    close: float

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
