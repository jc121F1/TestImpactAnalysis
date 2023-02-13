from git import DiffIndex
import coverage_map
from pathlib import Path
from .test_selection_logger import get_logger

logger = get_logger(__file__)
class TestSelectionEngine:

    def __init__(self, changelist: DiffIndex, test_selection_mode, coverage_dir: Path):
        self.changelist = changelist
        self.coverage_map_engine = coverage_map.CoverageMapEngine(coverage_dir, coverage_map.StorageMode.LOCAL, coverage_map.RetentionPolicy.KEEP_ALL, "", "")
        self.test_selection_mode = test_selection_mode

    def select_tests(self):
        if self.coverage_map_engine.has_coverage:
            tests_to_execute = []
            for changed_file in self.changelist:
                try:
                    tests_to_execute += self.coverage_map_engine.coverage_map[changed_file.a_path]
                except KeyError as e:
                    logger.warning(f"File {changed_file.a_path} was changed but we have no coverage data available for this file. Executing all tests.")
                    return []
            
            return set(tests_to_execute)

        else:
            logger.warning("No coverage data available. All tests will be executed.")
            return []
