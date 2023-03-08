import pytest
from git import Repo, DiffIndex
from pathlib import Path
from changelist_generator.git_changelist_generator import GitChangeListGenerator
from test_selection import TestSelectionEngine, TestSelectionPolicy
import os
import shutil
from unittest import mock
from collections import namedtuple
import coverage_map

class TestSelectCoveringTests:
    ChangedFile = namedtuple('ChangedFile', ['path', 'change_type'])

    def test_select_covering_tests_for_existing_coverage_data(self):
        # Setup
        changelist = [self.ChangedFile(path='file1.py', change_type='M'), self.ChangedFile(
            path='file2.py', change_type='M')]
        coverage_map = {'file1.py': [
            'test_file1.py'], 'file2.py': ['test_file2.py']}
        test_info = {'test_file1.py': ('file1.py', 'unique_identifier_1'), 'test_file2.py': (
            'file2.py', 'unique_identifier_2'), 'test_file3.py': ('file3.py', 'unique_identifier_3')}
        te = TestSelectionEngine(TestSelectionPolicy.SELECT_COVERING_TESTS)

        # Execution
        selected_tests = te.select_tests(
            changelist, coverage_map, test_info)

        # Assertion
        assert sorted(selected_tests) == sorted(['test_file1.py', 'test_file2.py'])

    def test_select_covering_tests_for_missing_coverage_data(self):
        # Setup
        changelist = [self.ChangedFile(path='file1.py', change_type='M'), self.ChangedFile(
            path='file2.py', change_type='M')]
        coverage_map = {'file1.py': [
            'test_file1.py'], 'file3.py': ['test_file3.py']}
        test_info = {'test_file1.py': ('file1.py', 'unique_identifier_1'), 'test_file2.py': (
            'file2.py', 'unique_identifier_2'), 'test_file3.py': ('file3.py', 'unique_identifier_3')}
        te = TestSelectionEngine(TestSelectionPolicy.SELECT_COVERING_TESTS)

        # Execution
        selected_tests = te.select_tests(
            changelist, coverage_map, test_info)

        # Assertion
        assert sorted(selected_tests) == sorted(list(test_info.keys()))

    def test_select_covering_tests_for_missing_coverage_map_data(self):
        # Setup
        changelist = [self.ChangedFile(path='file1.py', change_type='M'), self.ChangedFile(
            path='file2.py', change_type='M')]
        coverage_map = {'file1.py': ['test_file1.py']}
        test_info = {'test_file1.py': ('file1.py', 'unique_identifier_1'), 'test_file2.py': (
            'file2.py', 'unique_identifier_2'), 'test_file3.py': ('file3.py', 'unique_identifier_3')}
        te = TestSelectionEngine(TestSelectionPolicy.SELECT_COVERING_TESTS)

        # Execution
        selected_tests = te.select_tests(
            changelist, coverage_map, test_info)

        # Assertion
        assert sorted(selected_tests) == sorted(['test_file1.py', 'test_file2.py', 'test_file3.py'])

    def test_select_covering_tests_for_missing_changelist_data(self):
        # Setup
        changelist = []
        coverage_map = {'file1.py': ['test_file1.py']}
        test_info = {'test_file1.py': ('file1.py', 'unique_identifier_1'), 'test_file2.py': (
            'file2.py', 'unique_identifier_2'), 'test_file3.py': ('file3.py', 'unique_identifier_3')}
        te = TestSelectionEngine(TestSelectionPolicy.SELECT_COVERING_TESTS)

        # Execution
        selected_tests = te.select_tests(
            changelist, coverage_map, test_info)

        # Assertion
        assert selected_tests == []

    def test_select_policy_that_does_not_exist(self):
        changelist = []
        coverage_map = {'file1.py': ['test_file1.py']}
        test_info = {'test_file1.py': ('file1.py', 'unique_identifier_1'), 'test_file2.py': (
            'file2.py', 'unique_identifier_2'), 'test_file3.py': ('file3.py', 'unique_identifier_3')}
        te = TestSelectionEngine(None)

        # Execution and Assertion
        with pytest.raises(ValueError):
            selected_tests = te.select_tests(
                changelist, coverage_map, test_info)
