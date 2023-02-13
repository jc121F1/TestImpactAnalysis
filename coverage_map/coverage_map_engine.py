from pathlib import Path
from coverage_generator import CoverageGenerator as Generator
from coverage_map_local_storage import LocalCoverageMapStorage as LocalStorage
from coverage_map_storage import StorageMode as SM, RetentionPolicy as RP
from coverage_map_logger import get_logger

logger = get_logger(__file__)


class CoverageMapEngine():

    def __init__(self, coverage_dir: Path, storage_mode: SM, storage_retention_policy: RP, pytest_args, coverage_args):
        self.coverage_dir = coverage_dir
        self.storage_mode = storage_mode
        self.storage_retention_policy = storage_retention_policy
        if (coverage := self.retrieve_coverage(coverage_dir)):
            self.coverage = coverage
        else:
            generator = Generator(pytest_args, coverage_args)
            generator.generate_coverage()

    def retrieve_coverage(self, coverage_dir: str):
        if self.storage_mode == SM.LOCAL:
            if (storage := LocalStorage(coverage_dir, self.storage_retention_policy).has_map):
                return storage.map
        return None


cm = CoverageMapEngine(Path("test"), SM.LOCAL, RP.KEEP_ALL, "py", "cov")
