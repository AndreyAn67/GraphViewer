from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget

from app.core.filter_engine import resolve_single
from app.core.labels import format_breadcrumb
from app.core.models import Library
from app.i18n import Translator
from app.widgets.filter_panel import FilterPanel
from app.widgets.image_card import ImageCard


class SingleView(QWidget):
    """Single-image mode: parameter panel on the left, one big ImageCard right."""

    statusChanged = Signal(str, int, float)  # path, count, zoom

    def __init__(self, library: Library, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self._library = library
        self._i18n = translator

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.filter_panel = FilterPanel(self._i18n)
        self.filter_panel.set_library(library)
        layout.addWidget(self.filter_panel)

        self.card = ImageCard(closable=False, translator=self._i18n)
        layout.addWidget(self.card, 1)

        self.filter_panel.applyRequested.connect(self._on_apply)
        self.filter_panel.resetRequested.connect(self._on_reset)
        self.card.zoomChanged.connect(
            lambda z: self.statusChanged.emit(self._last_path, 1, z)
        )
        self._last_path = "—"
        self._last_state: str = "empty"
        self._last_entry = None

        self._i18n.languageChanged.connect(self.retranslate)

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
            self._last_state = "empty"
            self._last_entry = None
            self.card.show_empty("view.no_match_hint")
            self._last_path = "—"
            self.statusChanged.emit(self._i18n.tr("view.no_match_short"), 0, 0)
            return
        self._last_state = "image"
        self._last_entry = entry
        self.card.show_image(entry.path, entry)
        breadcrumb = format_breadcrumb(entry, self._i18n)
        self._last_path = breadcrumb
        # Zoom emit comes from the chained card.zoomChanged signal after
        # fit_to_view runs; pass 0 here to mean "preserve" until that fires.
        self.statusChanged.emit(breadcrumb, 1, 0)

    def _on_reset(self) -> None:
        # Re-apply library to reset defaults
        self.filter_panel.set_library(self._library)
        self._on_apply()

    def retranslate(self) -> None:
        if self._last_state == "empty":
            self.statusChanged.emit(self._i18n.tr("view.no_match_short"), 0, 0)
        elif self._last_entry is not None:
            breadcrumb = format_breadcrumb(self._last_entry, self._i18n)
            self._last_path = breadcrumb
            self.statusChanged.emit(breadcrumb, 1, 0)
