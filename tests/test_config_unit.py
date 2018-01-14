import os
from importlib import reload

from decorator import contextmanager

import config


def test_asset_path_points_assets_dir():
    assert os.path.isdir(config.ASSETS_PATH)


@contextmanager
def env(key: str, value: str):
    old = os.environ.get(key)
    os.environ[key] = value
    yield
    if old is not None:
        os.environ[key] = old
    else:
        del os.environ[key]


def test_asset_path_can_be_overwritten_by_env():
    with env('CONFIG_ASSETS_PATH', '/the/assets/dir'):
        reload(config)
        assert config.ASSETS_PATH == '/the/assets/dir'
    reload(config)
    assert config.ASSETS_PATH != '/the/assets/dir'
