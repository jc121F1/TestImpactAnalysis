from pathlib import Path
from coverage_map.coverage_generator import PytestCoverageGenerator as Generator
from storage import LocalCoverageMapStorage as LocalStorage
from storage import StorageMode as SM, RetentionPolicy as RP
from .logger import get_logger

logger = get_logger(__file__)

TEST_LIST = "name_nodeid_map"


class CoverageMapEngine():

    coverage_map = {}

    def __init__(self, coverage_dir: Path, storage_mode: SM, storage_retention_policy: RP, generator_class, test_runner_args, coverage_args):
        self.coverage_dir = coverage_dir
        self.storage_mode = storage_mode
        self.storage_retention_policy = storage_retention_policy
        self.test_runner_args = test_runner_args
        self.coverage_args = coverage_args
        self.generator_class = generator_class
        self.initialise_storage()

    def initialise_storage(self):
        if self.storage_mode == SM.LOCAL:
            self.storage = LocalStorage(
                self.coverage_dir, self.storage_retention_policy)

    def retrieve_coverage(self):
        self.storage.load_map()
        if (self.storage.has_map):
            return self.storage.map
        return None

    def store_coverage(self, coverage_map: dict):
        self.storage.save_map(coverage_map)

    def generate_coverage(self):
        if (coverage := self.retrieve_coverage()):
            self.coverage_map = coverage
        else:
            generator = self.generator_class(self.test_runner_args, self.coverage_args)
            generator.generate_coverage()
            self.coverage_map = generator.load_coverage()

    @property
    def has_coverage(self):
        if self.coverage_map:
            return True
        return False
