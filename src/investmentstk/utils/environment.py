import os


def is_in_cloud_run():
    return bool(os.environ.get("K_SERVICE", None))
