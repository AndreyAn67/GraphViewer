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

from app.core.labels import format_breadcrumb
from app.core.models import ImageEntry
from app.i18n import Translator
from app.widgets.image_viewer import ImageViewer


class ImageCard(QFrame):
    """A single image tile used in grid and free comparison modes."""

    closed = Signal(object)  # emits self
    zoomChanged = Signal(float)
    clicked = Signal()

    def mousePressEvent(self, event):  # noqa: N802 (Qt naming)
        super().mousePressEvent(event)
        self.clicked.emit()

    def __init__(
        self,
        parent=None,
        *,
        closable: bool = False,
        translator: Translator | None = None,
    ) -> None:
        super().__init__(parent)
        assert translator is not None, "ImageCard requires a Translator"
        self._i18n: Translator = translator
        self.setObjectName("ImageCard")
        self.setProperty("selected", False)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # State for retranslation: at most one of these is "active" at a time.
        self._state: str = "empty"  # "empty" | "image" | "failed"
        self._last_entry: ImageEntry | None = None
        self._last_empty_key: str = "card.unselected_dash"
        self._last_failed_name: str = ""

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
        self._breadcrumb = QLabel("")
        self._breadcrumb.setObjectName("CardBreadcrumb")
        self._breadcrumb.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        h.addWidget(self._breadcrumb, 1)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setObjectName("CardZoom")
        h.addWidget(self._zoom_label)

        self._btn_fit = QPushButton("")
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
        self._empty_title = QLabel("")
        self._empty_title.setObjectName("EmptyStateTitle")
        self._empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_hint = QLabel("")
        self._empty_hint.setObjectName("EmptyStateHint")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ev.addWidget(self._empty_title)
        ev.addWidget(self._empty_hint)
        ev.addStretch(1)
        self._stack.addWidget(self._empty)

        outer.addWidget(self._body, 1)

        self._stack.setCurrentWidget(self._empty)

        self.viewer.zoomChanged.connect(self._on_zoom_changed)
        self._btn_fit.clicked.connect(self.viewer.fit_to_view)

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    # ---- public ----

    def show_image(self, path: Path, entry: ImageEntry) -> None:
        if self.viewer.load(path):
            self._state = "image"
            self._last_entry = entry
            self._stack.setCurrentWidget(self.viewer)
            self._breadcrumb.setText(format_breadcrumb(entry, self._i18n))
        else:
            self._state = "failed"
            self._last_failed_name = path.name
            self.viewer.clear()
            self._stack.setCurrentWidget(self._empty)
            self._breadcrumb.setText(
                self._i18n.tr("card.load_failed", name=self._last_failed_name)
            )
            self._zoom_label.setText("—")

    def show_empty(self, message_key: str | None = None) -> None:
        self._state = "empty"
        self._last_entry = None
        self._last_empty_key = message_key or "card.unselected_dash"
        self.viewer.clear()
        self._stack.setCurrentWidget(self._empty)
        self._breadcrumb.setText(self._i18n.tr(self._last_empty_key))
        self._zoom_label.setText("—")

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        # re-polish to apply property-based stylesheet
        self.style().unpolish(self)
        self.style().polish(self)

    def retranslate(self) -> None:
        self._btn_fit.setText(self._i18n.tr("card.fit"))
        self._empty_title.setText(self._i18n.tr("card.unselected_title"))
        self._empty_hint.setText(self._i18n.tr("card.unselected_hint"))
        if self._state == "image" and self._last_entry is not None:
            self._breadcrumb.setText(format_breadcrumb(self._last_entry, self._i18n))
        elif self._state == "failed":
            self._breadcrumb.setText(
                self._i18n.tr("card.load_failed", name=self._last_failed_name)
            )
        else:
            self._breadcrumb.setText(self._i18n.tr(self._last_empty_key))

    def _on_zoom_changed(self, percent: float) -> None:
        self._zoom_label.setText(f"{percent:.0f}%")
        self.zoomChanged.emit(percent)
