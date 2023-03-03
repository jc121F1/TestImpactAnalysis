import pytest
from test_prioritization import TestPrioritisationEngine, TestPrioritisationPolicy


class TestTestPrioritisationEngine:
    def test_prioritisation_policy_alphabetical(self):
        # Arrange
        selected_tests = ['test_b', 'test_a', 'test_c']
        engine = TestPrioritisationEngine(
            TestPrioritisationPolicy.ALPHABETICAL)

        # Act
        prioritised_tests = engine.prioritise_tests(selected_tests)

        # Assert
        assert prioritised_tests == ['test_a', 'test_b', 'test_c']

    def test_prioritisation_policy_by_change_percentage(self):
        # Arrange
        selected_tests = ['test_b', 'test_a', 'test_c']
        engine = TestPrioritisationEngine(
            TestPrioritisationPolicy.BY_CHANGE_PERCENTAGE)

        # Act/Assert
        with pytest.raises(ValueError) as e:
            engine.prioritise_tests(selected_tests)
        assert str(
            e.value) == f"Policy {TestPrioritisationPolicy.BY_CHANGE_PERCENTAGE} not currently supported"
