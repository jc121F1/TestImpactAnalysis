from abc import ABC, abstractclassmethod


class BaseCoverageGenerator(ABC):
    """
    Base class for Coverage Generator. Sub classes will extend this class for specific functionality, such as supporting different coverage generation methods.
    """

    @abstractclassmethod
    def __init__(self, test_runner_args, coverage_args):
        """        Initialise CoverageGenerator class.

        Args:
            test_runner_args (List[String]): List of arguments to pass through to our coverage tool.
            coverage_args (List[String]): List of arguments to pass through to the test runner we use to run tests and generate coverage.
        """
        pass

    @abstractclassmethod
    def generate_coverage(self):
        """
        Generate coverage for our tests.
        """

    @abstractclassmethod
    def load_coverage(self):
        """
        Load our generated coverage info using a CoverageParser and return the resulting coverage data. 
        Will raise a ValueError if coverage data is not found.

        Return:
            Coverage data generated in generate coverage.
        """
