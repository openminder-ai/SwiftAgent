from swiftagent.constants import CACHE_DIR


class SwiftCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize any instance attributes here
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not self._initialized:
            self._initialized = True
            # Add your initialization code here
            self.cache_dir = CACHE_DIR
