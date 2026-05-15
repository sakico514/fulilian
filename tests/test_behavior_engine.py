import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from behavior_engine import BehaviorEngine


class FakeAnimManager:
    def __init__(self):
        self.last_state = None
        self.movies = {s: True for s in [
            "idle", "running", "running-left", "running-right",
            "jumping", "waving", "waiting", "failed", "reviewing"
        ]}

    def switch_state(self, state):
        self.last_state = state


class TestBehaviorEngine:
    @pytest.fixture
    def engine(self):
        anim = FakeAnimManager()
        return BehaviorEngine(anim)

    def test_initial_state_is_idle(self, engine):
        assert engine.state == "idle"

    def test_set_state_switches_animation(self, engine):
        engine.set_state("jumping")
        assert engine.state == "jumping"
        assert engine.anim.last_state == "jumping"

    def test_set_state_unknown_falls_back(self, engine):
        engine.set_state("idle")
        engine.set_state("nonexistent")
        assert engine.state == "idle"

    def test_do_random_action_changes_state(self, engine):
        engine.set_state("idle")
        engine.do_random_action()
        assert engine.state in engine.auto_actions

    def test_react_to_click_picks_reaction(self, engine):
        engine.react_to_click()
        assert engine.state in engine.reaction_states

    def test_react_to_double_click_is_jumping(self, engine):
        engine.react_to_double_click()
        assert engine.state == "jumping"

    def test_auto_actions_are_five(self, engine):
        assert len(engine.auto_actions) == 5

    def test_reaction_states_are_six(self, engine):
        assert len(engine.reaction_states) == 6
