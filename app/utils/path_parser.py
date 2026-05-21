from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.models import DEFAULT_RFOV, Method


_FOLDER_RE = re.compile(
    r"^(?P<prefix>[12]_)?(?P<thickness>\d+)m(?:_rFOV(?P<rfov>[\d.]+))?$"
)


@dataclass(frozen=True)
class ParsedLeaf:
    method: Method
    thickness_m: int
    rfov: str  # "default" or numeric string like "0.11"


def parse_leaf_folder(name: str) -> ParsedLeaf | None:
    """Parse 4th-level folder name like '1_100m', '200m', '2_100m_rFOV0.11'.

    Returns None if the folder name does not match the expected schema —
    callers should treat such folders as unrecognized and skip them.
    """
    m = _FOLDER_RE.match(name.strip())
    if not m:
        return None
    prefix = m.group("prefix")
    if prefix == "1_":
        method = Method.STANDARD
    elif prefix == "2_":
        method = Method.ADAPTIVE
    else:
        method = Method.MIXED
    thickness = int(m.group("thickness"))
    rfov_raw = m.group("rfov")
    rfov = rfov_raw if rfov_raw is not None else DEFAULT_RFOV
    return ParsedLeaf(method=method, thickness_m=thickness, rfov=rfov)
