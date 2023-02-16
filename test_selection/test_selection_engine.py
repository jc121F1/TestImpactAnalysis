from git import DiffIndex
from enum import Enum
import coverage_map
from pathlib import Path
from .test_selection_logger import get_logger
from pytest import skip

logger = get_logger(__file__)


class TestSelectionPolicy(Enum):
    SELECT_ALL = 1
    SELECT_COVERING_TESTS = 2
    SELECT_COVERING_AND_DEPENDENCIES = 3


class TestSelectionEngine:

    def __init__(self, changelist: DiffIndex, test_selection_policy: TestSelectionPolicy, coverage_dir: Path, test_runner_args: str, coverage_args: str):
        self.changelist = changelist
        self.coverage_map_engine = coverage_map.CoverageMapEngine(
            coverage_dir, coverage_map.StorageMode.LOCAL, coverage_map.RetentionPolicy.KEEP_ALL, test_runner_args, coverage_args)
        self.test_selection_mode = test_selection_policy

    def select_tests(self):
        if self.coverage_map_engine.has_coverage:
            coverage_map = self.coverage_map_engine.coverage_map
            tests_to_execute = []
            if self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_TESTS:
                for changed_file in self.changelist:
                    try:
                        replaced = changed_file.a_path.replace("/","\\")
                        if (coverage_data := coverage_map[replaced]):
                            tests_to_execute += coverage_map[replaced]
                        else:
                            raise ValueError(f"No coverage data found for {replaced}")
                    except (KeyError, ValueError) as e:
                        logger.warning(
                            f"File {changed_file.a_path} was changed but we have no coverage data available for this file. Executing all tests.")
                        tests_to_execute = coverage_map['all_tests']
                        break

            elif self.test_selection_mode == TestSelectionPolicy.SELECT_ALL:
                tests_to_execute = coverage_map['all_tests']


            elif self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_AND_DEPENDENCIES:
                # TODO: Select tests for dependencies
                pass

            return list(set(tests_to_execute))

        else:
            logger.warning(
                "No coverage data available. All tests will be executed.")
            return []
        
    def store_coverage_map(self):
        self.coverage_map_engine.store_coverage(self.coverage_map_engine.coverage_dir, self.coverage_map_engine.coverage_map)
