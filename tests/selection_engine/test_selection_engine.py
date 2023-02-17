import pytest
from git import Repo, DiffIndex
from pathlib import Path
from change_list_generator import ChangeListGenerator
from test_selection import TestSelectionEngine, TestSelectionPolicy
import os
import shutil
from unittest import mock
import coverage_map

class MockObj(object):
    pass

@mock.patch('coverage_map.CoverageMapEngine')
def test_valid_selection_inputs(mock_coverage_map):
    # Setup
    changelist = []
    file1 = MockObj()
    file1.a_path = "file1.py"
    changelist.append(file1)
    
    test_selection_policy = TestSelectionPolicy.SELECT_COVERING_TESTS
    coverage_dir = Path('/path/to/coverage_dir')
    test_runner_args = 'some test runner args'
    coverage_args = 'some coverage args'
    mock_coverage_map_engine = mock_coverage_map.return_value
    mock_coverage_map_engine.coverage_map = {'all_tests': [
        'test1', 'test2','test3',], 'file1.py': ['test1', 'test3'], 'file2.py': ['test2'], 'file3.py' : []}

    # Test
    engine = TestSelectionEngine(
        changelist, test_selection_policy, coverage_dir, test_runner_args, coverage_args)
    tests_to_execute = engine.select_tests()


    # Assert
    assert set(tests_to_execute) == set(['test1', 'test3'])
