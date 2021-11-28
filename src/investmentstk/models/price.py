from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """
    A generic (and minimalist) representation of the current price

    TODO: Clarify close vs last (includes after-hours) and that I usually want close
    """

    last: float
    change: float
    change_pct: float
