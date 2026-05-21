from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget

from app.core.filter_engine import resolve_single
from app.core.models import Library
from app.widgets.filter_panel import FilterPanel
from app.widgets.image_card import ImageCard


class SingleView(QWidget):
    """Single-image mode: parameter panel on the left, one big ImageCard right."""

    statusChanged = Signal(str, int, float)  # path, count, zoom

    def __init__(self, library: Library, parent=None) -> None:
        super().__init__(parent)
        self._library = library

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.filter_panel = FilterPanel()
        self.filter_panel.set_library(library)
        layout.addWidget(self.filter_panel)

        self.card = ImageCard(closable=False)
        layout.addWidget(self.card, 1)

        self.filter_panel.applyRequested.connect(self._on_apply)
        self.filter_panel.resetRequested.connect(self._on_reset)
        self.card.zoomChanged.connect(
            lambda z: self.statusChanged.emit(self._last_path, 1, z)
        )
        self._last_path = "—"

        # Initial attempt
        self._on_apply()

    def set_library(self, library: Library) -> None:
        self._library = library
        self.filter_panel.set_library(library)
        self._on_apply()

    def _on_apply(self) -> None:
        sel = self.filter_panel.current()
        entry = resolve_single(self._library, sel)
        if entry is None:
            self.card.show_empty("无匹配图像 — 请调整参数")
            self._last_path = "—"
            self.statusChanged.emit("无匹配图像", 0, 0)
            return
        self.card.show_image(entry.path, entry.breadcrumb())
        self._last_path = entry.breadcrumb()
        # Zoom emit comes from the chained card.zoomChanged signal after
        # fit_to_view runs; pass 0 here to mean "preserve" until that fires.
        self.statusChanged.emit(entry.breadcrumb(), 1, 0)

    def _on_reset(self) -> None:
        # Re-apply library to reset defaults
        self.filter_panel.set_library(self._library)
        self._on_apply()
