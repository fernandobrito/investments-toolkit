from typing import Optional

import requests
import requests_cache

from investmentstk.data_feeds.data_feed import DataFeed
from investmentstk.models.bar import BarSet, Bar
from investmentstk.persistence.requests_cache import file_cache


class AvanzaClient(DataFeed):
    """
    A client to retrieve data from Avanza

    A simpler implementation, and inspired by:
    * https://github.com/Qluxzz/avanza/blob/master/avanza/avanza.py
    * https://github.com/alrevuelta/avanzapy/blob/master/avanzapy/avanzapy.py
    """

    def retrieve_bars(self, source_id: str, instrument_type: Optional[str] = "stock") -> BarSet:
        """
        Uses the same public API used by their public price page.
        Example: https://www.avanza.se/aktier/om-aktien.html/5269/volvo-b

        :param source_id: the internal ID used in Avanza
        :param instrument_type:
        :return: a BarSet
        """
        with requests_cache.enabled(backend=file_cache):
            response = requests.get(
                f"https://www.avanza.se/_api/price-chart/{instrument_type}/{source_id}",
                params={"timePeriod": "one_year", "resolution": "day"},
            )

        bars: BarSet = set()
        data = response.json()

        for ohlc in data["ohlc"]:
            bars.add(Bar.from_avanza(ohlc))

        return bars

    def retrieve_asset_name(self, source_id: str, instrument_type: Optional[str] = "stock") -> str:
        """
        Retrieves the name of an asset

        :param source_id: the internal ID used in Avanza
        :param instrument_type:
        :return: the asset name (ticker)
        """
        with requests_cache.enabled(backend=file_cache):
            response = requests.get(f"https://www.avanza.se/_mobile/market/{instrument_type}/{source_id}")

            return response.json()["tickerSymbol"]
