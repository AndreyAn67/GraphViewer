from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
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
        self._last_percent: float = 100.0

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

        self._btn_zoom_out = QPushButton("−")
        self._btn_zoom_out.setObjectName("CardZoomStep")
        self._btn_zoom_out.setFixedSize(24, 24)
        h.addWidget(self._btn_zoom_out)

        self._cmb_zoom = QComboBox()
        self._cmb_zoom.setObjectName("CardZoomCombo")
        self._cmb_zoom.setEditable(True)
        self._cmb_zoom.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._cmb_zoom.setFixedWidth(72)
        self._cmb_zoom.addItems(
            ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "400%", "800%"]
        )
        self._cmb_zoom.setCurrentText("100%")
        h.addWidget(self._cmb_zoom)

        self._btn_zoom_in = QPushButton("+")
        self._btn_zoom_in.setObjectName("CardZoomStep")
        self._btn_zoom_in.setFixedSize(24, 24)
        h.addWidget(self._btn_zoom_in)

        self._btn_fit = QPushButton("")
        self._btn_fit.setObjectName("CardActionButton")
        self._btn_fit.setMinimumWidth(48)
        self._btn_fit.setFixedHeight(24)
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
        self._btn_zoom_in.clicked.connect(lambda: self.viewer.zoom_step(1.15))
        self._btn_zoom_out.clicked.connect(lambda: self.viewer.zoom_step(1.0 / 1.15))
        self._cmb_zoom.activated.connect(self._on_zoom_combo_activated)
        self._cmb_zoom.lineEdit().editingFinished.connect(self._on_zoom_edit_finished)

        self._set_zoom_controls_enabled(False)

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    # ---- public ----

    def show_image(self, path: Path, entry: ImageEntry) -> None:
        if self.viewer.load(path):
            self._state = "image"
            self._last_entry = entry
            self._stack.setCurrentWidget(self.viewer)
            self._breadcrumb.setText(format_breadcrumb(entry, self._i18n))
            self._set_zoom_controls_enabled(True)
        else:
            self._state = "failed"
            self._last_failed_name = path.name
            self.viewer.clear()
            self._stack.setCurrentWidget(self._empty)
            self._breadcrumb.setText(
                self._i18n.tr("card.load_failed", name=self._last_failed_name)
            )
            self._set_zoom_controls_enabled(False)

    def show_empty(self, message_key: str | None = None) -> None:
        self._state = "empty"
        self._last_entry = None
        self._last_empty_key = message_key or "card.unselected_dash"
        self.viewer.clear()
        self._stack.setCurrentWidget(self._empty)
        self._breadcrumb.setText(self._i18n.tr(self._last_empty_key))
        self._set_zoom_controls_enabled(False)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        # re-polish to apply property-based stylesheet
        self.style().unpolish(self)
        self.style().polish(self)

    def retranslate(self) -> None:
        self._btn_fit.setText(self._i18n.tr("card.fit"))
        self._btn_fit.setToolTip(self._i18n.tr("card.fit_tooltip"))
        self._btn_zoom_in.setToolTip(self._i18n.tr("card.zoom_in_tooltip"))
        self._btn_zoom_out.setToolTip(self._i18n.tr("card.zoom_out_tooltip"))
        self._cmb_zoom.setToolTip(self._i18n.tr("card.zoom_tooltip"))
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
        self._last_percent = percent
        text = f"{percent:.0f}%"
        # Block both the combo and its line edit so updating the displayed
        # value from the viewer doesn't fire activated / editingFinished
        # back into set_scale (which would cause a feedback loop on every
        # wheel tick).
        line = self._cmb_zoom.lineEdit()
        self._cmb_zoom.blockSignals(True)
        line.blockSignals(True)
        try:
            self._cmb_zoom.setCurrentText(text)
        finally:
            line.blockSignals(False)
            self._cmb_zoom.blockSignals(False)
        self.zoomChanged.emit(percent)

    def _on_zoom_combo_activated(self, index: int) -> None:
        value = self._parse_zoom_text(self._cmb_zoom.itemText(index))
        if value is not None:
            self.viewer.set_scale(value / 100.0)

    def _on_zoom_edit_finished(self) -> None:
        value = self._parse_zoom_text(self._cmb_zoom.currentText())
        if value is None:
            # Restore the last known good text rather than leaving garbage.
            self._cmb_zoom.lineEdit().setText(f"{self._last_percent:.0f}%")
            return
        self.viewer.set_scale(value / 100.0)

    @staticmethod
    def _parse_zoom_text(text: str) -> float | None:
        s = text.strip().rstrip("%").strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    def _set_zoom_controls_enabled(self, enabled: bool) -> None:
        self._btn_zoom_in.setEnabled(enabled)
        self._btn_zoom_out.setEnabled(enabled)
        self._cmb_zoom.setEnabled(enabled)
        self._btn_fit.setEnabled(enabled)
        if not enabled:
            line = self._cmb_zoom.lineEdit()
            self._cmb_zoom.blockSignals(True)
            line.blockSignals(True)
            try:
                self._cmb_zoom.setCurrentText("—")
            finally:
                line.blockSignals(False)
                self._cmb_zoom.blockSignals(False)
