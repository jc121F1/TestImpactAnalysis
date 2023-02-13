
from abc import abstractmethod, ABC
from pathlib import Path
from enum import Enum

class StoragePolicy(Enum):
    KEEP_ALL = 1
    KEEP_ONE = 2
    KEEP_TEN = 3

class CoverageMapStorage(ABC):

    file_extension = "testimpact"
    file_name = "test_impact_map"

    @abstractmethod
    def __init__(self, storage_location: Path, storage_policy: StoragePolicy):
        pass
    
    @abstractmethod
    def load_map(self, storage_location: Path):
        pass

    @abstractmethod
    def save_map(self, storage_location: Path, map: dict):
        pass