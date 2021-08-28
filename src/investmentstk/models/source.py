from enum import Enum
from typing import Type

from investmentstk.data_feeds.avanza_client import AvanzaClient
from investmentstk.data_feeds.cmc_client import CMCClient
from investmentstk.data_feeds.data_feed import DataFeed


class Source(str, Enum):
    """
    The supported sources. Each source has a short name used for creating our
    unique asset ids.
    """

    Avanza = "AV"
    Nordnet = "NN"
    CMC = "CMC"


SOURCES_DATA_FEED_MAP: dict[Source, Type[DataFeed]] = {
    Source.Avanza: AvanzaClient,
    Source.Nordnet: AvanzaClient,  # TODO: Not very elegant and very specific to my needs
    Source.CMC: CMCClient,
}


def build_data_feed_from_source(source: Source) -> DataFeed:
    """
    Returns an instance of the `DataFeed` implementation associated
    with the given `Source`.

    :param source:
    :return:
    """
    return SOURCES_DATA_FEED_MAP[source]()
