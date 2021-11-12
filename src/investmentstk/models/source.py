from enum import Enum
from typing import Type

from investmentstk.data_feeds import AvanzaFeed, CMCFeed, DataFeed, KrakenFeed


class Source(str, Enum):
    """
    The supported sources. Each source has a short name used for creating our
    unique asset ids.
    """

    Avanza = "AV"
    CMC = "CMC"
    Kraken = "KR"
    Nordnet = "NN"


SOURCES_DATA_FEED_MAP: dict[Source, Type[DataFeed]] = {
    Source.Avanza: AvanzaFeed,
    Source.CMC: CMCFeed,
    Source.Kraken: KrakenFeed,
    Source.Nordnet: AvanzaFeed,  # TODO: Not very elegant and very specific to my needs
}


def build_data_feed_from_source(source: Source) -> DataFeed:
    """
    Returns an instance of the `DataFeed` implementation associated
    with the given `Source`.

    :param source:
    :return:
    """
    return SOURCES_DATA_FEED_MAP[source]()
