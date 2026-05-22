from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.scanner import scan_library
from app.i18n import Translator
from app.theme.theme_manager import ThemeManager
from app.views.free_view import FreeView
from app.views.grid_view import GridView
from app.views.single_view import SingleView
from app.widgets.mode_switcher import ViewMode
from app.widgets.status_bar import StatusBar
from app.widgets.top_bar import TopBar


class MainWindow(QMainWindow):
    def __init__(self, pics_root: Path, theme: ThemeManager) -> None:
        super().__init__()
        self.setWindowTitle("GraphViewer")
        self._pics_root = pics_root
        self._theme = theme
        self._i18n = Translator(default="zh")

        # ---- Scan library ----
        self._library = scan_library(pics_root)

        # ---- Central widget ----
        central = QWidget()
        v = QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self.top_bar = TopBar(self._i18n)
        v.addWidget(self.top_bar)

        self._stack = QStackedWidget()
        v.addWidget(self._stack, 1)

        self.view_single = SingleView(self._library, self._i18n)
        self.view_grid = GridView(self._library, self._i18n)
        self.view_free = FreeView(self._library, self._i18n)

        self._stack.addWidget(self.view_single)
        self._stack.addWidget(self.view_grid)
        self._stack.addWidget(self.view_free)

        self.setCentralWidget(central)

        # ---- Status bar ----
        self._status = StatusBar(self, self._i18n)
        self.setStatusBar(self._status)
        self._status.set_theme(theme.current, theme.mode)
        self.top_bar.set_theme_mode(theme.mode)
        self.top_bar.set_language(self._i18n.current)

        # ---- Wire signals ----
        self.top_bar.modeChanged.connect(self._switch_mode)
        self.top_bar.refreshRequested.connect(self._refresh_library)
        self.top_bar.themeModeRequested.connect(self._theme.set_mode)
        self.top_bar.languageRequested.connect(self._i18n.set_language)
        self._i18n.languageChanged.connect(self._on_language_changed)

        for view in (self.view_single, self.view_grid, self.view_free):
            view.statusChanged.connect(self._on_status)

        theme.themeChanged.connect(self._on_theme_changed)
        theme.modeChanged.connect(self._on_theme_mode_changed)

        # ---- Shortcuts ----
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self._switch_mode(ViewMode.SINGLE))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self._switch_mode(ViewMode.GRID))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self._switch_mode(ViewMode.FREE))
        QShortcut(QKeySequence("Ctrl+R"), self, self._refresh_library)
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_theme)

        # Library check
        if not self._library.entries:
            self.statusBar().showMessage(
                self._i18n.tr("status.bootstrap_empty", root=str(pics_root))
            )

    def _switch_mode(self, mode: ViewMode) -> None:
        index = {ViewMode.SINGLE: 0, ViewMode.GRID: 1, ViewMode.FREE: 2}[mode]
        self._stack.setCurrentIndex(index)
        self.top_bar.mode_switcher.set_mode(mode)

    def _refresh_library(self) -> None:
        self._library = scan_library(self._pics_root)
        self.view_single.set_library(self._library)
        self.view_grid.set_library(self._library)
        self.view_free.set_library(self._library)
        n = len(self._library.entries)
        self._status.set_count(n)
        if n == 0:
            QMessageBox.warning(
                self,
                self._i18n.tr("dialog.scan_title"),
                self._i18n.tr("dialog.scan_empty", root=str(self._pics_root)),
            )

    def _toggle_theme(self) -> None:
        self._theme.toggle()

    def _on_theme_changed(self, resolved: str) -> None:
        self._status.set_theme(resolved, self._theme.mode)

    def _on_theme_mode_changed(self, mode: str) -> None:
        self.top_bar.set_theme_mode(mode)
        self._status.set_theme(self._theme.current, mode)

    def _on_language_changed(self, lang: str) -> None:
        self.top_bar.set_language(lang)
        # Re-render composite "system (resolved)" theme cell under new language.
        self._status.set_theme(self._theme.current, self._theme.mode)

    def _on_status(self, path: str, count: int, zoom: float) -> None:
        self._status.set_path(path)
        if count > 0:
            self._status.set_count(count)
        if zoom > 0:
            self._status.set_zoom(zoom)
        else:
            self._status.set_zoom(None)
