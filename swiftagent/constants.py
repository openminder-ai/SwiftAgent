from platformdirs import user_cache_dir
from pathlib import Path

CACHE_DIR = Path(user_cache_dir("swiftagent"))
