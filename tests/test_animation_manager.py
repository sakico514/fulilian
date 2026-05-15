import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from PyQt6.QtWidgets import QApplication, QLabel
from animation_manager import AnimationManager, STATE_GIF_MAP


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestStateGifMap:
    def test_has_nine_states(self):
        assert len(STATE_GIF_MAP) == 9

    def test_idle_mapped(self):
        assert STATE_GIF_MAP["idle"] == "idle.gif"

    def test_all_states_end_with_gif(self):
        for state, filename in STATE_GIF_MAP.items():
            assert filename.endswith(".gif"), f"{state} -> {filename}"


class TestAnimationManager:
    @pytest.fixture
    def assets_dir(self, tmp_path):
        d = tmp_path / "assets"
        d.mkdir()
        for name in ["idle.gif", "running.gif", "jumping.gif",
                     "waving.gif", "waiting.gif", "failed.gif",
                     "review.gif", "running-left.gif", "running-right.gif"]:
            (d / name).write_bytes(b"GIF89a\x00\x00\x00\x00;")
        return str(d)

    def test_load_all_gifs_success(self, qapp, assets_dir):
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        assert len(mgr.movies) == 9
        assert "idle" in mgr.movies

    def test_load_missing_gif_skips(self, qapp, assets_dir):
        os.remove(os.path.join(assets_dir, "failed.gif"))
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        assert "failed" not in mgr.movies
        assert len(mgr.movies) == 8

    def test_current_state_starts_none(self, qapp, assets_dir):
        mgr = AnimationManager(assets_dir)
        assert mgr.current_state is None

    def test_switch_state_updates_current(self, qapp, assets_dir):
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        mgr.switch_state("jumping")
        assert mgr.current_state == "jumping"

    def test_switch_state_unknown_does_nothing(self, assets_dir):
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        mgr.switch_state("idle")  # Set a known state first
        mgr.switch_state("nonexistent")
        assert mgr.current_state == "idle"  # Should not change

    def test_set_label_and_switch_integration(self, assets_dir, qapp):
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        label = QLabel()
        mgr.set_label(label)
        mgr.switch_state("idle")
        assert mgr.current_state == "idle"
        # The label should now have a movie set
        assert label.movie() is not None
