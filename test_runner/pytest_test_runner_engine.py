import subprocess
from test_impact_logger import get_logger
from test_runner import BaseTestRunnerEngine
from coverage_map.coverage_generator import PytestCoverageGenerator

logger = get_logger("logger")


class PytestTestRunnerEngine(BaseTestRunnerEngine):

    def form_execution_command(self, execution_arguments, tests_to_run):
        return execution_arguments + " " + " ".join(tests_to_run)

    def execute_tests(self, execution_arguments, coverage_arguments, tests_to_run, test_info):
        """ Execute all the tests in tests to run, feeding in the arguments in execution arguments to our test runner. Generate coverage of these tests and return this data.

        Args:
            execution_arguments(List): List of arguments to pass through to Pytest
            coverage_arguments (List): List of arguments to pass through to the Python Coverage module.
            tests_to_run(List): List of the tests to run
            test_info(Map): Map with qualified names of tests as the key, and a namedtuple TestInfo containing the path to the test file and the name to be passed to the test runner to execute the test.
        """

        test_execution_command = self.form_execution_command(
            execution_arguments, self.extract_test_nodeids(test_info, tests_to_run))
        
        coverage_generator = PytestCoverageGenerator(
            test_execution_command, coverage_arguments)
        completed_process = coverage_generator.generate_coverage()
        result = coverage_generator.load_coverage()
        return (result, completed_process.returncode)
        
    def get_tests_to_execute(self, tests_to_run, test_info):
        """     
        Returns a list of pytest nodeids that can be fed into pytest to be executed. Used in no-execution mode.

        Args:
            tests_to_run (List): List of tests to execute
            test_info(Map): Map with qualified names of tests as the key, and a namedtuple TestInfo containing the path to the test file and the name to be passed to the test runner to execute the test.

        Returns:
            List: List of tests in a form that can be used by the test runner to execute all selected tests.
        """
        return self.extract_test_nodeids(test_info, tests_to_run)

    def extract_test_nodeids(self, test_info, tests_to_run):
        """Extracts a list of nodeids from our list of tests to run.

        Args:
            tests_to_run (List): List of tests to execute
            test_info(Map): Map with qualified names of tests as the key, and a namedtuple TestInfo containing the path to the test file and the name to be passed to the test runner to execute the test.

        Returns:
            List: List of tests in a form that can be used by the test runner to execute all selected tests.
        """
        nodeids = []
        for (key, test) in test_info.items():
            if key in tests_to_run:
                nodeids.append(test.nodeid)

        return nodeids
