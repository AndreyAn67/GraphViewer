from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication


THEME_DIR = Path(__file__).resolve().parent

VALID_MODES = ("light", "dark", "system")


class ThemeManager(QObject):
    """Manages QSS theme application with three user-selectable modes.

    Modes:
        "light"  — always light.qss
        "dark"   — always dark.qss
        "system" — follow OS color scheme, re-resolve on system change

    Signals:
        themeChanged(str)  — emitted with the *resolved* theme ("light"/"dark")
                              whenever the on-screen theme changes.
        modeChanged(str)   — emitted with the *user-selected* mode
                              ("light"/"dark"/"system") when the mode changes.
    """

    themeChanged = Signal(str)
    modeChanged = Signal(str)

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._mode: str = "system"
        self._current: str = "dark"

        hints = QGuiApplication.styleHints()
        if hints is not None:
            try:
                hints.colorSchemeChanged.connect(self._on_system_scheme_changed)
            except (AttributeError, TypeError):
                # Qt < 6.5 lacks the signal; system mode then resolves once at apply time.
                pass

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def current(self) -> str:
        return self._current

    def apply(self, name: str) -> None:
        """Legacy entry point — accepts a mode name ('light'/'dark'/'system')."""
        self.set_mode(name)

    def set_mode(self, mode: str) -> None:
        if mode not in VALID_MODES:
            return
        self._mode = mode
        self.modeChanged.emit(mode)
        self._reapply()

    def toggle(self) -> None:
        """Cycle through modes: dark → light → system → dark."""
        nxt = {"dark": "light", "light": "system", "system": "dark"}[self._mode]
        self.set_mode(nxt)

    # ---- internals ----

    def _resolve(self) -> str:
        if self._mode == "system":
            return self._detect_system()
        return self._mode

    @staticmethod
    def _detect_system() -> str:
        hints = QGuiApplication.styleHints()
        if hints is None:
            return "dark"
        try:
            scheme = hints.colorScheme()
        except AttributeError:
            return "dark"
        if scheme == Qt.ColorScheme.Light:
            return "light"
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
        return "dark"

    def _reapply(self) -> None:
        target = self._resolve()
        qss_file = THEME_DIR / f"{target}.qss"
        if not qss_file.is_file():
            # Fall back to the other theme if the resolved file is missing.
            fallback = "dark" if target == "light" else "light"
            qss_file = THEME_DIR / f"{fallback}.qss"
            if not qss_file.is_file():
                return
            target = fallback
        qss = qss_file.read_text(encoding="utf-8")
        self._app.setStyleSheet(qss)
        if target != self._current:
            self._current = target
            self.themeChanged.emit(target)
        else:
            # Re-emit so listeners can refresh derived labels (e.g. "跟随系统(深色)")
            self.themeChanged.emit(target)

    def _on_system_scheme_changed(self, _scheme) -> None:
        if self._mode == "system":
            self._reapply()
