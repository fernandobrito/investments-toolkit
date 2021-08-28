from pathlib import Path

from requests_cache import FileCache, json_serializer

current_folder = Path(__file__).resolve().parent

"""
Default cache options for a filesystem backend.
https://requests-cache.readthedocs.io/en/v0.7.4/modules/requests_cache.backends.html#module-requests_cache.backends.filesystem
"""
file_cache = FileCache(cache_name=current_folder / "../../.." / "cache" / "http_cache", serializer=json_serializer)
