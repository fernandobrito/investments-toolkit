import os
from typing import ClassVar, Optional

import requests

from investmentstk.data_feeds.data_feed import DataFeed
from investmentstk.models.bar import BarSet, Bar
from investmentstk.models.price import Price
from investmentstk.persistence.requests_cache import requests_cache_configured


class CMCClient(DataFeed):
    """
    A client to retrieve data from CMC Markets
    """

    # Public API key from just going to their website
    API_KEY: ClassVar[str] = os.environ["CMC_API_KEY"]

    @requests_cache_configured()
    def retrieve_bars(self, source_id: str, instrument_type: Optional[str] = None) -> BarSet:
        """
        Uses the same public API used by their public price page.
        Example: https://www.cmcmarkets.com/en-gb/instruments/sugar-raw-cash

        For daily interval, the maximum allowed number of months is 6.

        :param source_id:
        :param instrument_type:
        :return:
        """
        response = requests.get(
            f"https://oaf.cmcmarkets.com/instruments/prices/{source_id}/MONTH/6",
            params={"key": self.API_KEY},
        )
        response.raise_for_status()

        bars: BarSet = set()
        data = response.json()

        for ohlc in data:
            bars.add(Bar.from_cmc(ohlc))

        return bars

    @requests_cache_configured()
    def retrieve_asset_name(self, source_id: str, instrument_type: Optional[str] = "stock") -> str:
        response = requests.get(
            f"https://oaf.cmcmarkets.com/json/instruments/{source_id}_gb.json",
            params={"key": self.API_KEY},
        )
        response.raise_for_status()

        return response.json()["name"]

    @requests_cache_configured(hours=0.5)
    def retrieve_price(self, source_id: str, instrument_type: Optional[str] = "stock") -> Price:
        response = requests.get(
            f"https://oaf.cmcmarkets.com//instruments/price/{source_id}",
            params={"key": self.API_KEY},
        )
        response.raise_for_status()

        data = response.json()
        mid_price = (data["buy"] + data["sell"]) / 2

        return Price(last=mid_price, change=data["movement_point"], change_pct=data["movement_percentage"])
