from pathlib import Path
from coverage_map.coverage_generator import CoverageGenerator as Generator
from coverage_map.coverage_map_local_storage import LocalCoverageMapStorage as LocalStorage
from coverage_map.coverage_map_storage import StorageMode as SM, RetentionPolicy as RP
from coverage_map.coverage_map_logger import get_logger

logger = get_logger(__file__)

TEST_LIST = "name_nodeid_map"


class CoverageMapEngine():

    def __init__(self, coverage_dir: Path, storage_mode: SM, storage_retention_policy: RP, pytest_args, coverage_args):
        self.coverage_dir = coverage_dir
        self.storage_mode = storage_mode
        self.storage_retention_policy = storage_retention_policy
        self.initialise_storage()
        if (coverage := self.retrieve_coverage()):
            self.coverage_map = coverage
        else:
            generator = Generator(pytest_args, coverage_args)
            generator.generate_coverage()
            self.coverage_map = generator.load_coverage()
            self.coverage_map[TEST_LIST] = generator.load_test_info()
            
    def initialise_storage(self):
        if self.storage_mode == SM.LOCAL:
            self.storage = LocalStorage(self.coverage_dir, self.storage_retention_policy)

    def retrieve_coverage(self):
        self.storage.load_map()
        if (self.storage.has_map):
            return self.storage.map
        return None

    def store_coverage(self, coverage_map: dict):
        self.storage.save_map(coverage_map)

    @property
    def has_coverage(self):
        try:
            if self.coverage_map:
                return True
            return False
        except AttributeError as e:
            self.coverage_map = None
