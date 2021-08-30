from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """
    A generic (and minimalist) representation of the current price
    """

    last: float
    change: float
    change_pct: float
