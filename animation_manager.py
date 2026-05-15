import os
from PyQt6.QtCore import QObject, QSize
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QLabel

STATE_GIF_MAP = {
    "idle": "idle.gif",
    "running": "running.gif",
    "running-left": "running-left.gif",
    "running-right": "running-right.gif",
    "jumping": "jumping.gif",
    "waving": "waving.gif",
    "waiting": "waiting.gif",
    "failed": "failed.gif",
    "reviewing": "review.gif",
}


class AnimationManager(QObject):
    def __init__(self, assets_dir: str, scale: float = 1.0, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.assets_dir = assets_dir
        self.scale = scale
        self.movies: dict[str, QMovie] = {}
        self.current_state: str | None = None
        self._label: QLabel | None = None
        self.target_size: QSize | None = None

    def set_label(self, label: QLabel) -> None:
        self._label = label

    def load_all(self) -> None:
        self.target_size = self._load_movies(1.0)  # load at native size first
        if self.target_size:
            self._apply_scale(self.scale)

    def _load_movies(self, scale: float) -> QSize | None:
        """Load all GIFs at given scale, return idle GIF's scaled size."""
        base_size = None
        for state, filename in STATE_GIF_MAP.items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                movie = QMovie(path)
                movie.setCacheMode(QMovie.CacheMode.CacheAll)
                self.movies[state] = movie
                if state == "idle":
                    movie.start()
                    pixmap = movie.currentPixmap()
                    movie.stop()
                    if not pixmap.isNull():
                        w = int(pixmap.width() * scale)
                        h = int(pixmap.height() * scale)
                        base_size = QSize(w, h)
        return base_size

    def _apply_scale(self, scale: float) -> None:
        """Apply a uniform scaled size to all loaded movies."""
        if not self.target_size:
            return
        self.scale = scale
        # Recompute target from idle movie's native size
        idle_movie = self.movies.get("idle")
        if idle_movie:
            idle_movie.start()
            pixmap = idle_movie.currentPixmap()
            idle_movie.stop()
            if not pixmap.isNull():
                w = int(pixmap.width() * scale)
                h = int(pixmap.height() * scale)
                self.target_size = QSize(w, h)
        for movie in self.movies.values():
            movie.setScaledSize(self.target_size)

    def set_scale(self, scale: float) -> QSize | None:
        self._apply_scale(scale)
        if self.current_state and self._label:
            movie = self.movies.get(self.current_state)
            if movie:
                self._label.setMovie(movie)
                movie.start()
        return self.target_size

    def switch_state(self, state: str) -> None:
        if state not in self.movies:
            return
        self.current_state = state
        if self._label is not None:
            movie = self.movies[state]
            self._label.setMovie(movie)
            movie.start()
