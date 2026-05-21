from __future__ import annotations

from pathlib import Path

from app.core.models import (
    DataType,
    ImageEntry,
    Library,
    Method,
    Polarization,
)
from app.utils.path_parser import parse_leaf_folder


IGNORED_DIRS = {"Multiple scattering"}


def _try_polarization(name: str) -> Polarization | None:
    for p in Polarization:
        if p.value == name:
            return p
    return None


def scan_library(pics_root: Path) -> Library:
    """Walk sources/pics/ and build a complete in-memory index.

    Folder hierarchy expected:
        <pics_root>/<Lidar>/<Cloud>/<Polarization>/<method+thickness[_rFOV]>/<*.png>

    Unrecognized leaf folder names are skipped silently (the user will see
    them missing from the filter chips, which is the desired feedback).
    """
    lib = Library()
    if not pics_root.is_dir():
        return lib

    lidars: set[str] = set()
    clouds: set[str] = set()
    pols: set[Polarization] = set()
    methods: set[Method] = set()
    thicknesses: set[int] = set()
    rfovs: set[str] = set()
    data_types: set[DataType] = set()

    for lidar_dir in sorted(pics_root.iterdir()):
        if not lidar_dir.is_dir() or lidar_dir.name in IGNORED_DIRS:
            continue
        for cloud_dir in sorted(lidar_dir.iterdir()):
            if not cloud_dir.is_dir() or cloud_dir.name in IGNORED_DIRS:
                continue
            for pol_dir in sorted(cloud_dir.iterdir()):
                if not pol_dir.is_dir() or pol_dir.name in IGNORED_DIRS:
                    continue
                pol = _try_polarization(pol_dir.name)
                if pol is None:
                    continue
                for leaf_dir in sorted(pol_dir.iterdir()):
                    if not leaf_dir.is_dir() or leaf_dir.name in IGNORED_DIRS:
                        continue
                    parsed = parse_leaf_folder(leaf_dir.name)
                    if parsed is None:
                        continue
                    for dt in DataType:
                        f = leaf_dir / dt.filename
                        if not f.is_file():
                            continue
                        entry = ImageEntry(
                            lidar=lidar_dir.name,
                            cloud=cloud_dir.name,
                            polarization=pol,
                            method=parsed.method,
                            thickness_m=parsed.thickness_m,
                            rfov=parsed.rfov,
                            data_type=dt,
                            path=f,
                        )
                        lib.entries.append(entry)
                        lidars.add(entry.lidar)
                        clouds.add(entry.cloud)
                        pols.add(entry.polarization)
                        methods.add(entry.method)
                        thicknesses.add(entry.thickness_m)
                        rfovs.add(entry.rfov)
                        data_types.add(entry.data_type)

    lib.lidars = sorted(lidars)
    lib.clouds = sorted(clouds)
    lib.polarizations = [p for p in Polarization if p in pols]
    lib.methods = [m for m in Method if m in methods]
    lib.thicknesses = sorted(thicknesses)
    # 'default' first, then numeric sorted
    numeric_rfov = sorted(r for r in rfovs if r != "default")
    lib.rfovs = (["default"] if "default" in rfovs else []) + numeric_rfov
    lib.data_types = [d for d in DataType if d in data_types]
    return lib
