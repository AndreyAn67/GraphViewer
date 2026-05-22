from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.models import DEFAULT_RFOV, ImageEntry

if TYPE_CHECKING:
    from app.i18n import Translator


def format_breadcrumb(entry: ImageEntry, tr: "Translator") -> str:
    rfov_label = entry.rfov if entry.rfov != DEFAULT_RFOV else tr.tr("enum.rfov.default")
    return (
        f"{entry.lidar} / {entry.cloud} / {tr.tr(entry.polarization.label_key)} / "
        f"{tr.tr(entry.method.label_key)} {entry.thickness_m}m / rFOV={rfov_label} / "
        f"{tr.tr(entry.data_type.label_key)}"
    )
