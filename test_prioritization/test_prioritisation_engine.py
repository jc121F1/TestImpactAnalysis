from enum import Enum
import pytest


class TestPrioritisationPolicy(Enum):
    ALPHABETICAL = 1
    BY_CHANGE_PERCENTAGE = 2


class TestPrioritisationEngine():
    """
    Class responsible for sorting selected tests into an order for execution.
    """

    def __init__(self, test_prioritisation_policy: TestPrioritisationPolicy):
        self.prioritisation_policy = test_prioritisation_policy

    def prioritise_tests(self, selected_tests: list):
        if self.prioritisation_policy == TestPrioritisationPolicy.ALPHABETICAL:
            return sorted(selected_tests)
