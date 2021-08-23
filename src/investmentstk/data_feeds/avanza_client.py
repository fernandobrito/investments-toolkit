import requests
import requests_cache

from investmentstk.data_feeds.data_feed import DataFeed
from investmentstk.models.bar import BarSet, Bar
from investmentstk.utils.requests_cache import file_cache


class AvanzaClient(DataFeed):
    """
    A client to retrieve data from Avanza

    It uses the same public API used by their public price page.
    Example: https://www.avanza.se/aktier/om-aktien.html/5269/volvo-b
    """

    def retrieve_bars(self, source_id: str) -> BarSet:
        with requests_cache.enabled(backend=file_cache):
            response = requests.get(
                f"https://www.avanza.se/_api/price-chart/stock/{source_id}",
                params={"timePeriod": "one_year", "resolution": "day"},
            )

        bars: BarSet = set()
        data = response.json()

        for ohlc in data["ohlc"]:
            bars.add(Bar.from_avanza(ohlc))

        return bars
