from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBar(QStatusBar):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        self._path = QLabel("—")
        self._count = QLabel("共 0 张")
        self._zoom = QLabel("缩放 —")
        self._theme = QLabel("深色")

        self.addWidget(self._path, 1)
        self.addPermanentWidget(self._count)
        self.addPermanentWidget(self._make_sep())
        self.addPermanentWidget(self._zoom)
        self.addPermanentWidget(self._make_sep())
        self.addPermanentWidget(self._theme)

    @staticmethod
    def _make_sep() -> QLabel:
        s = QLabel("|")
        s.setObjectName("StatusSep")
        return s

    def set_path(self, text: str) -> None:
        self._path.setText(text)

    def set_count(self, n: int) -> None:
        self._count.setText(f"共 {n} 张")

    def set_zoom(self, percent: float | None) -> None:
        if percent is None:
            self._zoom.setText("缩放 —")
        else:
            self._zoom.setText(f"缩放 {percent:.0f}%")

    def set_theme(self, resolved: str, mode: str | None = None) -> None:
        resolved_label = "深色" if resolved == "dark" else "浅色"
        if mode == "system":
            self._theme.setText(f"跟随系统 ({resolved_label})")
        else:
            self._theme.setText(resolved_label)
