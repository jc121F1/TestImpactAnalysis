from pathlib import Path
from storage import LocalCoverageMapStorage as LocalStorage
from storage import StorageMode as SM, RetentionPolicy as RP


class CoverageMapEngine():
    """
    A class representing a coverage map engine for generating and storing code coverage information.

    Attributes:
    - coverage_map: A dictionary representing the coverage information.
    - coverage_dir: A Path object representing the directory where coverage data will be stored.
    - storage_mode: A StorageMode enum value indicating where the coverage data will be stored.
    - storage_retention_policy: A RetentionPolicy enum value indicating the retention policy for coverage data.
    - generator_class: The class for the coverage generator to be used.
    - test_runner_args: The arguments for the test runner.
    - coverage_args: The arguments for the coverage generator.

    Methods:
    - initialise_storage(): Initializes the storage based on the storage mode.
    - retrieve_coverage(): Retrieves the coverage data from the storage.
    - store_coverage(coverage_map): Stores the coverage data in the storage.
    - generate_coverage(): Generates the coverage data and stores it in the coverage map.
    - has_coverage: Returns True if the coverage map has any data, else False.
    """

    coverage_map = {}

    def __init__(self, coverage_dir: Path, storage_mode: SM, storage_retention_policy: RP, generator_class, test_runner_args, coverage_args):
        """
        Constructs a new CoverageMapEngine object with the specified parameters.

        Args:
        - coverage_dir: A Path object representing the directory where coverage data will be stored.
        - storage_mode: A StorageMode enum value indicating where the coverage data will be stored.
        - storage_retention_policy: A RetentionPolicy enum value indicating the retention policy for coverage data.
        - generator_class: The class for the coverage generator to be used.
        - test_runner_args: The arguments for the test runner.
        - coverage_args: The arguments for the coverage generator.
        """
        self.coverage_dir = coverage_dir
        self.storage_mode = storage_mode
        self.storage_retention_policy = storage_retention_policy
        self.test_runner_args = test_runner_args
        self.coverage_args = coverage_args
        self.generator_class = generator_class
        self.initialise_storage()

    def initialise_storage(self):
        """
        Initializes the storage based on the storage mode.
        """
        if self.storage_mode == SM.LOCAL:
            self.storage = LocalStorage(
                self.coverage_dir, self.storage_retention_policy)
        else:
            raise ValueError("Selected storage mode is not implemented. Check again.")

    def retrieve_coverage(self):
        """
        Retrieves the coverage data from the storage.

        Returns:
        - The coverage map if it exists in the storage, else None.
        """
        self.storage.load_map()
        if (self.storage.has_map):
            return self.storage.map
        return None

    def store_coverage(self, coverage_map: dict):
        """
        Stores the coverage data in the storage media.

        Args:
        - coverage_map: A dictionary representing the coverage information to be stored.
        """
        self.storage.save_map(coverage_map)

    def generate_coverage(self):
        """
        Generates the coverage data and stores it in the coverage map.
        If the coverage data already exists in the storage, it is retrieved from there.
        """
        if (coverage := self.retrieve_coverage()):
            self.coverage_map = coverage
        else:
            generator = self.generator_class(
                self.test_runner_args, self.coverage_args)
            generator.generate_coverage()
            self.coverage_map = generator.load_coverage()

    @property
    def has_coverage(self):
        """
        Returns True if the coverage map has any data, else False.
        """
        if self.coverage_map:
            return True
        return False
