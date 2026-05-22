from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from app.i18n import Translator


class ViewMode(str, Enum):
    SINGLE = "single"
    GRID = "grid"
    FREE = "free"


class ModeSwitcher(QWidget):
    modeChanged = Signal(ViewMode)

    def __init__(self, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ModeSwitch")
        self._i18n = translator
        h = QHBoxLayout(self)
        h.setContentsMargins(2, 2, 2, 2)
        h.setSpacing(2)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[ViewMode, QPushButton] = {}
        for mode in (ViewMode.SINGLE, ViewMode.GRID, ViewMode.FREE):
            btn = QPushButton("")
            btn.setObjectName("ModeSwitchTab")
            btn.setCheckable(True)
            self._group.addButton(btn)
            h.addWidget(btn)
            self._buttons[mode] = btn
            btn.toggled.connect(self._make_handler(mode))
        self._buttons[ViewMode.SINGLE].setChecked(True)

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    def _make_handler(self, mode: ViewMode):
        def handler(checked: bool) -> None:
            if checked:
                self.modeChanged.emit(mode)
        return handler

    def set_mode(self, mode: ViewMode) -> None:
        self._buttons[mode].setChecked(True)

    def retranslate(self) -> None:
        for mode, btn in self._buttons.items():
            btn.setText(self._i18n.tr(f"mode.{mode.value}"))
