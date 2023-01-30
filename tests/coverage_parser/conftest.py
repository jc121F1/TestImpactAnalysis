from pathlib import Path
import pytest
import json

JSON_TEST_FILE_PATH = "test_json.json"


@pytest.fixture
def test_data_file():
    path = Path(JSON_TEST_FILE_PATH)
    with open(path) as file:
        return json.load(file)
