import subprocess
from coverage_map.coverage_parser import CoverageParserAndProcessor as Parser
from coverage_map.coverage_map_logger import get_logger
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import os
import pytest

logger = get_logger(__file__)

#TODO WE NEED TO COLLECT TESTS BETTER

class CoverageGenerator():

    def __init__(self, test_runner_args, coverage_args):
        self.create_storage()
        self.coverage_file = Path("generated_coverage/coverage_data.coverage")
        self.report_file = Path("generated_coverage/coverage_report.json")
        self.xml_file = Path("generated_coverage/test_xml.xml")
        self.coverage_subprocess = "coverage run " + coverage_args + \
            f"--data-file=\"{self.coverage_file}\" " + test_runner_args

    def create_storage(self):
        try:
            os.mkdir(Path.cwd().joinpath("generated_coverage"))
        except Exception as e:
            pass

    def delete_storage(self):
        try:
            shutil.rmtree(Path.cwd().joinpath("generated_coverage"))
        except Exception as e:
            pass

    def generate_coverage(self):
        logger.info(
            f"Executing coverage generation with the following arguments: {self.coverage_subprocess}")
        coverage_result = subprocess.run(
            self.coverage_subprocess, capture_output=True)
        logger.info(f"Testing returned with ExitCode: {coverage_result.returncode}.")
        report_result = subprocess.run(
            f"coverage json --data-file={self.coverage_file} -o {self.report_file} --show-contexts", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logger.info(
            f"Converting coverage report to JSON returned with ExitCode: {report_result.returncode}")

    def load_coverage(self):
        if self.coverage_file.exists():
            self.coverage_parser = Parser(self.report_file)
            return self.coverage_parser.coverage
        raise ValueError("Coverage file does not exist")

    def __del__(self):
        self.delete_storage()
