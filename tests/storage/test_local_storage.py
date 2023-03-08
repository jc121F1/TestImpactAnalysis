import json
import os
import pytest
from pathlib import Path

from storage import BaseCoverageMapStorage, RetentionPolicy as RP
from storage.local_storage import LocalCoverageMapStorage

class TestLocalStorage():
    @pytest.fixture
    def storage_location(self, tmpdir):
        return Path(tmpdir) / "maps"


    @pytest.fixture
    def storage(self, storage_location):
        return LocalCoverageMapStorage(storage_location, RP.KEEP_ALL)


    @pytest.fixture
    def map(self, storage):
        return {"test1.py": {"test1": [1, 2, 3], "test2": [4, 5, 6]}, "test2.py": {"test1": [7, 8, 9], "test2": [10, 11, 12]}}


    def test_save_and_load_map(self, storage, map, storage_location):
        # save the map
        storage.save_map(map)

        # load the map
        storage.load_map()

        # check that the map was loaded correctly
        assert storage.map == map

        # check that the file was created
        assert os.path.exists(f"{storage_location}\\test_impact_map_{storage.id}.testimpact")

        # remove the file
        #os.remove(f"{storage_location}/test_impact_{storage.id}.json")


    def test_save_map_with_existing_location(self, storage, map, storage_location):
        # create the directory to store the coverage maps
        os.mkdir(storage_location)

        # save the map
        storage.save_map(map)

        # check that the file was created
        assert os.path.exists(
            f"{storage_location}\\test_impact_map_{storage.id}.testimpact")


    def test_save_map_with_existing_file(self, storage, map, storage_location):
        # create the directory to store the coverage maps
        os.mkdir(storage_location)

        # create an existing coverage map file
        existing_file = f"{storage_location}/test_impact_map.testimpact"
        with open(existing_file, "w") as f:
            json.dump({"test1.py": {"test1": [1, 2, 3], "test2": [4, 5, 6]}, "test2.py": {
                    "test1": [7, 8, 9], "test2": [10, 11, 12]}}, f)

        # save the map
        storage.save_map(map)

        # check that the file was created
        assert os.path.exists(
            f"{storage_location}\\test_impact_map_{storage.id}.testimpact")

        # check that the existing file was not deleted
        assert os.path.exists(existing_file)


    def test_apply_storage_policy_keep_all(self, storage, map, storage_location):
        # apply the storage policy
        storage.retention_policy = RP.KEEP_ALL
        # save the map 3 times
        storage.save_map(map)
        storage.id = "test"
        storage.save_map(map)
        storage.id = "test123123"
        storage.save_map(map)

        

        storage.apply_storage_policy()

        # check that all 3 files were kept
        assert len(list(storage_location.glob("*.testimpact"))) == 3