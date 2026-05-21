from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QVBoxLayout,
    QWidget,
)

from app.core.filter_engine import resolve_single
from app.core.models import (
    DataType,
    Library,
    Method,
    ParameterSelection,
    Polarization,
)
from app.widgets.filter_panel import FilterPanel
from app.widgets.grid_preset_picker import GridPresetPicker
from app.widgets.image_card import ImageCard


class GridView(QWidget):
    """Preset-grid comparison mode. Each cell is an ImageCard.

    For Phase-1 simplicity, the left FilterPanel sets the parameters for the
    currently selected cell. Clicking a different cell switches the panel's
    target. Future iterations will allow a "common" group of dims at the top
    and per-cell overrides for the rest.
    """

    statusChanged = Signal(str, int, float)

    def __init__(self, library: Library, parent=None) -> None:
        super().__init__(parent)
        self._library = library
        self._cells: list[ImageCard] = []
        self._selected_index: int = 0
        self._sync_zoom = True
        self._syncing_zoom = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.preset = GridPresetPicker()
        outer.addWidget(self.preset)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(0, 0, 0, 0)
        body_l.setSpacing(0)

        content = QWidget()
        h = QVBoxLayout(content)
        h.setContentsMargins(0, 0, 0, 0)

        # Inner layout: filter panel + grid area
        from PySide6.QtWidgets import QHBoxLayout

        inner = QHBoxLayout()
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)

        self.filter_panel = FilterPanel()
        self.filter_panel.set_library(library)
        inner.addWidget(self.filter_panel)

        self._grid_host = QWidget()
        self._grid_host.setStyleSheet("background-color: #0f1117;")
        self._grid = QGridLayout(self._grid_host)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setSpacing(8)
        inner.addWidget(self._grid_host, 1)

        h.addLayout(inner)
        outer.addWidget(content, 1)

        self.preset.presetChanged.connect(self.set_grid)
        self.preset.syncZoomChanged.connect(self._on_sync_changed)
        self.filter_panel.applyRequested.connect(self._on_apply_current)
        self.filter_panel.resetRequested.connect(self._on_reset)

        self.set_grid(2, 2)

    # ---- public ----

    def set_library(self, library: Library) -> None:
        self._library = library
        self.filter_panel.set_library(library)
        for card in self._cells:
            card.show_empty()

    def set_grid(self, rows: int, cols: int) -> None:
        # Clear existing
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._cells.clear()

        for r in range(rows):
            for c in range(cols):
                card = ImageCard(closable=False)
                self._grid.addWidget(card, r, c)
                self._cells.append(card)
                card.viewer.zoomChanged.connect(
                    lambda z, src=card: self._on_card_zoom(src, z)
                )
                card.clicked.connect(
                    lambda src=card: self._select_card(src)
                )

        self._selected_index = 0
        self._refresh_selection()
        self.statusChanged.emit(f"{rows}×{cols} 网格", len(self._cells), 0)

    # ---- internals ----

    def _select_card(self, card: ImageCard) -> None:
        if card in self._cells:
            self._selected_index = self._cells.index(card)
            self._refresh_selection()

    def _refresh_selection(self) -> None:
        for i, card in enumerate(self._cells):
            card.set_selected(i == self._selected_index)

    def _on_apply_current(self) -> None:
        if not self._cells:
            return
        sel = self.filter_panel.current()
        entry = resolve_single(self._library, sel)
        card = self._cells[self._selected_index]
        if entry is None:
            card.show_empty("无匹配图像")
        else:
            card.show_image(entry.path, entry.breadcrumb())

    def _on_reset(self) -> None:
        self.filter_panel.set_library(self._library)

    def _on_sync_changed(self, sync: bool) -> None:
        self._sync_zoom = sync

    def _on_card_zoom(self, source: ImageCard, percent: float) -> None:
        if not self._sync_zoom or self._syncing_zoom:
            return
        self._syncing_zoom = True
        try:
            for c in self._cells:
                if c is source:
                    continue
                c.viewer.set_scale(percent / 100.0)
        finally:
            self._syncing_zoom = False
