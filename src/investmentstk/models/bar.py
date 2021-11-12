from datetime import datetime, time, timedelta
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

import pydantic
from pydantic import validator
from pydantic.dataclasses import dataclass
from pydantic.datetime_parse import parse_datetime, parse_date


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
        """
        Converts a bar OHLC representation from Avanza into our
        representation.
        """

        """
        Timestamps from Avanza come in CET time. When retrieving daily bars,
        a bar for the close of the day 2021-09-03 will be 1630620000000,
        which is "Friday, September 3, 2021 12:00:00 AM GMT+02:00 DST".
        If I treat that as a UTC timestamp, I get "Thursday, September 2, 2021 10:00:00 PM",
        which is the day before.

        However, I had issues with pandas when I tried to create a dataframe
        with a timezone aware datetime, so I drop the timezone info.
        """

        local_tz = ZoneInfo("Europe/Stockholm")

        return cls(
            time=datetime.fromtimestamp(ohlc["timestamp"] / 1000, tz=local_tz).replace(tzinfo=None),
            open=ohlc["open"],
            high=ohlc["high"],
            low=ohlc["low"],
            close=ohlc["close"],
        )

    @classmethod
    def from_cmc(cls, ohlc: Mapping) -> "Bar":
        """
        Converts a bar OHLC representation from CMC Markets into our
        representation.

        I have had issues before with timezone and date misalignment with this data feed.
        Example: when retrieving daily bars, I would get timestamps starting at 9pm or 10pm on the day before,
        depending if DST is ongoing or not.
        """

        # This logic works both for daily and weekly resolution
        ts = datetime.strptime(ohlc["t"], "%Y-%m-%dT%H:%M:%S%z")

        if ts.hour > 12:
            ts = ts + timedelta(days=1)
            ts = ts.replace(hour=0, minute=0)

        return cls(
            time=ts,
            open=ohlc["o"],
            high=ohlc["h"],
            low=ohlc["l"],
            close=ohlc["c"],
        )

    @classmethod
    def from_kraken(cls, ohlc: Sequence) -> "Bar":
        """
        converts a bar OHLC representation from Kraken into our
        representation.
        """
        return cls(
            time=datetime.fromtimestamp(ohlc[0]),
            open=float(ohlc[1]),
            high=float(ohlc[2]),
            low=float(ohlc[3]),
            close=float(ohlc[4])
        )

    @validator("time", pre=True)
    def parse_time(cls, value):
        """
        By default, dates (2021-09-02) are not accepted by pydantic in datetime.
        This custom pre-validator checks if the value is a date before returning an error.

        If it's not a datetime and not a date, passes the original value through so
        the real validation will kick-in.
        """
        try:
            return parse_datetime(value)
        except pydantic.errors.DateTimeError:
            try:
                # Creates a datetime from a date with time 00:00:00
                return datetime.combine(parse_date(value), time())
            except pydantic.errors.DateError:
                return value
