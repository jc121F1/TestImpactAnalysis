
from abc import abstractmethod, ABC
from pathlib import Path
from enum import Enum


class RetentionPolicy(Enum):
    KEEP_ALL = "keep_all"
    KEEP_ONE = "keep_one"
    KEEP_TEN = "keep_ten"


class StorageMode(Enum):
    LOCAL = "local"


class BaseCoverageMapStorage(ABC):
    
    map = None
    file_extension = "testimpact"
    file_name = "test_impact_map"

    @abstractmethod
    def __init__(self, storage_location: Path, storage_policy: RetentionPolicy):
        """
        Initialises class controlling storage. Each individual subclass will control a different storage method, ie local storage, AWS S3 storage or Azure cloud storage.

        Args:
            storage_location (Path): Location to store and retrieve testimpact data from.
            storage_policy (RetentionPolicy): Retention Policy for storage. Options are stored in RetentionPolicy in storage_base_class.
        """
        pass

    @abstractmethod
    def load_map(self, storage_location: Path):
        """
        Attempt to load map from location specified in storage_location and store it in self.map. Will handle exceptions caused by this attempt. If failure to retrieve occurs, self.map will be empty.

        Args:
            storage_location (Path): Location to try and load our coverage data from.
        """
        pass

    @abstractmethod
    def save_map(self, storage_location: Path, map: dict):
        """
        Attempt to store coverage data in the storage location specified. Will handle exceptions caused by this attempt. Possible to fail to save data and continue program execution.

        Args:
            storage_location (Path): Location to try and load our coverage data from.
            map (dict): Coverage data to store.
        """
        pass
