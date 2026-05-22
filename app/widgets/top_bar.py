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

from app.i18n import LANG_GLYPH, SUPPORTED_LANGS, Translator
from app.widgets.mode_switcher import ModeSwitcher, ViewMode


THEME_ICONS = {
    "light": "☀",
    "dark": "☾",
    "system": "◐",
}


class TopBar(QWidget):
    refreshRequested = Signal()
    themeModeRequested = Signal(str)  # "light" / "dark" / "system"
    languageRequested = Signal(str)  # "zh" / "ru"
    modeChanged = Signal(ViewMode)

    def __init__(self, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self._i18n = translator
        self.setObjectName("TopBar")
        self.setFixedHeight(48)

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 8, 12, 8)
        h.setSpacing(8)

        title = QLabel("GraphViewer")
        title.setObjectName("AppTitle")
        h.addWidget(title)
        version = QLabel("v0.3")
        version.setObjectName("AppVersion")
        h.addWidget(version)
        author = QLabel("by AndreyAn")
        author.setObjectName("AppAuthor")
        h.addWidget(author)
        h.addStretch(1)

        self.mode_switcher = ModeSwitcher(self._i18n)
        h.addWidget(self.mode_switcher, 0, Qt.AlignmentFlag.AlignCenter)
        h.addStretch(1)

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setObjectName("IconButton")
        h.addWidget(self.btn_refresh)

        self.btn_theme = QToolButton()
        self.btn_theme.setObjectName("IconButton")
        self.btn_theme.setText(THEME_ICONS["system"])
        self.btn_theme.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)

        self._theme_menu = QMenu(self.btn_theme)
        self._theme_actions: dict[str, QAction] = {}
        theme_group = QActionGroup(self._theme_menu)
        theme_group.setExclusive(True)
        for key in ("light", "dark", "system"):
            act = QAction("", self._theme_menu)
            act.setCheckable(True)
            act.setData(key)
            act.triggered.connect(
                lambda _checked=False, k=key: self.themeModeRequested.emit(k)
            )
            theme_group.addAction(act)
            self._theme_menu.addAction(act)
            self._theme_actions[key] = act
        self.btn_theme.setMenu(self._theme_menu)
        h.addWidget(self.btn_theme)

        # Language switcher — mirrors theme button structure.
        self.btn_lang = QToolButton()
        self.btn_lang.setObjectName("IconButton")
        self.btn_lang.setText(LANG_GLYPH[self._i18n.current])
        self.btn_lang.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)

        self._lang_menu = QMenu(self.btn_lang)
        self._lang_actions: dict[str, QAction] = {}
        lang_group = QActionGroup(self._lang_menu)
        lang_group.setExclusive(True)
        for key in SUPPORTED_LANGS:
            act = QAction("", self._lang_menu)
            act.setCheckable(True)
            act.setData(key)
            act.triggered.connect(
                lambda _checked=False, k=key: self.languageRequested.emit(k)
            )
            lang_group.addAction(act)
            self._lang_menu.addAction(act)
            self._lang_actions[key] = act
        self._lang_actions[self._i18n.current].setChecked(True)
        self.btn_lang.setMenu(self._lang_menu)
        h.addWidget(self.btn_lang)

        self.btn_refresh.clicked.connect(self.refreshRequested)
        self.mode_switcher.modeChanged.connect(self.modeChanged)

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    def set_theme_mode(self, mode: str) -> None:
        """Reflect the active mode in the menu check state and button icon."""
        for key, act in self._theme_actions.items():
            act.setChecked(key == mode)
        if mode in THEME_ICONS:
            self.btn_theme.setText(THEME_ICONS[mode])

    def set_language(self, lang: str) -> None:
        for key, act in self._lang_actions.items():
            act.setChecked(key == lang)
        if lang in LANG_GLYPH:
            self.btn_lang.setText(LANG_GLYPH[lang])

    def retranslate(self) -> None:
        self.btn_refresh.setToolTip(self._i18n.tr("top_bar.refresh_tooltip"))
        self.btn_theme.setToolTip(self._i18n.tr("top_bar.theme_tooltip"))
        self.btn_lang.setToolTip(self._i18n.tr("top_bar.language_tooltip"))
        for key, act in self._theme_actions.items():
            act.setText(f"{THEME_ICONS[key]}  {self._i18n.tr('top_bar.theme.' + key)}")
        for key, act in self._lang_actions.items():
            act.setText(self._i18n.tr(f"top_bar.lang.{key}"))
