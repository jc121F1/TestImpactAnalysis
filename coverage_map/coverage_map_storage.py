
from abc import abstractmethod, ABC
from pathlib import Path
from enum import Enum


class RetentionPolicy(Enum):
    KEEP_ALL = "keep_all"
    KEEP_ONE = "keep_one"
    KEEP_TEN = "keep_ten"


class StorageMode(Enum):
    LOCAL = "local"


class CoverageMapStorage(ABC):
    
    map = None
    file_extension = "testimpact"
    file_name = "test_impact_map"

    @abstractmethod
    def __init__(self, storage_location: Path, storage_policy: RetentionPolicy):
        pass

    @abstractmethod
    def load_map(self, storage_location: Path):
        pass

    @abstractmethod
    def save_map(self, storage_location: Path, map: dict):
        pass
