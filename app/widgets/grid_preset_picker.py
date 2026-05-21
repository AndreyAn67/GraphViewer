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

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SubToolbar")
        self.setFixedHeight(40)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 6, 16, 6)
        h.setSpacing(8)

        h.addWidget(self._label("网格预设"))
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
        self.chk_sync = QCheckBox("同步缩放")
        self.chk_sync.setChecked(True)
        self.chk_sync.toggled.connect(self.syncZoomChanged)
        h.addWidget(self.chk_sync)

        self._buttons[1][0].setChecked(True)  # default 2×2

    @staticmethod
    def _label(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("color: #8b91a8; font-size: 11px; letter-spacing: 0.04em;")
        return l

    def _make_handler(self, rows: int, cols: int):
        def handler(checked: bool) -> None:
            if checked:
                self.presetChanged.emit(rows, cols)
        return handler
