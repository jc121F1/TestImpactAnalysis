from abc import ABC, abstractclassmethod
from collections import namedtuple

TestInfo = namedtuple("TestInfo", ["nodeid", "path"])

class BaseTestInformationExtractor(ABC):

    @abstractclassmethod
    def load_test_information(self):
        """
        Load test information. Overriden by subclasses. 
        Must return a list of TestInfo namedtuples, where the first entry is the name of the test that can be passed to the test runner to execute the test, and the second is the path to the test file.
        """
        pass