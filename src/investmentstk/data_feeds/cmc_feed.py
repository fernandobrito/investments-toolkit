import os
import requests
from datetime import datetime, timedelta
from typing import ClassVar, Optional, Mapping

from investmentstk.data_feeds.data_feed import DataFeed, TimeResolution
from investmentstk.models.bar import Bar
from investmentstk.models.barset import BarSet
from investmentstk.models.price import Price
from investmentstk.persistence.requests_cache import requests_cache_configured


class CMCFeed(DataFeed):
    """
    A client to retrieve data from CMC Markets
    """

    # Public API key from just going to their website
    API_KEY: ClassVar[str] = os.environ["CMC_API_KEY"]

    @requests_cache_configured()
    def _retrieve_bars(
        self, source_id: str, *, resolution: TimeResolution = TimeResolution.day, instrument_type: Optional[str] = None
    ) -> BarSet:
        """
        Uses the same public API used by their public price page.
        Example: https://www.cmcmarkets.com/en-gb/instruments/sugar-raw-cash

        For daily interval, the maximum allowed number of months is 6.
        """
        if resolution == TimeResolution.day:
            response = requests.get(
                f"https://oaf.cmcmarkets.com/instruments/prices/{source_id}/MONTH/6",
                params={"key": self.API_KEY},
            )
        elif resolution == TimeResolution.week:
            response = requests.get(
                f"https://oaf.cmcmarkets.com/instruments/prices/{source_id}/YEAR/2",
                params={"key": self.API_KEY},
            )
        else:
            raise ValueError(f"{resolution} resolution not supported for {self.__class__.__name__} source")

        response.raise_for_status()
        data = response.json()

        bars: BarSet = set()

        for ohlc in data:
            bars.add(self._ohlc_to_bar(ohlc, resolution))

        return bars

    @requests_cache_configured()
    def retrieve_asset_name(self, source_id: str, instrument_type: Optional[str] = None) -> str:
        response = requests.get(
            f"https://oaf.cmcmarkets.com/json/instruments/{source_id}_gb.json",
            params={"key": self.API_KEY},
        )
        response.raise_for_status()

        return response.json()["name"]

    def retrieve_price(self, source_id: str, instrument_type: Optional[str] = None) -> Price:
        response = requests.get(
            f"https://oaf.cmcmarkets.com//instruments/price/{source_id}",
            params={"key": self.API_KEY},
        )
        response.raise_for_status()

        data = response.json()
        mid_price = (data["buy"] + data["sell"]) / 2

        return Price(last=mid_price, change=data["movement_point"], change_pct=data["movement_percentage"])

    @classmethod
    def _ohlc_to_bar(cls, ohlc: Mapping, resolution: TimeResolution) -> Bar:
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

        # CMC starts the week on Sunday, but most other places do on Monday
        if resolution == TimeResolution.week:
            ts = ts + timedelta(days=1)

        return Bar(
            time=ts,
            open=ohlc["o"],
            high=ohlc["h"],
            low=ohlc["l"],
            close=ohlc["c"],
        )
