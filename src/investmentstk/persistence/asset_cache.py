import os

from google.cloud import firestore

from investmentstk.models import asset
from investmentstk.utils.logger import get_logger

GCP_PROJECT = os.environ["GCP_PROJECT_NAME"]
CACHE_COLLECTION_NAME = "cache"
ASSETS_CACHE_DOCUMENT_NAME = "assets"

logger = get_logger()


class AssetCache:
    __instance = None

    # Singleton pattern: https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    def __new__(cls):
        if AssetCache.__instance is None:
            logger.debug("[AssetCache] Creating a new instance of AssetCache")
            AssetCache.__instance = object.__new__(cls)

            AssetCache.__instance.assets = None
            AssetCache.__instance.remote_db = firestore.Client(project=GCP_PROJECT)
            AssetCache.__instance.assets_ref = AssetCache.__instance.remote_db.collection(
                CACHE_COLLECTION_NAME
            ).document(ASSETS_CACHE_DOCUMENT_NAME)
        else:
            logger.debug("[AssetCache] Reusing existing AssetCache")

        return AssetCache.__instance

    def retrieve(self, asset_fqn_id):
        if self.assets:
            logger.debug("[AssetCache] Local cache is not empty")
            return self.assets.get(asset_fqn_id)

        logger.debug("[AssetCache] Local cache is empty. Retrieving a copy from remote")
        remote_assets = self.assets_ref.get()

        if not remote_assets.exists:
            logger.debug("[AssetCache] Remote cache is empty. Adding empty object")
            self.start_empty_cache()
            remote_assets = self.assets_ref.get()

        self.assets = {
            fqn_id: asset.Asset.from_dict(asset_dict) for fqn_id, asset_dict in remote_assets.to_dict().items()
        }

        return self.assets.get(asset_fqn_id)

    def add_asset(self, asset):
        self.assets_ref.update({firestore.Client.field_path(asset.fqn_id): asset.to_dict()})

        # Invalidates the cache
        logger.debug("[AssetCache] Invaliding the local cache after modifying the remote cache")
        self.assets = None

    def start_empty_cache(self):
        self.assets_ref.create({})
