"""Unit tests for states.py — state enum validation."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from states import State

class TestStates:
    def test_all_core_states_exist(self):
        required = ['INIT', 'CONNECTING', 'ARMING', 'TAKEOFF', 'SEARCH',
                     'CENTERING', 'DESCENDING', 'VERIFY', 'LANDING', 'DONE',
                     'MANUAL', 'HOVER', 'APPROACH', 'RETURN_TO_SEARCH',
                     'RETURN_HOME', 'PRE_WAYPOINTS', 'TRANSIT_TO_SEARCH',
                     'HOVER_TARGET', 'RETURN_TRANSIT', 'RETURN_FROM_MANUAL']
        for s in required:
            assert hasattr(State, s), f"Missing state: {s}"

    def test_states_are_strings(self):
        for attr in dir(State):
            if not attr.startswith('_'):
                assert isinstance(getattr(State, attr), str)

    def test_state_values_unique(self):
        vals = [getattr(State, a) for a in dir(State) if not a.startswith('_')]
        assert len(vals) == len(set(vals)), "Duplicate state values found"

    def test_state_name_matches_value(self):
        for attr in dir(State):
            if not attr.startswith('_'):
                assert attr == getattr(State, attr)

    def test_minimum_state_count(self):
        count = len([a for a in dir(State) if not a.startswith('_')])
        assert count >= 18, f"Expected >= 18 states, got {count}"
