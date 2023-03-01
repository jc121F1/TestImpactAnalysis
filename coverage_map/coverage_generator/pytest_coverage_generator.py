
from .coverage_parser import CoverageParserAndProcessor as Parser
from .base_coverage_generator import BaseCoverageGenerator
from .logger import get_logger
import uuid
import subprocess
from pathlib import Path
import shutil
import os

logger = get_logger(__file__)

#TODO WE NEED TO COLLECT TESTS BETTER

class PytestCoverageGenerator(BaseCoverageGenerator):

    unique_id = uuid.uuid4()

    def __init__(self, test_runner_args, coverage_args):
        """        Initialise CoverageGenerator class. Sets up file names and builds our commandline arguments.

        Args:
            test_runner_args (List[String]): List of arguments to pass through to our coverage tool.
            coverage_args (List[String]): List of arguments to pass through to the test runner we use to run tests and generate coverage.
        """
        self.create_storage()
        self.coverage_file = Path(f"{str(self.unique_id)}/coverage_data.coverage")
        self.report_file = Path(f"{str(self.unique_id)}/coverage_report.json")
        self.xml_file = Path(f"{str(self.unique_id)}/test_xml.xml")
        self.coverage_subprocess = "coverage run " + coverage_args + \
            f"--data-file=\"{self.coverage_file}\" " + test_runner_args

    def create_storage(self):
        """
        Create storage folder for storing generated coverage data
        """
        try:
            os.mkdir(Path.cwd().joinpath(f"{str(self.unique_id)}"))
        except Exception as e:
            pass

    def delete_storage(self):
        """
        Delete storage folder used for storing generated coverage data
        """
        try:
            shutil.rmtree(Path.cwd().joinpath(f"{str(self.unique_id)}"))
        except Exception as e:
            pass

    def generate_coverage(self):
        """
        Generate coverage data for our tests.
        """
        logger.info(
            f"Executing coverage generation with the following arguments: {self.coverage_subprocess}")
        coverage_result = subprocess.run(
            self.coverage_subprocess, capture_output=True)
        logger.info(f"Testing returned with ExitCode: {coverage_result.returncode}.")
        report_result = subprocess.run(
            f"coverage json --data-file={self.coverage_file} -o {self.report_file} --show-contexts", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logger.info(
            f"Converting coverage report to JSON returned with ExitCode: {report_result.returncode}")
        return coverage_result

    def load_coverage(self):
        """
        Load our generated coverage info using a CoverageParser and return the resulting coverage data. 
        Will raise a ValueError if coverage data is not found.

        Return:
            Coverage data generated in generate coverage.
        """
        if self.coverage_file.exists():
            self.coverage_parser = Parser(self.report_file)
            return self.coverage_parser.coverage
        raise ValueError("Coverage file does not exist")

    def __del__(self):
        """
        Calls delete storage when this object is GCed to ensure artifacts aren't left orphaned.
        """
        self.delete_storage()
