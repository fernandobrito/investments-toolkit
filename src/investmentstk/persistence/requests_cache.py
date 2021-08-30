from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path

import requests_cache
from requests_cache import FileCache, json_serializer

current_folder = Path(__file__).resolve().parent

"""
Default cache options for a filesystem backend.
https://requests-cache.readthedocs.io/en/v0.7.4/modules/requests_cache.backends.html#module-requests_cache.backends.filesystem
"""
file_cache = FileCache(cache_name=current_folder / "../../.." / "cache" / "http_cache", serializer=json_serializer)


def cache_default_options(hours: float = 24):
    return dict(expire_after=timedelta(hours=hours))


@contextmanager
def requests_cache_configured(hours: float = 24):
    """
    Wrapper around a configured requests_cache context manager
    """
    with requests_cache.enabled(backend=file_cache, **cache_default_options(hours=hours)):
        yield
