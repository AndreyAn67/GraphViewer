from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar

from app.i18n import Translator


class StatusBar(QStatusBar):
    def __init__(self, parent=None, translator: Translator | None = None) -> None:
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        assert translator is not None, "StatusBar requires a Translator"
        self._i18n: Translator = translator

        self._n: int = 0
        self._percent: float | None = None
        self._resolved: str = "dark"
        self._mode: str | None = None

        self._path = QLabel("—")
        self._count = QLabel("—")
        self._zoom = QLabel("—")
        self._theme = QLabel("—")

        self.addWidget(self._path, 1)
        self.addPermanentWidget(self._count)
        self.addPermanentWidget(self._make_sep())
        self.addPermanentWidget(self._zoom)
        self.addPermanentWidget(self._make_sep())
        self.addPermanentWidget(self._theme)

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    @staticmethod
    def _make_sep() -> QLabel:
        s = QLabel("|")
        s.setObjectName("StatusSep")
        return s

    def set_path(self, text: str) -> None:
        self._path.setText(text)

    def set_count(self, n: int) -> None:
        self._n = n
        self._render_count()

    def set_zoom(self, percent: float | None) -> None:
        self._percent = percent
        self._render_zoom()

    def set_theme(self, resolved: str, mode: str | None = None) -> None:
        self._resolved = resolved
        self._mode = mode
        self._render_theme()

    def _render_count(self) -> None:
        self._count.setText(self._i18n.tr("status.count", n=self._n))

    def _render_zoom(self) -> None:
        if self._percent is None:
            self._zoom.setText(self._i18n.tr("status.zoom_empty"))
        else:
            self._zoom.setText(self._i18n.tr("status.zoom", percent=self._percent))

    def _render_theme(self) -> None:
        resolved_label = self._i18n.tr(f"status.theme.{self._resolved}")
        if self._mode == "system":
            self._theme.setText(
                self._i18n.tr("status.theme.system", resolved=resolved_label)
            )
        else:
            self._theme.setText(resolved_label)

    def retranslate(self) -> None:
        self._render_count()
        self._render_zoom()
        self._render_theme()
