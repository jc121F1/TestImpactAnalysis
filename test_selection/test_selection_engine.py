from git import DiffIndex
import coverage_map as CoverageMap
from pathlib import Path
class TestSelectionEngine:

    def __init__(self, changelist: DiffIndex, test_selection_mode, coverage_dir: Path):
        self.changelist = changelist
        self.coverage_map_engine = CoverageMap.Engine(coverage_dir)
        self.test_selection_mode = test_selection_mode

    def select_tests(self):
        if self.coverage_map_engine.has_coverage:
            # select_tests
            pass
        else:
            raise ValueError(
                "Error, no coverage available. All tests will be executed.")
