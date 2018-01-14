import os

ROOT_PATH = os.path.dirname(__file__)
ASSETS_PATH = os.environ.get('CONFIG_ASSETS_PATH', os.path.join(ROOT_PATH, 'assets'))
