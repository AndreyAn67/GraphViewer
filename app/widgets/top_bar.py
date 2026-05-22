from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QToolButton,
    QWidget,
)

from app.widgets.mode_switcher import ModeSwitcher, ViewMode


THEME_LABELS = {
    "light": "浅色",
    "dark": "深色",
    "system": "跟随系统",
}

THEME_ICONS = {
    "light": "☀",
    "dark": "☾",
    "system": "◐",
}


class TopBar(QWidget):
    refreshRequested = Signal()
    themeModeRequested = Signal(str)  # "light" / "dark" / "system"
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
        version = QLabel("v0.2")
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

        self.btn_theme = QToolButton()
        self.btn_theme.setObjectName("IconButton")
        self.btn_theme.setText(THEME_ICONS["system"])
        self.btn_theme.setToolTip("切换主题 (Ctrl+T 循环切换)")
        self.btn_theme.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)

        self._theme_menu = QMenu(self.btn_theme)
        self._theme_actions: dict[str, QAction] = {}
        group = QActionGroup(self._theme_menu)
        group.setExclusive(True)
        for key in ("light", "dark", "system"):
            label = f"{THEME_ICONS[key]}  {THEME_LABELS[key]}"
            act = QAction(label, self._theme_menu)
            act.setCheckable(True)
            act.setData(key)
            act.triggered.connect(lambda _checked=False, k=key: self.themeModeRequested.emit(k))
            group.addAction(act)
            self._theme_menu.addAction(act)
            self._theme_actions[key] = act
        self.btn_theme.setMenu(self._theme_menu)
        h.addWidget(self.btn_theme)

        self.btn_refresh.clicked.connect(self.refreshRequested)
        self.mode_switcher.modeChanged.connect(self.modeChanged)

    def set_theme_mode(self, mode: str) -> None:
        """Reflect the active mode in the menu check state and button icon."""
        for key, act in self._theme_actions.items():
            act.setChecked(key == mode)
        if mode in THEME_ICONS:
            self.btn_theme.setText(THEME_ICONS[mode])
