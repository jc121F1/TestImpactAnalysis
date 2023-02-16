from git import DiffIndex
from enum import Enum
from pathlib import Path
from coverage_map.coverage_map_storage import StorageMode, RetentionPolicy
from coverage_map import CoverageMapEngine
from .test_selection_logger import get_logger

logger = get_logger(__file__)


TEST_LIST = "name_nodeid_map"


class TestSelectionPolicy(Enum):
    SELECT_ALL = "all"
    SELECT_COVERING_TESTS = "covering_tests"
    SELECT_COVERING_AND_DEPENDENCIES = "covering_tests_and_dependencies"


class TestSelectionEngine:

    def __init__(self, changelist: DiffIndex, test_selection_policy: TestSelectionPolicy, coverage_dir: Path, test_runner_args: str, coverage_args: str, storage_mode: StorageMode, retention_policy: RetentionPolicy):
        self.changelist = changelist
        self.coverage_map_engine = CoverageMapEngine(
            coverage_dir, storage_mode, retention_policy, test_runner_args, coverage_args)
        self.test_selection_mode = test_selection_policy

    def select_tests(self):
        if self.coverage_map_engine.has_coverage:
            coverage_map = self.coverage_map_engine.coverage_map
            tests_to_execute = []
            if self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_TESTS:
                tests_to_execute = self.select_covering_tests(coverage_map)
            elif self.test_selection_mode == TestSelectionPolicy.SELECT_ALL:
                tests_to_execute = coverage_map[TEST_LIST].keys()
            elif self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_AND_DEPENDENCIES:
                # TODO: Select tests for dependencies
                pass

            return list(set(tests_to_execute))

        else:
            logger.warning(
                "No coverage data available. All tests will be executed.")
            return []

    def select_covering_tests(self, coverage_map):
        tests_to_execute = []
        for changed_file in self.changelist:
            try:
                replaced = changed_file.a_path.replace("/", "\\")
                if (coverage_data := coverage_map[replaced]):
                    tests_to_execute += coverage_map[replaced]
                else:
                    raise ValueError(
                        f"No coverage data found for {replaced}")
            except (KeyError, ValueError) as e:
                logger.warning(
                    f"File {changed_file.a_path} was changed but we have no coverage data available for this file. Executing all tests.")
                return coverage_map[TEST_LIST].keys()
        return tests_to_execute

    def store_coverage_map(self):
        self.coverage_map_engine.store_coverage(
            self.coverage_map_engine.coverage_map)
