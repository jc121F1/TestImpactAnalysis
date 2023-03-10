import argparse
from storage import StorageMode, RetentionPolicy
from coverage_map import CoverageMapEngine
from coverage_map.coverage_generator import PytestCoverageGenerator
from test_selection import TestSelectionEngine, TestSelectionPolicy
from changelist_generator import GitChangeListGenerator, ChangeInfo
from pathlib import Path
from test_runner.pytest_test_runner_engine import PytestTestRunnerEngine
from test_info_extractor import PyTestTestInformationExtractor
from test_prioritization import TestPrioritisationEngine, TestPrioritisationPolicy
from test_impact_logger import get_logger
from global_enums import TestArchitectures, ChangelistGenerators
import sys
import pathlib

FROM_COVERAGE = "from_coverage"
TEST_RUNNER_ARGS = "test_runner_args"
COVERAGE_ARGS = "coverage_args"
TEST_EXEC_ARGS = "test_execution_args"
INIT_COMMIT = "init_commit"
FINAL_COMMIT = "final_commit"
TEST_SELECTION_POLICY = "test_selection_policy"
STORAGE_MODE = "storage_mode"
RETENTION_POLICY = "storage_retention_policy"
COVERAGE_TARGET = "coverage_target"
SOURCE_DIR = "source_directories"
LIB_DIR = "library_directories"
CHANGELIST_GENERATOR_TYPE = "changelist_generator"
TEST_ARCHITECTURE_TYPE = "test_architecture"

logger = get_logger(__file__)


def parse_args():
    parser = argparse.ArgumentParser()

    def listoffolders(value):
        l = value.replace(" ", "").split(",")
        for entry in l:
            if not pathlib.Path(value).is_dir():
                raise ValueError(
                    f"Error, given argument {value} is not a directory.")
        return l

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
                        required=True)
    parser.add_argument("--final-commit",
                        type=str,
                        help="Final commit which we will generate changes from",
                        required=True)

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

    parser.add_argument("--source-directories",
                        type=listoffolders,
                        help="Comma seperated list of folders that contains source files to scan for dependencies when using the \"select covering and dependencies\" test selection policy",
                        required=False)

    parser.add_argument("--library-directories",
                        type=listoffolders,
                        help="Comma seperated list of folders that contain library files to exclude when scanning for dependencies. \nPlease include any virtual environment files. For use when using the \"select covering and dependencies\" test selection policy",
                        required=False)

    parser.add_argument("--test-execution-args",
                        type=str,
                        help="Arguments to be passed to test runner when executing tests after selection. If not set, test-runner args will be used instead. If neither is set, no extra arguments will be passed to our test runner.",
                        required=False)

    parser.add_argument("--changelist-generator",
                        type=ChangelistGenerators,
                        help="Type of changelist generator type to be used. Built-in support for Git but custom generators can be written and bolted on as necessary.",
                        required=True)

    parser.add_argument("--test-architecture",
                        type=TestArchitectures,
                        help="Test architecture to carry out test selection and execution on. Built-in support is provided for PyTest, but other architectures can supported by following the provided patterns and generating the required data and passing it to the test selection engine.",
                        required=True)

    return parser.parse_args()


def main(args: dict):

    test_selection_policy = args.get(
        TEST_SELECTION_POLICY) or TestSelectionPolicy.SELECT_COVERING_TESTS
    storage_mode = args.get(STORAGE_MODE) or StorageMode.LOCAL
    retention_policy = args.get(RETENTION_POLICY) or RetentionPolicy.KEEP_ALL
    coverage_file = args.get(COVERAGE_TARGET) or Path("coverage_dir")
    test_runner_args = args.get(TEST_RUNNER_ARGS) or ""
    test_execution_args = args.get(
        TEST_EXEC_ARGS) or args.get(TEST_RUNNER_ARGS) or ""
    coverage_args = args.get(COVERAGE_ARGS) or ""
    init_commit = args.get(INIT_COMMIT)
    final_commit = args.get(FINAL_COMMIT)
    source_directories = args.get(SOURCE_DIR) or [""]
    library_directories = args.get(LIB_DIR) or [""]
    changelist_generator_type = args.get(CHANGELIST_GENERATOR_TYPE)
    test_architecture_type = args.get(TEST_ARCHITECTURE_TYPE)

    # Generate changelist
    try:
        changelist_generator_class = get_changelist_specific_tooling(
            changelist_generator_type)
        changelist = generate_changelist(
            changelist_generator_class, init_commit, final_commit)
    except Exception as e:
        logger.error(e)
        logger.error(
            "Execution cannot proceed without a changelist, program will exit.")
        sys.exit(0)


    test_generator_class, test_info_extractor_class, test_runner_engine_class = get_architecture_specific_tooling(
        test_architecture_type)

    # Generate coverage map or load it from memory
    coverage_map_engine = CoverageMapEngine(
        coverage_file, storage_mode, retention_policy, test_generator_class, test_runner_args, coverage_args)
    coverage_map_engine.generate_coverage()

    coverage_map = coverage_map_engine.coverage_map
    test_info = test_info_extractor_class().load_test_information()

    # Select tests and prioritise
    test_engine = TestSelectionEngine(test_selection_policy)
    selected_tests = test_engine.select_tests(
        changelist, coverage_map, test_info, source_directories, library_directories)
    logger.info(f"{len(selected_tests)} tests have been selected.")
    logger.info(
        f"The following tests have been selected by Test Impact Analysis:")
    pretty_print_list(selected_tests)

    pe = TestPrioritisationEngine(
        TestPrioritisationPolicy.ALPHABETICAL)
    prioritised_list = pe.prioritise_tests(selected_tests)

    # Run tests, update our coverage map, store it.
    tr = test_runner_engine_class()
    additive_coverage_map, return_code = tr.execute_tests(
        test_execution_args, coverage_args, prioritised_list, test_info)
    logger.info(f"Test execution concluded with returncode {return_code}")
    coverage_map.update(additive_coverage_map)
    coverage_map_engine.store_coverage(coverage_map)

    sys.exit(return_code)


def generate_changelist(changelist_generator_class, init_commit, final_commit):
    cg = changelist_generator_class(Path.cwd())
    return cg.get_changelist(init_commit, final_commit)


def get_changelist_specific_tooling(changelist_generator_type):
    if changelist_generator_type == ChangelistGenerators.Git:
        return GitChangeListGenerator


def get_architecture_specific_tooling(test_architecture_type):
    if test_architecture_type == TestArchitectures.PyTest:
        return PytestCoverageGenerator, PyTestTestInformationExtractor, PytestTestRunnerEngine


def pretty_print_list(list_to_print):
    for entry in list_to_print:
        logger.info(entry)


if __name__ == "__main__":
    main(vars(parse_args()))
