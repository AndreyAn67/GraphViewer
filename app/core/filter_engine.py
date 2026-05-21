from __future__ import annotations

from app.core.models import (
    FilterState,
    ImageEntry,
    Library,
    ParameterSelection,
)


def resolve_single(library: Library, sel: ParameterSelection) -> ImageEntry | None:
    """Return the unique entry matching a fully-specified ParameterSelection."""
    if not sel.is_complete():
        return None
    for e in library.entries:
        if (
            e.lidar == sel.lidar
            and e.cloud == sel.cloud
            and e.polarization == sel.polarization
            and e.method == sel.method
            and e.thickness_m == sel.thickness_m
            and e.rfov == sel.rfov
            and e.data_type == sel.data_type
        ):
            return e
    return None


def filter_entries(library: Library, state: FilterState) -> list[ImageEntry]:
    return [e for e in library.entries if state.matches(e)]
