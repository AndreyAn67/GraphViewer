from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.core.models import (
    DEFAULT_RFOV,
    DataType,
    Library,
    Method,
    ParameterSelection,
    Polarization,
)
from app.widgets.filter_chip import FilterChip


class _ChipGroup(QWidget):
    """A horizontally-flowing row of FilterChip buttons; single-select."""

    selected = Signal(object)  # emits the value of the selected chip, or None

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._chips: list[tuple[FilterChip, object]] = []

    def set_options(self, options: list[tuple[str, object]]) -> None:
        # Drain the layout completely, including any prior stretch item,
        # so rebuilds don't accumulate orphan stretches.
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w is not None:
                self._group.removeButton(w)
                w.deleteLater()
        self._chips.clear()
        for label, value in options:
            chip = FilterChip(label)
            self._group.addButton(chip)
            self._layout.addWidget(chip)
            self._chips.append((chip, value))
            chip.toggled.connect(self._on_toggled)
        self._layout.addStretch(1)

    def _on_toggled(self, checked: bool) -> None:
        # Qt fires toggled(False) on the deselecting chip BEFORE toggled(True)
        # on the newly-selected chip. We only want the new-selection event,
        # so ignore the un-check side.
        if not checked:
            return
        sender = self.sender()
        for chip, value in self._chips:
            if chip is sender:
                self.selected.emit(value)
                return

    def select_value(self, value: object) -> None:
        for chip, v in self._chips:
            if v == value:
                chip.setChecked(True)
                return

    def first(self) -> None:
        if self._chips:
            self._chips[0][0].setChecked(True)


