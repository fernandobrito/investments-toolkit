from dataclasses import dataclass
from typing import Optional, Mapping

from investmentstk.models.bar import BarSet
from investmentstk.models.source import Source, build_data_feed_from_source
from investmentstk.persistence import asset_cache


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
    def from_id(cls, fqn_id) -> "Asset":
        # Parse the fqn id
        source_value, source_id = fqn_id.split(":")
        source = Source(source_value)

        # Look at the cache, which is lazily loaded
        cache = asset_cache.AssetCache()
        cached_asset = cache.retrieve(fqn_id)

        if cached_asset:
            print("[Asset] Found in local cache")
            return cached_asset
        else:
            print("[Asset] Not found in cache. Retrieving from the source and adding to the remote cache")
            client = build_data_feed_from_source(source)
            name = client.retrieve_asset_name(source_id)

            asset = cls(source=Source(source_value), source_id=source_id, name=name)
            cache.add_asset(asset)

            return asset

    def retrieve_prices(self) -> BarSet:
        client = build_data_feed_from_source(self.source)
        return client.retrieve_bars(self.source_id)

    def to_dict(self) -> dict:
        return dict(source=self.source.name, source_id=self.source_id, name=self.name)

    def merge_dict(self, data: Mapping) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data: Mapping) -> "Asset":
        return cls(source=Source[data["source"]], source_id=data["source_id"], name=data["name"])
