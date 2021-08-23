from typing import NamedTuple

from investmentstk.models.bar import BarSet
from investmentstk.models.source import Source, build_data_feed_from_source


class Asset(NamedTuple):
    """
    A generic representation of an asset in a data feed
    """

    name: str
    source: Source
    source_id: str

    def retrieve_prices(self) -> BarSet:
        client = build_data_feed_from_source(self.source)
        return client.retrieve_bars(self.source_id)
