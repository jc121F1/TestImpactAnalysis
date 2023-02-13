from pathlib import Path


class CoverageMapEngine():

    def __init__(self, coverage_dir: Path):
        self.coverage_dir = coverage_dir
        if ((coverage := self.retrieve_coverage(coverage_dir))):
            # return coverage map
            pass
        else:
            # generate coverage
            pass

    def retrieve_coverage(coverage_dir: str):
        pass
