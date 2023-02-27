from enum import Enum


class TestArchitectures(Enum):
    PyTest = "pytest"

class ChangelistGenerators(Enum):
    Git = "git"