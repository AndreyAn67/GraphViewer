from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPixmap, QWheelEvent, QPainter
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
)


class ImageViewer(QGraphicsView):
    """QGraphicsView wrapper that displays a single image with pan/zoom.

    Emits zoomChanged(float percent) so cards can render a "125%" indicator
    and an external controller can synchronize zoom across multiple viewers.
    """

    zoomChanged = Signal(float)  # percent (100.0 = 1:1)

    MIN_SCALE = 0.1
    MAX_SCALE = 20.0

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ImageView")
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pix_item: QGraphicsPixmapItem | None = None
        self._scale = 1.0
        # When True, resize re-fits the image. Cleared as soon as the user
        # manually zooms (so their chosen zoom level is preserved on resize).
        self._auto_fit = True

        self.setRenderHints(
            QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setBackgroundBrush(Qt.GlobalColor.black)

    # ---- public API ----

    def load(self, path: Path | None) -> bool:
        self._scene.clear()
        self._pix_item = None
        if path is None or not path.is_file():
            return False
        pix = QPixmap(str(path))
        if pix.isNull():
            return False
        self._pix_item = self._scene.addPixmap(pix)
        self._scene.setSceneRect(QRectF(pix.rect()))
        self.fit_to_view()
        return True

    def clear(self) -> None:
        self._scene.clear()
        self._pix_item = None

    def fit_to_view(self) -> None:
        if self._pix_item is None:
            return
        self.resetTransform()
        self.fitInView(self._pix_item, Qt.AspectRatioMode.KeepAspectRatio)
        # fitInView with KeepAspectRatio gives m11 == m22 (up to FP rounding),
        # so reading m11 is the canonical scale.
        self._scale = self.transform().m11()
        self._auto_fit = True
        self.zoomChanged.emit(self._scale * 100.0)

    def actual_size(self) -> None:
        if self._pix_item is None:
            return
        self.resetTransform()
        self._scale = 1.0
        self._auto_fit = False
        self.zoomChanged.emit(100.0)

    def set_scale(self, scale: float) -> None:
        if self._pix_item is None:
            return
        scale = max(self.MIN_SCALE, min(self.MAX_SCALE, scale))
        self.resetTransform()
        self.scale(scale, scale)
        self._scale = scale
        self._auto_fit = False
        self.zoomChanged.emit(scale * 100.0)

    def zoom_step(self, factor: float) -> None:
        if self._pix_item is None:
            return
        new_scale = max(self.MIN_SCALE, min(self.MAX_SCALE, self._scale * factor))
        self.scale(new_scale / self._scale, new_scale / self._scale)
        self._scale = new_scale
        self._auto_fit = False
        self.zoomChanged.emit(self._scale * 100.0)

    # ---- events ----

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802 (Qt naming)
        if self._pix_item is None:
            super().wheelEvent(event)
            return
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.zoom_step(factor)
        event.accept()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._pix_item is not None and self._auto_fit:
            self.fit_to_view()
