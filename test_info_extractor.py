import pytest
from collections import namedtuple
class TestInformationExtractor():

    def load_test_info(self):
        collector = NodeidsCollector()
        pytest.main(['--collect-only', '-pno:terminal'], plugins=[collector])
        TestInfo = namedtuple("TestInfo", ["nodeid", "path"])
        return {item.originalname: TestInfo(item.nodeid, item.location[0]) for item in collector.nodeids}


class NodeidsCollector:
    def pytest_collection_modifyitems(self, items):
        self.nodeids = [item for item in items]
