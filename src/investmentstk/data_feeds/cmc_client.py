import os
from typing import ClassVar

import requests
import requests_cache

from investmentstk.data_feeds.data_feed import DataFeed
from investmentstk.models.bar import BarSet, Bar
from investmentstk.utils.requests_cache import file_cache


class CMCClient(DataFeed):
    """
    A client to retrieve data from CMC Markets

    It uses the same public API used by their public price page.
    Example: https://www.cmcmarkets.com/en-gb/instruments/sugar-raw-cash
    """

    # Public API key from just going to their website
    API_KEY: ClassVar[str] = os.environ["CMC_API_KEY"]

    def retrieve_bars(self, source_id: str) -> BarSet:
        with requests_cache.enabled(backend=file_cache):
            response = requests.get(
                f"https://oaf.cmcmarkets.com/instruments/prices/{source_id}/MONTH/11",
                params={"key": self.API_KEY},
            )

        bars: BarSet = set()
        data = response.json()

        for ohlc in data:
            bars.add(Bar.from_cmc(ohlc))

        return bars
