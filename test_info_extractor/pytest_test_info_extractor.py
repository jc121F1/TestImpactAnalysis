import pytest
from .base_test_info_extractor import BaseTestInformationExtractor, TestInfo


class PyTestTestInformationExtractor(BaseTestInformationExtractor):

    def load_test_information(self):
        """
        Load test information. This subclass implementation loads pytest test information using a plugin.
        Must return a map of qualified(full name) names of tests keys with TestInfo namedtuples values, where the first entry is the name of the test that can be passed to the test runner to execute the test, and the second is the path to the test file.
        """
        collector = NodeidsCollector()
        pytest.main(['--collect-only','-s','--disable-warnings'], plugins=[collector])
        return {f"{item.module.__name__}.{item.location[2]}": TestInfo(item.nodeid, item.location[0].replace("/", "\\")) for item in collector.nodeids}


class NodeidsCollector:
    def pytest_collection_modifyitems(self, items):
        self.nodeids = [item for item in items]
