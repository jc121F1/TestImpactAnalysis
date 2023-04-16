from enum import Enum


class TestArchitectures(Enum):
    PyTest = "pytest"

class ChangelistGenerators(Enum):
    Git = "git"

class ExecutionMode(Enum):
    Execute = "execute"
    List_Only = "list"

class Verbosity(Enum):
    Normal = "Normal"
    Debug = "Debug"
    Silenced = "Silenced"