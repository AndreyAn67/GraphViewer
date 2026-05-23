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
from app.i18n import Translator
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

    def relabel(self, label_for_value) -> None:
        for chip, value in self._chips:
            chip.setText(label_for_value(value))


class FilterPanel(QWidget):
    """Left-hand parameter panel for the Single-image view.

    Emits selectionChanged whenever any parameter changes. Consumers can call
    current() to get the current ParameterSelection.
    """

    selectionChanged = Signal()
    applyRequested = Signal()
    resetRequested = Signal()

    def __init__(self, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("FilterPanel")
        # Resizable via the host QSplitter. Only a minimum is clamped here —
        # the upper bound is left to the splitter so the user can drag freely.
        self.setMinimumWidth(200)
        self._i18n = translator
        self._library: Library | None = None
        # Section title labels keyed by catalog key, for retranslation.
        self._section_titles: dict[str, QLabel] = {}

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

        v.addWidget(self._section_title("filter.section.lidar"))
        self.cmb_lidar = QComboBox()
        v.addWidget(self.cmb_lidar)

        v.addWidget(self._section_title("filter.section.cloud"))
        self.cmb_cloud = QComboBox()
        v.addWidget(self.cmb_cloud)

        v.addWidget(self._section_title("filter.section.polarization"))
        self.chips_pol = _ChipGroup()
        v.addWidget(self.chips_pol)

        v.addWidget(self._section_title("filter.section.method"))
        self.chips_method = _ChipGroup()
        v.addWidget(self.chips_method)

        v.addWidget(self._section_title("filter.section.thickness"))
        self.chips_thickness = _ChipGroup()
        v.addWidget(self.chips_thickness)

        v.addWidget(self._section_title("filter.section.rfov"))
        self.cmb_rfov = QComboBox()
        v.addWidget(self.cmb_rfov)

        v.addWidget(self._section_title("filter.section.data_type"))
        self.chips_datatype = _ChipGroup()
        v.addWidget(self.chips_datatype)

        v.addStretch(1)

        # Bottom action bar
        bar = QFrame()
        bar.setObjectName("FilterFooter")
        bar_l = QHBoxLayout(bar)
        bar_l.setContentsMargins(12, 10, 12, 12)
        bar_l.setSpacing(8)
        self.btn_reset = QPushButton("")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_apply = QPushButton("")
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

        self._i18n.languageChanged.connect(self.retranslate)
        self.retranslate()

    def _section_title(self, key: str) -> QLabel:
        lbl = QLabel("")
        lbl.setObjectName("FilterSectionTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._section_titles[key] = lbl
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
            [(self._i18n.tr(p.label_key), p) for p in library.polarizations]
        )
        self.chips_method.set_options(
            [(self._i18n.tr(m.label_key), m) for m in library.methods]
        )
        self.chips_thickness.set_options(
            [(f"{t}m", t) for t in library.thicknesses]
        )

        self.cmb_rfov.blockSignals(True)
        self.cmb_rfov.clear()
        for r in library.rfovs:
            label = self._i18n.tr("enum.rfov.default") if r == DEFAULT_RFOV else r
            self.cmb_rfov.addItem(label, r)
        self.cmb_rfov.blockSignals(False)

        self.chips_datatype.set_options(
            [(self._i18n.tr(d.label_key), d) for d in library.data_types]
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

        self.chips_method.set_options(
            [(self._i18n.tr(m.label_key), m) for m in methods]
        )
        self.chips_thickness.set_options([(f"{t}m", t) for t in thicknesses])
        self.cmb_rfov.clear()
        for r in rfovs:
            label = self._i18n.tr("enum.rfov.default") if r == DEFAULT_RFOV else r
            self.cmb_rfov.addItem(label, r)
        self.chips_datatype.set_options(
            [(self._i18n.tr(d.label_key), d) for d in dtypes]
        )

        self.chips_method.first()
        self.chips_thickness.first()
        self.chips_datatype.first()

        for grp in (self.chips_method, self.chips_thickness, self.chips_datatype):
            grp.blockSignals(False)
        self.cmb_rfov.blockSignals(False)

        # Emit a single coalesced change notification for the whole cascade.
        self.selectionChanged.emit()

    def retranslate(self) -> None:
        for key, lbl in self._section_titles.items():
            lbl.setText(self._i18n.tr(key))
        self.btn_reset.setText(self._i18n.tr("filter.reset"))
        self.btn_apply.setText(self._i18n.tr("filter.apply"))
        # Relabel chips in place to avoid widget churn + selection loss.
        self.chips_pol.relabel(lambda v: self._i18n.tr(v.label_key))
        self.chips_method.relabel(lambda v: self._i18n.tr(v.label_key))
        self.chips_thickness.relabel(lambda v: f"{v}m")
        self.chips_datatype.relabel(lambda v: self._i18n.tr(v.label_key))
        # rFOV combo items: walk and rewrite the display text for DEFAULT.
        for i in range(self.cmb_rfov.count()):
            r = self.cmb_rfov.itemData(i)
            label = self._i18n.tr("enum.rfov.default") if r == DEFAULT_RFOV else r
            self.cmb_rfov.setItemText(i, label)

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
