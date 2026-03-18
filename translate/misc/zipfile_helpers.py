#
# Copyright 2026 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import zipfile
    from collections.abc import Iterable

MAX_ARCHIVE_MEMBER_SIZE = 64 * 1024 * 1024
MAX_ARCHIVE_TOTAL_SIZE = 128 * 1024 * 1024


def validate_archive_members(
    members: Iterable[zipfile.ZipInfo],
    *,
    validate_total_size: bool = True,
) -> list[zipfile.ZipInfo]:
    """Validate archive members before reading them into memory."""
    selected = [info for info in members if not info.is_dir()]
    if validate_total_size:
        total_size = sum(info.file_size for info in selected)
        if total_size > MAX_ARCHIVE_TOTAL_SIZE:
            raise ValueError(
                f"archive members are too large after decompression: {total_size} bytes"
            )
    for info in selected:
        if info.file_size > MAX_ARCHIVE_MEMBER_SIZE:
            raise ValueError(
                f"archive member {info.filename!r} is too large after decompression: "
                f"{info.file_size} bytes"
            )
    return selected


def read_archive_members(
    archive: zipfile.ZipFile,
    members: Iterable[zipfile.ZipInfo],
    *,
    validate_total_size: bool = True,
) -> dict[str, bytes]:
    """
    Read archive members after validating their uncompressed sizes.

    Callers choose the member selection policy. This helper applies the shared
    size limits and then reads the selected members into memory.
    """
    selected = validate_archive_members(
        members,
        validate_total_size=validate_total_size,
    )
    return {info.filename: archive.read(info.filename) for info in selected}
