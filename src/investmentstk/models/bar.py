import pydantic
from datetime import datetime, time
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
