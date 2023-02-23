import json
import uuid
from storage import BaseCoverageMapStorage, RetentionPolicy as RP, get_logger
import os
from pathlib import Path

logger = get_logger(__file__)


class LocalCoverageMapStorage(BaseCoverageMapStorage):

    id = uuid.uuid1()

    def __init__(self, storage_location: Path, retention_policy: RP):
        self.retention_policy = retention_policy
        self.storage_location = storage_location

    def load_map(self):
        try:
            self.validate_storage_location()
            glob = self.storage_location.rglob(
                f'*{self.file_extension}')
            globs = list(glob)
            if len(globs) > 0:
                latest_file = max(globs, key=lambda p: p.stat().st_ctime)
                with open(latest_file, "rb") as f:
                    self.map = json.load(f)
            else:
                raise ValueError("No test impact files found")
        except json.JSONDecodeError as e:
            logger.warning(f"Error: {e}. Error parsing JSON Coverage Map.")
        except Exception as e:
            logger.warning(f"Error: {e}")

    def save_map(self, map: dict):
        try:
            if not self.storage_location.exists():
                os.mkdir(self.storage_location)
            storage_file_path = self.storage_location.joinpath(Path(
                f"{self.file_name}_{self.id}.{self.file_extension}"))
            with open(storage_file_path, "w+") as f:
                logger.info(f"Writing map to {storage_file_path}")
                json.dump(map, f)
            self.apply_storage_policy()
        except Exception as e:
            logger.warning(f"Error: {e}")

    def apply_storage_policy(self):
        if self.retention_policy == RP.KEEP_ALL:
            pass
        elif self.retention_policy == RP.KEEP_ONE:
            latest_file = max(self.storage_location.rglob(
                f'*{self.file_extension}'), key=os.path.getctime)
            for file in self.storage_location.rglob(f'*{self.file_extension}'):
                if (file != latest_file):
                    os.remove(file)
        elif self.retention_policy == RP.KEEP_TEN:
            files_to_delete = sorted(self.storage_location.rglob(
                f'*{self.file_extension}'), key=os.path.getctime, reverse=True)[10:]
            for file in files_to_delete:
                os.remove(file)

    @property
    def has_map(self):
        if self.map:
            return True
        return False

    def validate_storage_location(self):
        if (self.storage_location.exists()):
            return True
        raise ValueError(f"Folder {self.storage_location} does not exist.")