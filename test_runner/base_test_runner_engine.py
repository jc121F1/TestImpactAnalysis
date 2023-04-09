from abc import ABC, abstractclassmethod


class BaseTestRunnerEngine(ABC):
    """
    Base class for our TestRunnerEngine. Subclasses will inherit this class and implement the specifics for different test runners.
    """

    @abstractclassmethod
    def execute_tests(self, execution_arguments, coverage_arguments, tests_to_run, test_info):
        """ Execute all the tests in tests to run, feeding in the arguments in execution arguments to our test runner. Generate coverage of these tests and return this data.

        Args:
            execution_arguments (List): List of arguments to pass through to the test runner, such as Pytest
            coverage_arguments (List): List of arguments to pass through to the coverage tool, such as the Python Coverage module.
            tests_to_run (List): List of the tests to run
            test_info (Map): Map with qualified names of tests as the key, and a namedtuple TestInfo containing the path to the test file and the name to be passed to the test runner to execute the test.
        """
        pass

    @abstractclassmethod
    def get_tests_to_execute(self, test_info, tests_to_run):
        """
        Returns a list of pytest nodeids that can be fed into pytest to be executed. Used in no-execution mode.

        Args:
            tests_to_run (List): List of tests to execute
            test_info(Map): Map with qualified names of tests as the key, and a namedtuple TestInfo containing the path to the test file and the name to be passed to the test runner to execute the test.

        Returns:
        List: List of tests in a form that can be used by the test runner to execute all selected tests.
        """
        pass