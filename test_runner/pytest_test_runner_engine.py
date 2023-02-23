import subprocess
from test_runner import get_logger, BaseTestRunnerEngine
from coverage_map.coverage_generator import PytestCoverageGenerator

logger = get_logger(__file__)


class PytestTestRunnerEngine(BaseTestRunnerEngine):

    def form_execution_command(self, execution_arguments, tests_to_run):
        return "-m pytest " + execution_arguments + " " + " ".join(tests_to_run)

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
        

    def extract_test_nodeids(self, test_info, tests_to_run):
        nodeids = []
        for (key, test) in test_info.items():
            if key in tests_to_run:
                nodeids.append(test.nodeid)

        return nodeids