import pytest
import shutil
import os
from git import Repo

TEST_FOLDER_KEY = "test_dir"

@pytest.fixture
def test_repository():
    """Fixture to setup and teardown a test repository for our git based tests.
    """
    repo_dir = os.path.join(TEST_FOLDER_KEY, "test_repo")
    r = Repo.init(repo_dir)
    
    yield (r, repo_dir)
    
    shutil.rmtree(TEST_FOLDER_KEY, ignore_errors=True)