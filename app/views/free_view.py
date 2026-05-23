from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.core.filter_engine import resolve_single
from app.core.models import Library
from app.i18n import Translator
from app.widgets.filter_panel import FilterPanel
from app.widgets.image_card import ImageCard


class FreeView(QWidget):
    """Free drag-resize comparison mode.

    Phase-1 implementation: top toolbar with [+ 新增面板], a horizontal QSplitter
    of ImageCards. Splitter handles are draggable to resize. Clicking a card
    selects it; the left FilterPanel applies to the selected card.
    """

    statusChanged = Signal(str, int, float)

    def __init__(self, library: Library, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self._library = library
        self._i18n = translator
        self._cards: list[ImageCard] = []
        self._selected_index: int = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        toolbar = QWidget()
        toolbar.setObjectName("SubToolbar")
        toolbar.setFixedHeight(40)
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(16, 6, 16, 6)
        tl.setSpacing(8)
        self.btn_add = QPushButton("")
        self.btn_add.setObjectName("GhostButton")
        self.btn_add.setFixedHeight(28)
        tl.addWidget(self.btn_add)
        tl.addStretch(1)
        self._hint = QLabel("")
        self._hint.setObjectName("ToolbarHint")
        tl.addWidget(self._hint)
        outer.addWidget(toolbar)

        self.filter_panel = FilterPanel(self._i18n)
        self.filter_panel.set_library(library)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setObjectName("FreeSplitter")
        self._splitter.setHandleWidth(4)
        self._splitter.setChildrenCollapsible(False)

        self._outer_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._outer_splitter.setObjectName("FilterSplitter")
        self._outer_splitter.setHandleWidth(4)
        self._outer_splitter.setChildrenCollapsible(False)
        self._outer_splitter.addWidget(self.filter_panel)
        self._outer_splitter.addWidget(self._splitter)
        self._outer_splitter.setStretchFactor(0, 0)
        self._outer_splitter.setStretchFactor(1, 1)
        self._outer_splitter.setSizes([264, 1000])

        outer.addWidget(self._outer_splitter, 1)

        self.btn_add.clicked.connect(self._add_card)
        self.filter_panel.applyRequested.connect(self._on_apply_current)
        self.filter_panel.resetRequested.connect(
            lambda: self.filter_panel.set_library(self._library)
        )

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

        self._add_card()
        self._add_card()

    def set_library(self, library: Library) -> None:
        self._library = library
        self.filter_panel.set_library(library)
        for c in self._cards:
            c.show_empty()

    def _add_card(self) -> None:
        card = ImageCard(closable=True, translator=self._i18n)
        card.closed.connect(self._remove_card)
        card.clicked.connect(lambda src=card: self._select_card(src))
        card.zoomChanged.connect(
            lambda z: self.statusChanged.emit(
                self._i18n.tr("view.free.title"), len(self._cards), z
            )
        )
        self._splitter.addWidget(card)
        self._cards.append(card)
        # Equalize sizes
        n = len(self._cards)
        total = max(self._splitter.width(), 800)
        self._splitter.setSizes([total // n] * n)
        self._selected_index = len(self._cards) - 1
        self._refresh_selection()
        self._emit_status()

    def _remove_card(self, card: ImageCard) -> None:
        if len(self._cards) <= 1:
            return
        self._cards.remove(card)
        card.setParent(None)
        card.deleteLater()
        self._selected_index = min(self._selected_index, len(self._cards) - 1)
        self._refresh_selection()
        self._emit_status()

    def _select_card(self, card: ImageCard) -> None:
        if card in self._cards:
            self._selected_index = self._cards.index(card)
            self._refresh_selection()

    def _refresh_selection(self) -> None:
        for i, c in enumerate(self._cards):
            c.set_selected(i == self._selected_index)

    def _on_apply_current(self) -> None:
        if not self._cards:
            return
        sel = self.filter_panel.current()
        entry = resolve_single(self._library, sel)
        card = self._cards[self._selected_index]
        if entry is None:
            card.show_empty("view.no_match_short")
        else:
            card.show_image(entry.path, entry)

    def _emit_status(self) -> None:
        self.statusChanged.emit(
            self._i18n.tr("view.free.title"), len(self._cards), 0
        )

    def retranslate(self) -> None:
        self.btn_add.setText(self._i18n.tr("view.free.add_panel"))
        self._hint.setText(self._i18n.tr("view.free.drag_hint"))
        self._emit_status()
