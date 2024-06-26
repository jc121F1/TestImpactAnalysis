import argparse
import logging
from storage import StorageMode, RetentionPolicy
from coverage_map import CoverageMapEngine
from coverage_map.coverage_generator import PytestCoverageGenerator
from test_selection import TestSelectionEngine, TestSelectionPolicy
from changelist_generator import GitChangeListGenerator, ChangeInfo
from pathlib import Path
from test_runner.pytest_test_runner_engine import PytestTestRunnerEngine
from test_info_extractor import PyTestTestInformationExtractor
from test_prioritization import TestPrioritisationEngine, TestPrioritisationPolicy
from test_impact_logger import get_logger, get_handler, config_logger
from global_enums import TestArchitectures, ChangelistGenerators, ExecutionMode, Verbosity
import util
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
IGNORE_DIR = "ignore_dir"
IGNORE_FOLDERS = "ignore_directories"
IGNORE_FILES = "ignore_files"
EXECUTION_MODE = "execution_mode"
VERBOSITY = "verbosity"

def parse_args():
    parser = argparse.ArgumentParser()

    def list_of_folders(value):
        l = value.replace(" ", "").split(",")
        for entry in l:
            if not pathlib.Path(entry).is_dir():
                raise ValueError(
                    f"Error, given argument {entry} is not a directory.")
        return l

    def list_of_files(value):
        l = value.replace(" ", "").split(",")
        for entry in l:
            if not pathlib.Path(entry).absolute().is_file():
                raise ValueError(
                    f"Error, given argument {entry} is not a file."
                )
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
                        help="Test selection policy: covering_tests | all. Defaults to covering_tests",
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

    parser.add_argument("--ignore-directories",
                        type=list_of_folders,
                        help="Comma seperated list of folders to ignore changes in when selecting tests.",
                        required=False)
    
    parser.add_argument("--ignore-files",
                        type=list_of_files,
                        help="Comma seperated list of files(relative or absolute path) to ignore changes in when selecting tests.")
    
    parser.add_argument("--execution-mode",
                        type=ExecutionMode,
                        help="Mode for test runner. \"execute\" will use the test runner to execute the tests, \"list\" will print a list of tests in an executable form out to the console. Defaults to execute.",
                        required=False)
    
    parser.add_argument("--verbosity",
                        type=Verbosity,
                        help="Verbosity of logging. Options are Normal | Debug | Silenced. Defaults to Normal.",
                        required=False)

    return parser.parse_args()

logger = config_logger("logger")

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
    changelist_generator_type = args.get(CHANGELIST_GENERATOR_TYPE)
    test_architecture_type = args.get(TEST_ARCHITECTURE_TYPE)
    folders_to_ignore = args.get(IGNORE_FOLDERS) or list()
    files_to_ignore = args.get(IGNORE_FILES) or list()
    execution_mode = args.get(EXECUTION_MODE) or ExecutionMode.Execute
    verbosity = lookup_logging_level(args.get(VERBOSITY)) or logging.INFO

    logger.setLevel(verbosity)
    # Generate changelist
    try:
        changelist_generator_class = get_changelist_specific_tooling(
            changelist_generator_type)
        changelist = generate_changelist(
            changelist_generator_class, init_commit, final_commit)
        logger.debug(changelist)
    except Exception as e:
        logger.error(e)
        logger.error(
            "Execution cannot proceed without a changelist, program will exit.")
        sys.exit(0)


    test_generator_class, test_info_extractor_class, test_runner_engine_class = get_architecture_specific_tooling(test_architecture_type)

    # Generate coverage map or load it from memory
    coverage_map_engine = CoverageMapEngine(
        coverage_file, storage_mode, retention_policy, test_generator_class, test_runner_args, coverage_args)
    coverage_map_engine.generate_coverage()

    coverage_map = coverage_map_engine.coverage_map
    logger.debug(coverage_map)
    test_info = test_info_extractor_class().load_test_information()
    logger.debug(test_info)
    
    # This section of code prevents duplication of logging handlers that can occur when extracting test information
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(get_handler(__file__))
    logger.setLevel(verbosity)

    # Select tests and prioritise
    
    files_to_ignore = list(map(pathlib.Path, files_to_ignore))
    files_to_ignore += util.get_file_names_from_directory(folders_to_ignore)
    test_engine = TestSelectionEngine(test_selection_policy)
    selected_tests = test_engine.select_tests(
        changelist, coverage_map, test_info, files_to_ignore)
    logger.info(f"{len(selected_tests)} tests have been selected.")
    logger.info("The following tests have been selected by Test Impact Analysis:")
    logger.debug(selected_tests)
    pretty_print_list(selected_tests)

    if len(selected_tests) > 0:
        pe = TestPrioritisationEngine(
            TestPrioritisationPolicy.ALPHABETICAL)
        prioritised_list = pe.prioritise_tests(selected_tests)

        # Run tests, update our coverage map, store it.
        tr = test_runner_engine_class()
        if execution_mode == ExecutionMode.Execute:
            additive_coverage_map, return_code = tr.execute_tests(
                test_execution_args, coverage_args, prioritised_list, test_info)
            logger.info(
                f"Test execution concluded with returncode {return_code}")
            coverage_map.update(additive_coverage_map)
            coverage_map_engine.store_coverage(coverage_map)
        elif execution_mode == ExecutionMode.List_Only:
            tests_in_executable_form = tr.get_tests_to_execute(prioritised_list, test_info)
            logger.info("Listing all selected tests:")
            logger.info(" ".join(tests_in_executable_form))
            return_code = 0

    else:
        return_code = 0
    sys.exit(return_code)


def generate_changelist(changelist_generator_class, init_commit, final_commit):
    with changelist_generator_class(Path.cwd()) as cg:
        return cg.get_changelist(init_commit, final_commit)


def get_changelist_specific_tooling(changelist_generator_type):
    """
    Returns the correct changelist generator class depending on the changelist_generator_type provided. 
    Allows for user implementation of different generator classes for different source control systems.

    Args:
        changelist_generator_type (Enum): Enum representing the type of changelist generator

    Returns:
        ChangeListGenerator: A changelist generator subclass.
    """
    if changelist_generator_type == ChangelistGenerators.Git:
        return GitChangeListGenerator


def get_architecture_specific_tooling(test_architecture_type):
    """
    Returns the correct coverage generator, test information extractor, and test runner engine based on what testing architecture has been selected. This allows for user implemented versions of these classes.

    Args:
        test_architecture_type (Enum): Which test architecture to use.

    Returns:
       3-Tuple of TestCoverageGenerator, TestInformationExtractor, and TestRunnerEngine classes.
    """
    if test_architecture_type == TestArchitectures.PyTest:
        return PytestCoverageGenerator, PyTestTestInformationExtractor, PytestTestRunnerEngine

def lookup_logging_level(level):
    if level == Verbosity.Debug:
        return logging.DEBUG
    if level == Verbosity.Normal:
        return logging.INFO
    if level == Verbosity.Silenced:
        return logging.CRITICAL

def pretty_print_list(list_to_print):
    if len(list_to_print)== 0:
        logger.info("List is empty.")
    else:
        for entry in list_to_print:
            logger.info(entry)

if __name__ == "__main__":
    main(vars(parse_args()))
