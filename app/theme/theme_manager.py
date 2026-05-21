from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


THEME_DIR = Path(__file__).resolve().parent


class ThemeManager(QObject):
    themeChanged = Signal(str)

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._current = "dark"

    @property
    def current(self) -> str:
        return self._current

    def apply(self, name: str) -> None:
        qss_file = THEME_DIR / f"{name}.qss"
        if not qss_file.is_file():
            return
        qss = qss_file.read_text(encoding="utf-8")
        self._app.setStyleSheet(qss)
        self._current = name
        self.themeChanged.emit(name)

    def toggle(self) -> None:
        target = "light" if self._current == "dark" else "dark"
        qss_file = THEME_DIR / f"{target}.qss"
        if not qss_file.is_file():
            # Target theme not shipped yet (light.qss is Phase 2).
            # Leave _current unchanged so a future click can try again.
            return
        self.apply(target)
