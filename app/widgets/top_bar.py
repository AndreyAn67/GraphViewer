from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from app.widgets.mode_switcher import ModeSwitcher, ViewMode


class TopBar(QWidget):
    refreshRequested = Signal()
    themeToggleRequested = Signal()
    modeChanged = Signal(ViewMode)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setFixedHeight(48)

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 8, 12, 8)
        h.setSpacing(8)

        title = QLabel("GraphViewer")
        title.setObjectName("AppTitle")
        h.addWidget(title)
        version = QLabel("v0.1")
        version.setObjectName("AppVersion")
        h.addWidget(version)
        h.addStretch(1)

        self.mode_switcher = ModeSwitcher()
        h.addWidget(self.mode_switcher, 0, Qt.AlignmentFlag.AlignCenter)
        h.addStretch(1)

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setObjectName("IconButton")
        self.btn_refresh.setToolTip("重新扫描图像库 (Ctrl+R)")
        h.addWidget(self.btn_refresh)

        self.btn_theme = QPushButton("◐")
        self.btn_theme.setObjectName("IconButton")
        self.btn_theme.setToolTip("切换主题 (Ctrl+T)")
        h.addWidget(self.btn_theme)

        self.btn_refresh.clicked.connect(self.refreshRequested)
        self.btn_theme.clicked.connect(self.themeToggleRequested)
        self.mode_switcher.modeChanged.connect(self.modeChanged)
