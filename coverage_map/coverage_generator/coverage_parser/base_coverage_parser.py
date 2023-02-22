from abc import ABC, abstractclassmethod, abstractproperty
from pathlib import Path
class BaseCoverageParserAndProcessor(ABC):

    @abstractclassmethod
    def __init__(self, filepath: Path):
        """
        Initialise CoverageParserAndProcessor and execute the loading, parsing, and processing of the coverage data stored at filepath.

        Args:
            filepath (pathlib.Path): Path to the file that contains our coverage data in json format.
        """
        pass

    @abstractproperty
    def coverage(self):
        """Getter for our coverage data

        Returns:
            dict: Dictionary containing a map of each file as the key and the tests that cover it as the value
        """
        pass
