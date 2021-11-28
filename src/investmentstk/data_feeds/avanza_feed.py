from zoneinfo import ZoneInfo

import requests
from datetime import datetime
from typing import Optional, Mapping

from investmentstk.data_feeds.data_feed import DataFeed, TimeResolution
from investmentstk.models.bar import Bar
from investmentstk.models.barset import BarSet
from investmentstk.models.price import Price
from investmentstk.persistence.requests_cache import requests_cache_configured

TIME_RESOLUTION_TO_AVANZA_API_RESOLUTION_MAP = {
    TimeResolution.day: "day",
    TimeResolution.week: "week",
    TimeResolution.month: "month",
}

TIME_RESOLUTION_TO_AVANZA_API_TIME_RANGE_MAP = {
    TimeResolution.day: "one_year",
    TimeResolution.week: "three_years",
    TimeResolution.month: "infinity",
}


class AvanzaFeed(DataFeed):
    """
    A client to retrieve data from Avanza

    A simpler implementation, and inspired by:
    * https://github.com/Qluxzz/avanza/blob/master/avanza/avanza.py
    * https://github.com/alrevuelta/avanzapy/blob/master/avanzapy/avanzapy.py
    """

    @requests_cache_configured()
    def _retrieve_bars(
        self,
        source_id: str,
        *,
        resolution: TimeResolution = TimeResolution.day,
        instrument_type: Optional[str] = "stock",
    ) -> BarSet:
        """
        Uses the same public API used by their public price page.
        Example: https://www.avanza.se/aktier/om-aktien.html/5269/volvo-b

        :param source_id: the internal ID used in Avanza
        :param instrument_type:
        :return: a BarSet
        """
        response = requests.get(
            f"https://www.avanza.se/_api/price-chart/{instrument_type}/{source_id}",
            params={
                "timePeriod": TIME_RESOLUTION_TO_AVANZA_API_TIME_RANGE_MAP[resolution],
                "resolution": TIME_RESOLUTION_TO_AVANZA_API_RESOLUTION_MAP[resolution],
            },
        )
        response.raise_for_status()

        bars: BarSet = set()
        data = response.json()

        for ohlc in data["ohlc"]:
            bars.add(self._ohlc_to_bar(ohlc))

        return bars

    @requests_cache_configured()
    def retrieve_asset_name(self, source_id: str, instrument_type: Optional[str] = "stock") -> str:
        """
        Retrieves the name of an asset

        :param source_id: the internal ID used in Avanza
        :param instrument_type:
        :return: the asset name (ticker)
        """
        response = requests.get(f"https://www.avanza.se/_mobile/market/{instrument_type}/{source_id}")
        response.raise_for_status()

        return response.json()["tickerSymbol"]

    def retrieve_price(self, source_id: str, instrument_type: Optional[str] = "stock") -> Price:
        response = requests.get(f"https://www.avanza.se/_mobile/market/{instrument_type}/{source_id}")
        response.raise_for_status()

        data = response.json()

        return Price(last=data["lastPrice"], change=data["change"], change_pct=data["changePercent"])

    @classmethod
    def _ohlc_to_bar(cls, ohlc: Mapping) -> Bar:
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

        return Bar(
            time=datetime.fromtimestamp(ohlc["timestamp"] / 1000, tz=local_tz).replace(tzinfo=None),
            open=ohlc["open"],
            high=ohlc["high"],
            low=ohlc["low"],
            close=ohlc["close"],
        )
