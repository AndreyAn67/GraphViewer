from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from app.i18n import Translator


PRESETS: list[tuple[str, int, int]] = [
    ("1×2", 1, 2),
    ("2×2", 2, 2),
    ("2×3", 2, 3),
    ("3×3", 3, 3),
    ("3×4", 3, 4),
]


class GridPresetPicker(QWidget):
    presetChanged = Signal(int, int)  # rows, cols
    syncZoomChanged = Signal(bool)

    def __init__(self, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SubToolbar")
        self.setFixedHeight(40)
        self._i18n = translator

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 6, 16, 6)
        h.setSpacing(8)

        self._title_label = self._label("")
        h.addWidget(self._title_label)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: list[tuple[QPushButton, int, int]] = []
        for label, rows, cols in PRESETS:
            btn = QPushButton(label)
            btn.setObjectName("PresetButton")
            btn.setCheckable(True)
            self._group.addButton(btn)
            h.addWidget(btn)
            self._buttons.append((btn, rows, cols))
            btn.toggled.connect(self._make_handler(rows, cols))

        h.addStretch(1)
        self.chk_sync = QCheckBox("")
        self.chk_sync.setChecked(True)
        self.chk_sync.toggled.connect(self.syncZoomChanged)
        h.addWidget(self.chk_sync)

        self._buttons[1][0].setChecked(True)  # default 2×2

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    @staticmethod
    def _label(text: str) -> QLabel:
        l = QLabel(text)
        l.setObjectName("ToolbarLabel")
        return l

    def _make_handler(self, rows: int, cols: int):
        def handler(checked: bool) -> None:
            if checked:
                self.presetChanged.emit(rows, cols)
        return handler

    def retranslate(self) -> None:
        self._title_label.setText(self._i18n.tr("grid.preset_title"))
        self.chk_sync.setText(self._i18n.tr("grid.sync_zoom"))