class FilterPanel(QWidget):
    """Left-hand parameter panel for the Single-image view.

    Emits selectionChanged whenever any parameter changes. Consumers can call
    current() to get the current ParameterSelection.
    """

    selectionChanged = Signal()
    applyRequested = Signal()
    resetRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("FilterPanel")
        self.setFixedWidth(264)
        self._library: Library | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll, 1)

        body = QWidget()
        body.setObjectName("FilterPanelBody")
        scroll.setWidget(body)
        v = QVBoxLayout(body)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(14)

        # Section: 激光雷达型号
        v.addWidget(self._section_title("激光雷达型号  ·  LIDAR"))
        self.cmb_lidar = QComboBox()
        v.addWidget(self.cmb_lidar)

        # Section: 云类型
        v.addWidget(self._section_title("云类型  ·  CLOUD"))
        self.cmb_cloud = QComboBox()
        v.addWidget(self.cmb_cloud)

        # Section: 偏振方式
        v.addWidget(self._section_title("偏振方式  ·  POLARIZATION"))
        self.chips_pol = _ChipGroup()
        v.addWidget(self.chips_pol)

        # Section: 计算方法
        v.addWidget(self._section_title("计算方法  ·  METHOD"))
        self.chips_method = _ChipGroup()
        v.addWidget(self.chips_method)

        # Section: 云层厚度
        v.addWidget(self._section_title("云层厚度  ·  THICKNESS"))
        self.chips_thickness = _ChipGroup()
        v.addWidget(self.chips_thickness)

        # Section: rFOV
        v.addWidget(self._section_title("接收视场角  ·  rFOV"))
        self.cmb_rfov = QComboBox()
        v.addWidget(self.cmb_rfov)

        # Section: 数据类型
        v.addWidget(self._section_title("数据类型  ·  DATA TYPE"))
        self.chips_datatype = _ChipGroup()
        v.addWidget(self.chips_datatype)

        v.addStretch(1)

        # Bottom action bar
        bar = QFrame()
        bar.setObjectName("FilterFooter")
        bar_l = QHBoxLayout(bar)
        bar_l.setContentsMargins(12, 10, 12, 12)
        bar_l.setSpacing(8)
        self.btn_reset = QPushButton("重置")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_apply = QPushButton("应用筛选")
        self.btn_apply.setObjectName("AccentButton")
        bar_l.addWidget(self.btn_reset)
        bar_l.addWidget(self.btn_apply, 1)
        outer.addWidget(bar)

        self.btn_reset.clicked.connect(self.resetRequested)
        self.btn_apply.clicked.connect(self.applyRequested)

        # Wire change signals
        for w in (self.cmb_lidar, self.cmb_cloud, self.cmb_rfov):
            w.currentIndexChanged.connect(lambda *_: self.selectionChanged.emit())
        for grp in (
            self.chips_pol,
            self.chips_method,
            self.chips_thickness,
            self.chips_datatype,
        ):
            grp.selected.connect(lambda *_: self.selectionChanged.emit())

        # When polarization changes, recompute downstream chip options.
        # noPolar narrows DataType to {TotalReturnSignal} and effectively
        # collapses Method/rFOV to single defaults.
        self.chips_pol.selected.connect(lambda *_: self._refresh_dependents())

    @staticmethod
    def _section_title(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("FilterSectionTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return lbl

    # ---- public API ----

    def set_library(self, library: Library) -> None:
        self._library = library

        self.cmb_lidar.blockSignals(True)
        self.cmb_lidar.clear()
        self.cmb_lidar.addItems(library.lidars)
        self.cmb_lidar.blockSignals(False)

        self.cmb_cloud.blockSignals(True)
        self.cmb_cloud.clear()
        self.cmb_cloud.addItems(library.clouds)
        self.cmb_cloud.blockSignals(False)

        self.chips_pol.set_options(
            [(p.label_cn, p) for p in library.polarizations]
        )
        self.chips_method.set_options(
            [(m.label_cn, m) for m in library.methods]
        )
        self.chips_thickness.set_options(
            [(f"{t}m", t) for t in library.thicknesses]
        )

        self.cmb_rfov.blockSignals(True)
        self.cmb_rfov.clear()
        for r in library.rfovs:
            self.cmb_rfov.addItem("默认" if r == DEFAULT_RFOV else r, r)
        self.cmb_rfov.blockSignals(False)

        self.chips_datatype.set_options(
            [(d.label_cn, d) for d in library.data_types]
        )

        # chips_pol.first() will trigger _refresh_dependents which initializes
        # all downstream chip groups. For an empty library this is a no-op.
        self.chips_pol.first()

    def _refresh_dependents(self) -> None:
        """Recompute Method/Thickness/rFOV/DataType options given current pol."""
        if self._library is None:
            return
        pol = self._chip_value(self.chips_pol, Polarization)
        entries = self._library.entries
        if pol is not None:
            entries = [e for e in entries if e.polarization == pol]
        if not entries:
            return

        methods_set = {e.method for e in entries}
        methods = [m for m in Method if m in methods_set]
        thicknesses = sorted({e.thickness_m for e in entries})
        rfovs_set = {e.rfov for e in entries}
        rfovs = ([DEFAULT_RFOV] if DEFAULT_RFOV in rfovs_set else []) + sorted(
            r for r in rfovs_set if r != DEFAULT_RFOV
        )
        dtypes_set = {e.data_type for e in entries}
        dtypes = [d for d in DataType if d in dtypes_set]

        # Suppress signal storm: each set_options + first() pair would otherwise
        # cascade through selected -> selectionChanged on every group.
        for grp in (self.chips_method, self.chips_thickness, self.chips_datatype):
            grp.blockSignals(True)
        self.cmb_rfov.blockSignals(True)

        self.chips_method.set_options([(m.label_cn, m) for m in methods])
        self.chips_thickness.set_options([(f"{t}m", t) for t in thicknesses])
        self.cmb_rfov.clear()
        for r in rfovs:
            self.cmb_rfov.addItem("默认" if r == DEFAULT_RFOV else r, r)
        self.chips_datatype.set_options([(d.label_cn, d) for d in dtypes])

        self.chips_method.first()
        self.chips_thickness.first()
        self.chips_datatype.first()

        for grp in (self.chips_method, self.chips_thickness, self.chips_datatype):
            grp.blockSignals(False)
        self.cmb_rfov.blockSignals(False)

        # Emit a single coalesced change notification for the whole cascade.
        self.selectionChanged.emit()

    def current(self) -> ParameterSelection:
        return ParameterSelection(
            lidar=self.cmb_lidar.currentText() or None,
            cloud=self.cmb_cloud.currentText() or None,
            polarization=self._chip_value(self.chips_pol, Polarization),
            method=self._chip_value(self.chips_method, Method),
            thickness_m=self._chip_value(self.chips_thickness, int),
            rfov=self.cmb_rfov.currentData() or DEFAULT_RFOV,
            data_type=self._chip_value(self.chips_datatype, DataType),
        )

    @staticmethod
    def _chip_value(group: _ChipGroup, _kind):
        for chip, value in group._chips:  # noqa: SLF001 — intentional internal access
            if chip.isChecked():
                return value
        return None
