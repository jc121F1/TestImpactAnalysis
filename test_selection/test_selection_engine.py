from enum import Enum
from pathlib import Path
import re
import pkgutil
import modulefinder
from test_impact_logger import get_logger

logger = get_logger(__file__)


class TestSelectionPolicy(Enum):
    SELECT_ALL = "all"
    SELECT_COVERING_TESTS = "covering_tests"
    SELECT_COVERING_AND_DEPENDENCIES = "covering_tests_and_dependencies"


class TestSelectionEngine:

    def __init__(self, test_selection_policy: TestSelectionPolicy):
        self.test_selection_mode = test_selection_policy

    def select_tests(self, changelist: list, coverage_map: map, test_info: list, files_to_ignore: list = []):
        tests_to_execute = []
        if not changelist:
            tests_to_execute = test_info.keys()
        else:
            if self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_TESTS:
                tests_to_execute = self.select_covering_tests(
                    changelist, coverage_map, test_info, files_to_ignore)
            elif self.test_selection_mode == TestSelectionPolicy.SELECT_ALL:
                tests_to_execute = test_info.keys()
            elif self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_AND_DEPENDENCIES:
                logger.warning("Covering and dependencies policy not enabled, selecting all tests")
                tests_to_execute = test_info.keys()
            else:
                raise ValueError("Provided policy does not exist.")

        return list(set(tests_to_execute))

    def select_covering_tests(self, changelist, coverage_map, test_info, files_to_ignore: list = []):
        tests_to_execute = []
        for changed_file in changelist:
            try:
                if (coverage_data := coverage_map[changed_file.path]):
                    tests_to_execute += coverage_data
            except (KeyError) as e:
                if changed_file.path.endswith("__init__.py"):
                    logger.info(f"File: {changed_file.path} was ignored as it is an init file.")
                    continue
                if Path(changed_file.path).absolute() in files_to_ignore or Path(changed_file.path) in files_to_ignore:
                    logger.info(f"File: {changed_file.path} was ignored as it is in the list of files or directories to ignore.")
                    continue
                else:
                    logger.warning(
                    f"File {changed_file.path} was changed but we have no coverage data available for this file. Executing all tests.")
                    return list(test_info.keys())
        return tests_to_execute