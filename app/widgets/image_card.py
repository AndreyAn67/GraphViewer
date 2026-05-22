from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from app.widgets.image_viewer import ImageViewer


class ImageCard(QFrame):
    """A single image tile used in grid and free comparison modes."""

    closed = Signal(object)  # emits self
    zoomChanged = Signal(float)
    clicked = Signal()

    def mousePressEvent(self, event):  # noqa: N802 (Qt naming)
        super().mousePressEvent(event)
        self.clicked.emit()

    def __init__(self, parent=None, *, closable: bool = False) -> None:
        super().__init__(parent)
        self.setObjectName("ImageCard")
        self.setProperty("selected", False)
        self.setFrameShape(QFrame.Shape.NoFrame)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        self._header = QWidget()
        self._header.setObjectName("CardHeader")
        self._header.setFixedHeight(34)
        h = QHBoxLayout(self._header)
        h.setContentsMargins(12, 0, 8, 0)
        h.setSpacing(6)
        self._breadcrumb = QLabel("— 未选择图像 —")
        self._breadcrumb.setObjectName("CardBreadcrumb")
        self._breadcrumb.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        h.addWidget(self._breadcrumb, 1)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setObjectName("CardZoom")
        h.addWidget(self._zoom_label)

        self._btn_fit = QPushButton("适应")
        self._btn_fit.setObjectName("CardActionButton")
        self._btn_fit.setFixedSize(40, 24)
        h.addWidget(self._btn_fit)

        if closable:
            self._btn_close = QPushButton("×")
            self._btn_close.setObjectName("CardCloseButton")
            self._btn_close.setFixedSize(24, 24)
            self._btn_close.clicked.connect(lambda: self.closed.emit(self))
            h.addWidget(self._btn_close)

        outer.addWidget(self._header)

        # Body — stacked: viewer on top, empty state below
        self._body = QWidget()
        self._stack = QStackedLayout(self._body)
        self._stack.setContentsMargins(0, 0, 0, 0)

        self.viewer = ImageViewer()
        self._stack.addWidget(self.viewer)

        self._empty = QWidget()
        ev = QVBoxLayout(self._empty)
        ev.setContentsMargins(20, 20, 20, 20)
        ev.addStretch(1)
        title = QLabel("未选择图像")
        title.setObjectName("EmptyStateTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("请在左侧参数面板设置参数后点击应用")
        hint.setObjectName("EmptyStateHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ev.addWidget(title)
        ev.addWidget(hint)
        ev.addStretch(1)
        self._stack.addWidget(self._empty)

        outer.addWidget(self._body, 1)

        self._stack.setCurrentWidget(self._empty)

        self.viewer.zoomChanged.connect(self._on_zoom_changed)
        self._btn_fit.clicked.connect(self.viewer.fit_to_view)

    # ---- public ----

    def show_image(self, path: Path, breadcrumb: str) -> None:
        if self.viewer.load(path):
            self._stack.setCurrentWidget(self.viewer)
            self._breadcrumb.setText(breadcrumb)
        else:
            self.show_empty(f"加载失败: {path.name}")

    def show_empty(self, message: str = "— 未选择图像 —") -> None:
        self.viewer.clear()
        self._stack.setCurrentWidget(self._empty)
        self._breadcrumb.setText(message)
        self._zoom_label.setText("—")

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        # re-polish to apply property-based stylesheet
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_zoom_changed(self, percent: float) -> None:
        self._zoom_label.setText(f"{percent:.0f}%")
        self.zoomChanged.emit(percent)
