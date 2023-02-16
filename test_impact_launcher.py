import argparse
from coverage_map.coverage_map_storage import StorageMode, RetentionPolicy
from test_selection import TestSelectionEngine, TestSelectionPolicy
from change_list_generator import ChangeListGenerator
from pathlib import Path
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


def parse_args():

    def file(file_path):
        if Path(file_path).is_file():
            return file_path
        else:
            return ValueError("Error, file does not exist.")

    parser = argparse.ArgumentParser()

    parser.add_argument("--from-coverage",
                        type=file,
                        help="Path a valid coverage json file to be used to seed maps",
                        required=False)

    parser.add_argument("--test-runner-args",
                        type=str,
                        help="Args to call your test runner to generate coverage",
                        required=False)

    parser.add_argument("--coverage-args",
                        type=str,
                        help="Args to apply to coverage module if necessary.",
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

    return parser.parse_args()


def main(args: dict):

    test_selection_policy = args.pop(
        TEST_SELECTION_POLICY) or TestSelectionPolicy.SELECT_COVERING_TESTS
    storage_mode = args.pop(STORAGE_MODE) or StorageMode.LOCAL
    retention_policy = args.pop(RETENTION_POLICY) or RetentionPolicy.KEEP_ALL
    coverage_file = args.get(FROM_COVERAGE) or ""
    test_runner_args = args.get(TEST_RUNNER_ARGS) or ""
    coverage_args = args.get(COVERAGE_ARGS) or ""
    init_commit = args.get(INIT_COMMIT) or ""
    final_commit = args.get(FINAL_COMMIT) or ""

    cg = ChangeListGenerator(pathlib.Path.cwd())
    changelist = cg.get_changelist(init_commit, final_commit)
    te = TestSelectionEngine(changelist, test_selection_policy, Path(
        "coverage_dir"), test_runner_args, coverage_args, storage_mode, retention_policy)
    selected_tests = te.select_tests()
    pe = test_prioritization.TestPrioritisationEngine(
        test_prioritization.TestPrioritisationPolicy.ALPHABETICAL)
    prioritised_list = pe.prioritise_tests(selected_tests)
    pprint.pprint(prioritised_list)
    te.store_coverage_map()


if __name__ == "__main__":
    main(vars(parse_args()))
