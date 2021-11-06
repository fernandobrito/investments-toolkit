from dataclasses import dataclass
from typing import Optional, Mapping

from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.barset import BarSet
from investmentstk.models.source import Source, build_data_feed_from_source
from investmentstk.persistence import asset_cache
from investmentstk.utils.logger import get_logger, logger_autobind_from_args

logger = get_logger()


@dataclass(frozen=True)
class Asset:
    """
    A generic representation of an asset in a data feed
    """

    source: Source
    source_id: str
    name: Optional[str] = None

    @property
    def fqn_id(self):
        return f"{self.source.value}:{self.source_id}"

    @classmethod
    @logger_autobind_from_args(asset_id="fqn_id")
    def from_id(cls, fqn_id: str) -> "Asset":
        # Parse the fqn id
        source, source_id = cls.parse_fqn_id(fqn_id)

        logger.info("Initializing")

        # Look at the cache, which is lazily loaded
        cache = asset_cache.AssetCache()
        cached_asset = cache.retrieve(fqn_id)

        if cached_asset:
            logger.debug("Found in local cache")
            return cached_asset
        else:
            logger.debug("Not found in cache. Retrieving from the source and adding to the remote cache")
            client = build_data_feed_from_source(source)
            name = client.retrieve_asset_name(source_id)

            asset = cls(source=source, source_id=source_id, name=name)
            cache.add_asset(asset)

            return asset

    def retrieve_bars(self, resolution: TimeResolution = TimeResolution.day) -> BarSet:
        client = build_data_feed_from_source(self.source)
        return client.retrieve_bars(self.source_id, resolution=resolution)

    def to_dict(self) -> dict:
        return dict(source=self.source.name, source_id=self.source_id, name=self.name)

    def merge_dict(self, data: Mapping) -> None:
        for key, value in data.items():
            object.__setattr__(self, key, value)

    @classmethod
    def from_dict(cls, data: Mapping) -> "Asset":
        return cls(source=Source[data["source"]], source_id=data["source_id"], name=data["name"])

    @staticmethod
    def parse_fqn_id(fqn_id: str) -> tuple[Source, str]:
        """
        Parses a FQN ID into a source and source_id.
        """
        source_value, source_id = fqn_id.split(":")
        source = Source(source_value)

        return source, source_id
