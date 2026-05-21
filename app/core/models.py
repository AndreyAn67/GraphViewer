from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Polarization(str, Enum):
    CIRC = "CircPolar"
    LINEAR = "Polar"
    NONE = "noPolar"

    @property
    def label_cn(self) -> str:
        return {
            Polarization.CIRC: "圆偏振",
            Polarization.LINEAR: "线偏振",
            Polarization.NONE: "无偏振",
        }[self]


class Method(str, Enum):
    STANDARD = "Standard"
    ADAPTIVE = "Adaptive"
    MIXED = "Mixed"

    @property
    def label_cn(self) -> str:
        return {
            Method.STANDARD: "标准",
            Method.ADAPTIVE: "自适应",
            Method.MIXED: "混合",
        }[self]


class DataType(str, Enum):
    ERROR_TOTAL = "error_total"
    IQUV_I = "IQUV_I"
    STOKES_DEPDEG = "Stokes_IQUV_DePDeg"
    STOKES_DOP = "Stokes_IQUV_Dop"
    STOKES_PREANG = "Stokes_IQUV_PreAng"
    TOTAL_RETURN_SIGNAL = "TotalReturnSignal"  # noPolar only

    @property
    def label_cn(self) -> str:
        return {
            DataType.ERROR_TOTAL: "总误差",
            DataType.IQUV_I: "强度 I",
            DataType.STOKES_DEPDEG: "退偏度 DoLP",
            DataType.STOKES_DOP: "偏振度 DoP",
            DataType.STOKES_PREANG: "偏振角 PreAng",
            DataType.TOTAL_RETURN_SIGNAL: "总回波信号",
        }[self]

    @property
    def filename(self) -> str:
        return f"{self.value}.png"


DEFAULT_RFOV = "default"


@dataclass(frozen=True)
class ImageEntry:
    lidar: str
    cloud: str
    polarization: Polarization
    method: Method
    thickness_m: int
    rfov: str
    data_type: DataType
    path: Path

    def breadcrumb(self) -> str:
        rfov_label = self.rfov if self.rfov != DEFAULT_RFOV else "默认"
        return (
            f"{self.lidar} / {self.cloud} / {self.polarization.label_cn} / "
            f"{self.method.label_cn} {self.thickness_m}m / rFOV={rfov_label} / "
            f"{self.data_type.label_cn}"
        )


@dataclass
class FilterState:
    lidar: str | None = None
    cloud: str | None = None
    polarizations: set[Polarization] = field(default_factory=set)
    methods: set[Method] = field(default_factory=set)
    thicknesses: set[int] = field(default_factory=set)
    rfovs: set[str] = field(default_factory=set)
    data_types: set[DataType] = field(default_factory=set)

    def matches(self, entry: ImageEntry) -> bool:
        if self.lidar and entry.lidar != self.lidar:
            return False
        if self.cloud and entry.cloud != self.cloud:
            return False
        if self.polarizations and entry.polarization not in self.polarizations:
            return False
        if self.methods and entry.method not in self.methods:
            return False
        if self.thicknesses and entry.thickness_m not in self.thicknesses:
            return False
        if self.rfovs and entry.rfov not in self.rfovs:
            return False
        if self.data_types and entry.data_type not in self.data_types:
            return False
        return True


@dataclass
class ParameterSelection:
    """A single fully-specified parameter combination identifying one image."""

    lidar: str | None = None
    cloud: str | None = None
    polarization: Polarization | None = None
    method: Method | None = None
    thickness_m: int | None = None
    rfov: str = DEFAULT_RFOV
    data_type: DataType | None = None

    def is_complete(self) -> bool:
        return all(
            v is not None
            for v in (
                self.lidar,
                self.cloud,
                self.polarization,
                self.method,
                self.thickness_m,
                self.data_type,
            )
        )


@dataclass
class Library:
    """In-memory index of all available images discovered under sources/pics/."""

    entries: list[ImageEntry] = field(default_factory=list)
    lidars: list[str] = field(default_factory=list)
    clouds: list[str] = field(default_factory=list)
    polarizations: list[Polarization] = field(default_factory=list)
    methods: list[Method] = field(default_factory=list)
    thicknesses: list[int] = field(default_factory=list)
    rfovs: list[str] = field(default_factory=list)
    data_types: list[DataType] = field(default_factory=list)
