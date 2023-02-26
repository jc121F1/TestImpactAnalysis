from enum import Enum
from pathlib import Path
import re
import pkgutil
import modulefinder
from .test_selection_logger import get_logger

logger = get_logger(__file__)


class TestSelectionPolicy(Enum):
    SELECT_ALL = "all"
    SELECT_COVERING_TESTS = "covering_tests"
    SELECT_COVERING_AND_DEPENDENCIES = "covering_tests_and_dependencies"


class TestSelectionEngine:

    def __init__(self, test_selection_policy: TestSelectionPolicy):
        self.test_selection_mode = test_selection_policy

    def select_tests(self, changelist: list, coverage_map: map, test_info: list, source_directories=[], library_directories=[]):
        tests_to_execute = []
        if self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_TESTS:
            tests_to_execute = self.select_covering_tests(
                changelist, coverage_map, test_info)
        elif self.test_selection_mode == TestSelectionPolicy.SELECT_ALL:
            tests_to_execute = test_info.keys()
        elif self.test_selection_mode == TestSelectionPolicy.SELECT_COVERING_AND_DEPENDENCIES:
            tests_to_execute = self.select_covering_tests_and_dependencies(
                changelist, coverage_map, test_info, source_directories, library_directories)

        return list(set(tests_to_execute))

    def select_covering_tests(self, changelist, coverage_map, test_info):
        tests_to_execute = []
        for changed_file in changelist:
            try:
                if (coverage_data := coverage_map[changed_file.path]):
                    tests_to_execute += coverage_data
            except (KeyError) as e:
                logger.warning(
                    f"File {changed_file.path} was changed but we have no coverage data available for this file. Executing all tests.")
                return list(test_info.keys())
        return tests_to_execute

    def select_covering_tests_and_dependencies(self, changelist, coverage_map, test_info, source_directories, library_directories):
        if not source_directories:
            logger.warning(
                "Source directories were not provided, select covering tests and dependencies policy may not be accurately selecting dependencies.")

        if not library_directories:
            logger.warning(
                "Library directories were not provided, select covering tests and depdencies policy may not be accurately selecting dependencies and may take an excessive amount of time.")

        library_directories = [
            "venv\Lib\site-packages"]

        def get_modules_in_directory(directory):
            """Returns a list of module names in the specified directory. Explores packages and imports all modules of a package"""
            modules = []
            for importer, name, ispkg in pkgutil.iter_modules([directory]):
                if not ispkg:
                    modules.append(name)
                else:
                    full_path = f"{directory}/{name}"
                    submodules = get_modules_in_directory(full_path)
                    for submodule in submodules:
                        modules.append(f"{name}.{submodule}")
            return modules

        lib_modules = []
        for lib_dir in library_directories:
            lib_modules.extend(get_modules_in_directory(lib_dir))

        import_map = {}
        mf = modulefinder.ModuleFinder(
            source_directories, excludes=lib_modules)


        def get_module_file_relative_to_cwd(module_pair):
            path = module_pair[1].__file__
            if path:
                return Path(path).relative_to(Path.cwd())
            return None

        for file in Path.cwd().rglob("*.py"):
            skip = False
            for dir in library_directories:
                dir_p = Path(dir).resolve()
                file_p = file.resolve()
                if file_p.is_relative_to(dir_p):
                    skip = True
            if not skip:
                mf.run_script(str(file))
                modules = map(get_module_file_relative_to_cwd, mf.modules.items())
                import_map[str(file)] = modules

        dependencies = []

        for changed_file in changelist:
            p = Path(changed_file.path)
            for file, modules in import_map.items():
                m = list(modules)
                if p in m:
                    dependencies.append(file)

        return dependencies
