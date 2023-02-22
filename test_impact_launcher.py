import argparse
from storage import StorageMode, RetentionPolicy
from coverage_map import CoverageMapEngine
from test_selection import TestSelectionEngine, TestSelectionPolicy
from changelist_generator import GitChangeListGenerator
from pathlib import Path
from test_runner.pytest_test_runner_engine import PytestTestRunnerEngine
from test_info_extractor import PyTestTestInformationExtractor
import test_prioritization
import pathlib
import pprint

FROM_COVERAGE = "from_coverage"
TEST_RUNNER_ARGS = "test_runner_args"
COVERAGE_ARGS = "coverage_args"
INIT_COMMIT = "init_commit"
FINAL_COMMIT = "final_commit"
TEST_SELECTION_POLICY = "test_selection_policy"
STORAGE_MODE = "storage_mode"
RETENTION_POLICY = "storage_retention_policy"
COVERAGE_TARGET = "coverage_target"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--test-runner-args",
                        type=str,
                        help="Args to call your test runner to generate coverage. Defaults to '-m pytest' which will run pytest with no additional arguments.",
                        required=False)

    parser.add_argument("--coverage-args",
                        type=str,
                        help="Args to apply to coverage module if necessary. Defaults to empty",
                        required=False)

    parser.add_argument("--init-commit",
                        type=str,
                        help="Initial commit that we will generate changes from.",
                        required=False)
    parser.add_argument("--final-commit",
                        type=str,
                        help="Final commit which we will generate changes from",
                        required=False)
    parser.add_argument("--test-selection-policy",
                        type=TestSelectionPolicy,
                        help="Test selection policy: covering_tests | covering_tests_and_dependencies | all. Defaults to covering_tests",
                        required=False)

    parser.add_argument("--storage-mode",
                        type=StorageMode,
                        help="Storage mode for test impact files: local  Defaults to local",
                        required=False)

    parser.add_argument("--storage-retention-policy",
                        type=RetentionPolicy,
                        help="Retention policy for test impact files: keep_all | keep_ten | keep_one.  Defaults to keep_all",
                        required=False)

    parser.add_argument("--coverage-target",
                        type=str,
                        help="Folder to store test_impact files in. Does not need to exist. Defaults to 'current_working_dir/coverage_dir'",
                        required=False)

    return parser.parse_args()


def main(args: dict):

    test_selection_policy = args.pop(
        TEST_SELECTION_POLICY) or TestSelectionPolicy.SELECT_COVERING_TESTS
    storage_mode = args.pop(STORAGE_MODE) or StorageMode.LOCAL
    retention_policy = args.pop(RETENTION_POLICY) or RetentionPolicy.KEEP_ALL
    coverage_file = args.get(COVERAGE_TARGET) or Path("coverage_dir")
    test_runner_args = args.get(TEST_RUNNER_ARGS) or "-m pytest"
    coverage_args = args.get(COVERAGE_ARGS) or ""
    init_commit = args.get(INIT_COMMIT) or ""
    final_commit = args.get(FINAL_COMMIT) or ""

    cg = GitChangeListGenerator(pathlib.Path.cwd())
    changelist = cg.get_changelist(init_commit, final_commit)

    coverage_map_engine = CoverageMapEngine(
        coverage_file, storage_mode, retention_policy, test_runner_args, coverage_args)
    coverage_map_engine.generate_coverage()

    coverage_map = coverage_map_engine.coverage_map
    test_info = PyTestTestInformationExtractor().load_test_information()

    te = TestSelectionEngine(test_selection_policy)
    selected_tests = te.select_tests(changelist, coverage_map, test_info)

    pe = test_prioritization.TestPrioritisationEngine(
        test_prioritization.TestPrioritisationPolicy.ALPHABETICAL)
    
    prioritised_list = pe.prioritise_tests(selected_tests)
    pprint.pprint(prioritised_list)

    tr = PytestTestRunnerEngine()
    additive_coverage_map = tr.execute_tests("", "", prioritised_list, test_info)
    coverage_map.update(additive_coverage_map)
    coverage_map_engine.store_coverage(coverage_map)


if __name__ == "__main__":
    main(vars(parse_args()))
