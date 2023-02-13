import argparse
from coverage_map.coverage_parser import CoverageParserAndProcessor
import pathlib

FROM_COVERAGE = "from_coverage"


def parse_args():

    def file(file_path):
        if pathlib.Path(file_path).is_file():
            return file_path
        else:
            return ValueError("Error, file does not exist.")

    parser = argparse.ArgumentParser()

    parser.add_argument("--from_coverage",
                        type=file,
                        help="Path a valid coverage json file to be used to seed maps",
                        required=False)
    return parser.parse_args()


def main(args: dict):
    coverage_file = args.get(FROM_COVERAGE)
    if coverage_file:
        print(CoverageParserAndProcessor(coverage_file).get_file_names)


if __name__ == "__main__":
    main(vars(parse_args()))
