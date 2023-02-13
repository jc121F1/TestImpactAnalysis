import json
import uuid
from coverage_map_storage import CoverageMapStorage, StoragePolicy as SP
from coverage_map_logger import get_logger
import os
from pathlib import Path

logger = get_logger(__file__)


class LocalCoverageMapStorage(CoverageMapStorage):

    id = uuid.uuid1()

    def __init__(self, storage_location: Path, storage_policy: SP = SP.KEEP_ALL):
        self.storage_policy = storage_policy
        self.storage_location = storage_location
        self.validate_storage_location
        self.map = self.load_map(storage_location)

    def load_map(self, storage_location: Path):
        try:
            latest_file = max(storage_location.rglob(
                f'*.{self.file_extension}'), key=os.path.getctime)
            with open(latest_file, "rb") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Error {e}. Error parsing JSON Coverage Map.")
        except Exception as e:
            logger.warning(f"Error {e}")

    def save_map(self, storage_location: Path, map: dict):
        self.validate_storage_location
        try:
            storage_file_path = storage_location.joinpath(Path(
                f"{self.file_name}_{self.id}.{self.file_extension}"))
            with open(storage_file_path, "w+") as f:
                json.dump(map, f)
        except Exception as e:
            logger.warning(f"Error {e}")

    @property
    def has_map(self):
        if self.map:
            return True
        return False

    @property
    def validate_storage_location(self):
        if (self.storage_location.exists()):
            return True
        raise ValueError("Error, folder does not exist.")


storage_location = Path(str(Path.cwd())+"/test_dir")
lc = LocalCoverageMapStorage(storage_location)
print(lc.has_map)
lc.save_map(storage_location, lc.map)
