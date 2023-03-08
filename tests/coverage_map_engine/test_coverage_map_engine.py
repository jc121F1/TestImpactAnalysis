import pytest
from git import Repo, DiffIndex
from pathlib import Path
from changelist_generator.git_changelist_generator import GitChangeListGenerator
from coverage_map.coverage_map_engine import CoverageMapEngine
from storage import RetentionPolicy as RP, StorageMode as SM, LocalCoverageMapStorage as LocalStorage
import os
import shutil
from collections import namedtuple
import coverage_map


class TestCoverageMapEngine():

    @pytest.fixture
    def local_storage_mock(self, mocker):
        return mocker.patch('storage.LocalCoverageMapStorage')

    @pytest.fixture
    def generator_mock(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def engine(self, mocker,  local_storage_mock, generator_mock):
        coverage_dir = Path('/test')
        storage_mode = SM.LOCAL
        retention_policy = RP.KEEP_ALL
        test_runner_args = []
        coverage_args = []
        return CoverageMapEngine(
            coverage_dir, storage_mode, retention_policy,
            generator_mock, test_runner_args, coverage_args
        )

    def test_initialise_storage_local_policy(self, engine, local_storage_mock, mocker):
        # Setup
        engine.storage_mode = SM.LOCAL

        # Execute
        engine.initialise_storage()

        # Assert
        assert isinstance(engine.storage, LocalStorage)

    def test_initialise_storage_invalid_policy(self, engine):
        # Setup
        engine.storage_mode = None

        # Execute and Assert
        with pytest.raises(ValueError):
            engine.initialise_storage()

    def test_retrieve_coverage_storage_has_map(self, engine):
        # Setup
        engine.storage.map = []

        # Execute
        result = engine.retrieve_coverage()

        # Assert
        assert result is not None

    def test_retrieve_coverage_storage_has_no_map(self, engine, mocker):
        # Setup
        engine.storage.map = None
        engine.storage.load_map = mocker.MagicMock()
        # Execute
        result = engine.retrieve_coverage()

        # Assert
        assert result is None

    def test_store_coverage(self, engine, local_storage_mock, mocker):
        # Setup
        store_this = {"cool": "things"}
        mock_save = mocker.MagicMock()
        engine.storage.save_map = mock_save
        # Execute
        engine.store_coverage(store_this)

        # Assert
        mock_save.assert_called_with(store_this)

    def test_generate_coverage_coverage_exists(self, engine, local_storage_mock, generator_mock, mocker):
        # Setup
        engine.storage.map = ["test"]
        engine.storage.load_map = mocker.MagicMock()

        # Execute
        engine.generate_coverage()

        # Assert
        assert engine.coverage_map == ["test"]
        generator_mock.assert_not_called()

    def test_generate_coverage_coverage_does_exist(self, engine, local_storage_mock, generator_mock, mocker):
        # Setup
        engine.storage.map = None
        engine.storage.load_map = mocker.MagicMock()
        # Execute
        engine.generate_coverage()

        # Assert
        generator_mock.assert_called()

    def test_has_coverage_no_coverage(self, engine):
        # Setup
        engine.coverage_map = None
        
        # Execute
        result = engine.has_coverage

        # Assert
        assert result is False

    def test_has_coverage_has_coverage_map(self, engine):
        # Setup
        engine.coverage_map = ["Test"]

        # Execute
        result = engine.has_coverage

        # Assert
        assert result is True
