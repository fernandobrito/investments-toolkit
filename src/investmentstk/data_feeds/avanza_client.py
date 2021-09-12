from typing import Optional

import requests

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


class AvanzaClient(DataFeed):
    """
    A client to retrieve data from Avanza

    A simpler implementation, and inspired by:
    * https://github.com/Qluxzz/avanza/blob/master/avanza/avanza.py
    * https://github.com/alrevuelta/avanzapy/blob/master/avanzapy/avanzapy.py
    """

    @requests_cache_configured()
    def retrieve_bars(
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
            bars.add(Bar.from_avanza(ohlc))

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

    @requests_cache_configured(hours=0.5)
    def retrieve_price(self, source_id: str, instrument_type: Optional[str] = "stock") -> Price:
        response = requests.get(f"https://www.avanza.se/_mobile/market/{instrument_type}/{source_id}")
        response.raise_for_status()

        data = response.json()

        return Price(last=data["lastPrice"], change=data["change"], change_pct=data["changePercent"])
