import pytest
import json
import pathlib
from coverage_map.coverage_generator.coverage_parser.pytest_coverage_parser import CoverageParserAndProcessor
# Define the path to the test coverage data
TEST_COVERAGE_DATA = pathlib.Path("test_json.json")

# Define the test data to be used for the tests
TEST_JSON_OBJ = {
    "files": {
        "file1.py": {
            "contexts": {
                "1": ["test1", "test2"],
                "2": ["test2"],
                "3": ["test3", ""]
            }
        },
        "file2.py": {
            "contexts": {
                "1": ["test1"],
                "2": ["test2", "test3"],
                "3": [""]
            }
        }
    }
}


@pytest.fixture
def coverage_data():
    # Write the test coverage data to a file
    with open(TEST_COVERAGE_DATA, "w") as f:
        json.dump(TEST_JSON_OBJ, f)

    # Load the coverage data using the CoverageParserAndProcessor class
    parser = CoverageParserAndProcessor(TEST_COVERAGE_DATA)

    # Return the coverage data
    return parser.coverage


def test_parse_covering_tests(coverage_data):
    # Test the coverage data for file1.py
    file1_coverage = coverage_data["file1.py"]
    file1_coverage = sorted(file1_coverage)
    assert file1_coverage == ["test1", "test2", "test3"]

    # Test the coverage data for file2.py
    file2_coverage = coverage_data["file2.py"]
    file2_coverage = sorted(file2_coverage)
    assert file2_coverage == ["test1", "test2", "test3"]


def test_init_exception():
    # Test if an exception is raised when the file is not found
    with pytest.raises(FileNotFoundError):
        parser = CoverageParserAndProcessor(pathlib.Path("nonexistent.json"))
