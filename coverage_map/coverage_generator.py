import subprocess
from coverage_map.coverage_parser import CoverageParserAndProcessor as Parser
from pathlib import Path
import shutil
import os


class CoverageGenerator():

    def __init__(self, pytest_args, coverage_args):
        self.create_storage()
        self.coverage_file = Path("coverage_dir/coverage_data.coverage")
        self.report_file = Path("coverage_dir/coverage_report.json")
        pytest_exec_args = "pytest " + pytest_args
        self.coverage_subprocess = "coverage run " + coverage_args + \
            f"--data-file=\"{self.coverage_file}\"" + " -m " + pytest_exec_args

    def create_storage(self):
        try:
            os.mkdir(Path.cwd().joinpath("coverage_dir"))
        except Exception as e:
            pass
    
    def delete_storage(self):
        try:
            shutil.rmtree(Path.cwd().joinpath("coverage_dir"))
        except Exception as e:
            pass

    def generate_coverage(self):
        print(self.coverage_subprocess)
        result = subprocess.run(self.coverage_subprocess)
        subprocess.run(
            f"coverage json --data-file={self.coverage_file} -o {self.report_file} --show-contexts")

    def load_coverage(self):
        if self.coverage_file.exists():
            self.coverage_parser = Parser(self.report_file)
            self.delete_storage()
            return self.coverage_parser.coverage
        raise ValueError("Coverage file does not exist")