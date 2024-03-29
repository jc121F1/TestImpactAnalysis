import pytest
import os
import uuid
from git import NoSuchPathError, InvalidGitRepositoryError, DiffIndex, GitCommandError
import pathlib
from changelist_generator.git_changelist_generator import GitChangeListGenerator as ChangeListGenerator, ChangeInfo 

def test_init_generator_valid_file_path(test_repository):
    repo_obj = test_repository[0]
    repo_dir = test_repository[1]
    assert (isinstance(ChangeListGenerator(repo_dir), ChangeListGenerator))


def test_init_generator_invalid_file_path():
    repo_dir = "fake_test_dir"
    with pytest.raises(NoSuchPathError):
        cg = ChangeListGenerator(repo_dir)
        cg.repo.close()


def test_init_generator_valid_file_path_no_repo():
    repo_dir = str(uuid.uuid1())
    try:
        os.mkdir(repo_dir)
        with pytest.raises(InvalidGitRepositoryError):
            cg = ChangeListGenerator(repo_dir)
            cg.repo.close()
    finally:
        os.rmdir(repo_dir)

def test_valid_commits(test_repository):
    repo_obj = test_repository[0]
    repo_dir = test_repository[1]
    commits = []
    file_name = "file_"
    for i in range(1, 3):
        this_file_name = file_name + str(i)
        with open(os.path.join(repo_dir, this_file_name), "w") as f:
            f.write("")
        repo_obj.git.add(all=True)
        repo_obj.index.commit(f"Test commit {i}")
        commits.append(repo_obj.head.commit)
    
    init = commits[0]
    final = commits[1]

    cg = ChangeListGenerator(repo_dir)
    assert isinstance(cg.get_changelist(init, final), list)
    cg.repo.close()

def test_invalid_init_commit(test_repository):
    repo_obj = test_repository[0]
    repo_dir = test_repository[1]
    commits = []
    file_name = "file_"
    for i in range(1, 3):
        this_file_name = file_name + str(i)
        with open(os.path.join(repo_dir, this_file_name), "w") as f:
            f.write("")
        repo_obj.git.add(all=True)
        repo_obj.index.commit(f"Test commit {i}")
        commits.append(repo_obj.head.commit)
    
    init = "test"
    final = commits[1]

    cg = ChangeListGenerator(repo_dir)
    with pytest.raises(Exception):
        cg.get_changelist(init, final)

    cg.repo.close()


def test_invalid_final_commit(test_repository):
    repo_obj = test_repository[0]
    repo_dir = test_repository[1]
    commits = []
    file_name = "file_"
    for i in range(1, 3):
        this_file_name = file_name + str(i)
        with open(os.path.join(repo_dir, this_file_name), "w") as f:
            f.write("")
        repo_obj.git.add(all=True)
        repo_obj.index.commit(f"Test commit {i}")
        commits.append(repo_obj.head.commit)

    init = commits[0]
    final = "test"

    cg = ChangeListGenerator(repo_dir)
    with pytest.raises(Exception):
        cg.get_changelist(init, final)

    cg.repo.close()