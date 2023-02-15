import argparse
import coverage_map
import test_selection
import test_prioritization
import change_list_generator
import pathlib

FROM_COVERAGE = "from_coverage"
TEST_RUNNER_ARGS = "test_runner_args"
COVERAGE_ARGS = "coverage_args"


def parse_args():

    def file(file_path):
        if pathlib.Path(file_path).is_file():
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
    return parser.parse_args()


def main(args: dict):
    conv = lambda i: i or ""
    args = {key: conv(value) for (key, value) in args.items()}
    coverage_file = args.get(FROM_COVERAGE)
    test_runner_args = args.get(TEST_RUNNER_ARGS)
    coverage_args = args.get(COVERAGE_ARGS)

    # cm = coverage_map.CoverageMapEngine(pathlib.Path(
    #   "test_dir"), coverage_map.StorageMode.LOCAL, coverage_map.RetentionPolicy.KEEP_ALL, "", "")

    cg = change_list_generator.ChangeListGenerator(pathlib.Path.cwd())
    changelist = cg.get_changelist(
        "080a2754a2add46d8b6bdea20be015a7f9583b71", "b2d0e5d6ee37d651bcd4da248397139d2e8fd8dd")
    te = test_selection.TestSelectionEngine(changelist, test_selection.TestSelectionPolicy.SELECT_COVERING_TESTS, pathlib.Path(
        "coverage_dir"), test_runner_args, coverage_args)
    selected_tests = te.select_tests()
    te.store_coverage_map()
    pe = test_prioritization.TestPrioritisationEngine(
        test_prioritization.TestPrioritisationPolicy.ALPHABETICAL)
    prioritised_list = pe.prioritise_tests(selected_tests)
    print(prioritised_list)


if __name__ == "__main__":
    main(vars(parse_args()))
