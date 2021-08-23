from enum import Enum, auto
from typing import Type

from investmentstk.data_feeds.avanza_client import AvanzaClient
from investmentstk.data_feeds.cmc_client import CMCClient
from investmentstk.data_feeds.data_feed import DataFeed


class Source(Enum):
    """
    The supported sources. Each
    """

    Avanza = auto()
    CMC = auto()


SOURCES_DATA_FEED_MAP: dict[Source, Type[DataFeed]] = {
    Source.Avanza: AvanzaClient,
    Source.CMC: CMCClient,
}


def build_data_feed_from_source(source: Source) -> DataFeed:
    return SOURCES_DATA_FEED_MAP[source]()
