import json
import os
from contextlib import contextmanager
from datetime import timedelta, datetime
from pathlib import Path

import requests
import requests_cache
from requests_cache import json_serializer

from investmentstk.utils.logger import get_logger

current_folder = Path(__file__).resolve().parent
http_cache_folder = current_folder / "../../.." / "cache" / "http_cache"

logger = get_logger()


def avoid_caching_google_api_requests(response: requests.Response) -> bool:
    """
    Returns a boolean indicating whether or not that response should be cached.
    """

    if "google" in response.url.lower():
        return False

    return True


def cache_default_options(hours: float = 24):
    """
    Default cache options for a filesystem backend.
    https://requests-cache.readthedocs.io/en/v0.7.4/modules/requests_cache.backends.html#module-requests_cache.backends.filesystem
    """

    return dict(
        backend="filesystem",
        expire_after=timedelta(hours=hours),
        cache_name=http_cache_folder,
        serializer=json_serializer,
        filter_fn=avoid_caching_google_api_requests,
    )


@contextmanager
def requests_cache_configured(*, hours: float = 1, **kwargs):
    """
    Wrapper around a configured requests_cache context manager
    """
    args = {**cache_default_options(hours=hours), **kwargs}

    with requests_cache.enabled(**args):
        yield


def delete_cached_requests() -> list[str]:
    deleted_and_valid = []

    for file_path in http_cache_folder.glob("*.json"):
        cache = json.loads(Path(file_path).read_text())
        os.remove(file_path)

        expires = datetime.fromisoformat(cache["expires"])

        if expires <= datetime.utcnow():
            logger.debug(f"Skipping expired: {file_path}")
            continue

        deleted_and_valid.append(cache["url"])

    return deleted_and_valid
