import subprocess
from test_runner import get_logger

logger = get_logger(__file__)

class TestRunnerEngine():

    def form_execution_command(self, execution_arguments, tests_to_run):
        return "pytest " + execution_arguments + " " + " ".join(tests_to_run)

    def execute_tests(self, execution_arguments, tests_to_run, test_info):

        test_execution_command = self.form_execution_command(
            execution_arguments, self.extract_test_nodeids(test_info, tests_to_run))
        logger.info(test_execution_command)
        subprocess.run(test_execution_command)

    def extract_test_nodeids(self, test_info, tests_to_run):
        nodeids = []
        for (key, test) in test_info.items():
            if key in tests_to_run:
                nodeids.append(test.nodeid)
        
        return nodeids
