from git import DiffIndex
from enum import Enum
from pathlib import Path
from storage.storage_base_class import StorageMode, RetentionPolicy
from coverage_map import CoverageMapEngine
from .test_selection_logger import get_logger

logger = get_logger(__file__)


TEST_LIST = "name_nodeid_map"


class TestSelectionPolicy(Enum):
    SELECT_ALL = "all"
    SELECT_COVERING_TESTS = "covering_tests"
    SELECT_COVERING_AND_DEPENDENCIES = "covering_tests_and_dependencies"


class TestSelectionEngine:

    def __init__(self, changelist: DiffIndex, test_selection_policy: TestSelectionPolicy, coverage_map):
        self.changelist = changelist
        self.test_selection_mode = test_selection_policy
        self.coverage_map = coverage_map

    def select_tests(self):
        test_info = self.coverage_map[TEST_LIST]
        tests_to_execute = []
        if self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_TESTS:
            tests_to_execute = self.select_covering_tests(
                self.coverage_map, test_info)
        elif self.test_selection_mode == TestSelectionPolicy.SELECT_ALL:
            tests_to_execute = test_info.keys()
        elif self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_AND_DEPENDENCIES:
            tests_to_execute = self.select_covering_tests_and_dependencies(self.coverage_map, test_info)
            pass

        return list(set(tests_to_execute))

    def select_covering_tests(self, coverage_map, test_info):
        tests_to_execute = []
        all_test_files = set([x[1] for x in test_info.values()])
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
                return test_info.keys()
        return tests_to_execute
    
    def select_covering_tests_and_dependencies(self, coverage_map, test_info):
        pass
