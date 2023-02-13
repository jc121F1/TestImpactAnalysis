import json
import pathlib

FILE_CONST = "files"
COV_TEST_CONST = 'covering_tests'
CONTEXTS = "contexts"


class CoverageParserAndProcessor():
    __json_obj = {}
    __files = {}

    def __init__(self, filepath: pathlib.Path):
        with open(filepath, "rb") as f:
            self.__json_obj: dict = json.load(f)

        try:
            for file_name, file_info in self.__json_obj[FILE_CONST].items():
                self.__files[file_name] = self.parse_covering_tests(file_info)
        except Exception as e:
            print(e)

    def parse_covering_tests(self, file_info):
        covering_tests = []
        for line, contexts in file_info[CONTEXTS].items():
            covering_tests.extend(contexts)
        file_info[COV_TEST_CONST] = [x for x in set(covering_tests) if x != ""]
        return file_info

    @property
    def get_file_names(self):
        return self.__files.keys()
