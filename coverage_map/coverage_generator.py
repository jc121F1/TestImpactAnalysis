import subprocess

class CoverageGenerator():

    def __init__(self, pytest_args, coverage_args):
        pytest_exec_args = "pytest" + pytest_args
        self.coverage_subprocess = "coverage run -m " + pytest_exec_args + " " + coverage_args

    def generate_coverage(self):
        result = subprocess.run(self.coverage_subprocess, shell=True)
        print(result)

cg = CoverageGenerator("", "")