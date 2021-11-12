import os
from dataclasses import dataclass
from typing import Optional, Mapping

from google.cloud import firestore

from investmentstk.models import asset
from investmentstk.utils.logger import get_logger

GCP_PROJECT_NAME = os.environ.get("GCP_PROJECT_NAME")
CACHE_COLLECTION_NAME = "cache"
ASSETS_CACHE_DOCUMENT_NAME = "assets"

logger = get_logger()


@dataclass(init=False)
class AssetCache:
    """
    Keeps a local and a remote (using Google Firestore) cache of assets metadata
    """

    assets: Optional[Mapping[str, "asset.Asset"]]
    remote_db: firestore.Client
    assets_ref: firestore.DocumentReference

    __instance = None

    # Singleton pattern: https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    def __new__(cls):
        if AssetCache.__instance is None:
            logger.debug("Creating a new instance")
            AssetCache.__instance = object.__new__(cls)

            AssetCache.__instance.assets = None
            AssetCache.__instance.remote_db = firestore.Client(project=GCP_PROJECT_NAME)
            AssetCache.__instance.assets_ref = AssetCache.__instance.remote_db.collection(
                CACHE_COLLECTION_NAME
            ).document(ASSETS_CACHE_DOCUMENT_NAME)
        else:
            logger.debug("Reusing existing instance")

        return AssetCache.__instance

    def retrieve(self, asset_fqn_id: str) -> Optional["asset.Asset"]:
        """
        Retrieves an asset given its ID
        """
        if not self.is_enabled():
            logger.debug("Cache is disabled")
            return None

        if self.assets:
            logger.debug("Local cache is not empty")
            return self.assets.get(asset_fqn_id)

        logger.debug("Local cache is empty. Retrieving a copy from remote")
        remote_assets = self.assets_ref.get()

        if not remote_assets.exists:
            logger.debug("Remote cache is empty. Adding empty object")
            self.start_empty_cache()
            remote_assets = self.assets_ref.get()

        self.assets = {
            fqn_id: asset.Asset.from_dict(asset_dict) for fqn_id, asset_dict in remote_assets.to_dict().items()
        }

        logger.debug(f"Retrieved from remote with size {len(self.assets)}")

        return self.assets.get(asset_fqn_id)

    def add_asset(self, asset: "asset.Asset") -> None:
        """
        Adds an asset to the cache
        """
        if not self.is_enabled():
            logger.debug("Cache is disabled")
            return None

        self.assets_ref.update({firestore.Client.field_path(asset.fqn_id): asset.to_dict()})

        # Invalidates the cache
        logger.debug("Invalidating the local cache after modifying the remote cache")
        self.assets = None

    def start_empty_cache(self) -> None:
        self.assets_ref.create({})

    @staticmethod
    def is_enabled() -> bool:
        return GCP_PROJECT_NAME is not None
