#
# Copyright 2014 Zuza Software Foundation
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

import zipfile
from os import PathLike
from typing import IO, TYPE_CHECKING

from translate.misc.zipfile_helpers import (
    read_archive_members,
    validate_archive_members,
)

if TYPE_CHECKING:
    from collections.abc import Collection

ZipInput = str | PathLike[str] | IO[bytes]

# Tags to be extracted as placeables (tags that are within translatable texts).
INLINE_ELEMENTS = [
    ("", "CharacterStyleRange"),
    ("", "Content"),
    # ('', 'Br'),
]


# Skipping one of these tags doesn't imply nested acceptable tags are not
# extracted.
NO_TRANSLATE_ELEMENTS = [
    ("http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging", "Story"),
    ("", "Story"),  # This is a different Story tag than the one above.
    ("", "StoryPreference"),
    ("", "InCopyExportOption"),
    # ('', 'ParagraphStyleRange'),
    # ('', 'CharacterStyleRange'),
    ("", "MetadataPacketPreference"),
    ("", "Contents"),  # Don't confuse with Content tag. This tag contains a
    # lot of CDATA we don't want to parse.
    ("", "Properties"),
    ("", "Leading"),
    ("", "AppliedFont"),
    ("", "TextFrame"),
    ("", "PathGeometry"),
    ("", "GeometryPathType"),
    ("", "PathPointArray"),
    ("", "PathPointType"),
    ("", "AnchoredObjectSetting"),
    ("", "TextFramePreference"),
    ("", "TextWrapPreference"),
    ("", "TextWrapOffset"),
    ("", "ContourOption"),
    ("", "EPS"),
    ("", "GraphicBounds"),
    ("", "Link"),
    ("", "ClippingPathSettings"),
    ("", "FrameFittingOption"),
    ("", "ObjectExportOption"),
    ("", "AltMetadataProperty"),
    ("", "ActualMetadataProperty"),
    ("", "TabList"),
    ("", "ListItem"),
    ("", "Alignment"),
    ("", "AlignmentCharacter"),
    ("", "Leader"),
    ("", "Position"),
    ("", "Rectangle"),
    # ('', 'Br'),
]


def open_idml(filename: ZipInput) -> dict[str, bytes]:
    with zipfile.ZipFile(filename, "r") as z:
        selected = [
            info for info in z.infolist() if info.filename.startswith("Stories/")
        ]
        return read_archive_members(z, selected)


def copy_idml(
    input_zip: zipfile.ZipFile,
    output_zip: zipfile.ZipFile,
    exclusion_list: Collection[str],
) -> zipfile.ZipFile:
    selected = [
        input_zip.getinfo(name)
        for name in input_zip.namelist()
        if name not in exclusion_list
    ]
    validate_archive_members(selected, validate_total_size=False)
    for info in selected:
        if info.is_dir():
            output_zip.writestr(info.filename, b"")
            continue
        output_zip.writestr(info.filename, input_zip.read(info.filename))
    return output_zip
