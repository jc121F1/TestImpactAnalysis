from .base_coverage_parser import BaseCoverageParserAndProcessor
import json
import pathlib

FILE_CONST = "files"
COV_TEST_CONST = 'covering_tests'
CONTEXTS = "contexts"


class CoverageParserAndProcessor(BaseCoverageParserAndProcessor):
    __json_obj = {}
    __files = {}
    __coverage_data = {}

    def __init__(self, filepath: pathlib.Path):
        try:
            with open(filepath, "rb") as f:
                self.__json_obj: dict = json.load(f)
            for file_name, file_info in self.__json_obj[FILE_CONST].items():
                self.__coverage_data[file_name] = self.parse_covering_tests(
                    file_info)
        except Exception as e:
            print(e)

    def parse_covering_tests(self, file_info):
        covering_tests = []
        for line, contexts in file_info[CONTEXTS].items():
            covering_tests.extend(contexts)
        return [x for x in set(covering_tests) if x != ""]

    @property
    def coverage(self):
        return self.__coverage_data
