#
# Copyright 2008, 2014 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import copy
import posixpath
import zipfile
from os import PathLike
from typing import IO, TYPE_CHECKING, Self
from urllib.parse import unquote, urlsplit

from lxml import etree

from translate.misc.xml_helpers import parse_xml
from translate.misc.zipfile_helpers import (
    read_archive_members,
    validate_archive_members,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

ZipInput = str | PathLike[str] | IO[bytes]

ODF_MEMBER_NAMES = ("content.xml", "styles.xml", "meta.xml")
ODF_MIMETYPE_PREFIX = "application/vnd.oasis.opendocument."
MANIFEST_NS = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
MANIFEST_FULL_PATH = f"{{{MANIFEST_NS}}}full-path"
MANIFEST_MEDIA_TYPE = f"{{{MANIFEST_NS}}}media-type"


def _normalise_member_path(path: str) -> str:
    """Return the ZIP member spelling used for a manifest path or reference."""
    path = unquote(urlsplit(path).path).removeprefix("./").rstrip("/")
    normalised = posixpath.normpath(path)
    return "" if normalised in {"", ".", "/"} else normalised.lstrip("/")


def _clone_info(info: zipfile.ZipInfo, *, stored: bool = False) -> zipfile.ZipInfo:
    cloned = copy.copy(info)
    if stored:
        cloned.compress_type = zipfile.ZIP_STORED
        cloned.extra = b""
    return cloned


class ODFPackage:
    """Reader and writer for the XML members of an ODF package."""

    def __init__(self, source: ZipInput) -> None:
        self.archive = zipfile.ZipFile(source, "r")
        self._infos = {info.filename: info for info in self.archive.infolist()}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self.archive.close()

    def _manifest_subdocuments(self) -> list[str]:
        """Return embedded ODF directory names in manifest order."""
        info = self._infos.get("META-INF/manifest.xml")
        if info is None:
            return []

        validate_archive_members([info])
        manifest = parse_xml(self.archive.read(info), collect_ids=False)
        result: list[str] = []
        for entry in manifest.iter(f"{{{MANIFEST_NS}}}file-entry"):
            media_type = entry.get(MANIFEST_MEDIA_TYPE, "")
            full_path = entry.get(MANIFEST_FULL_PATH, "")
            directory = _normalise_member_path(full_path)
            if (
                directory
                and full_path.endswith("/")
                and media_type.startswith(ODF_MIMETYPE_PREFIX)
                and any(
                    f"{directory}/{member}" in self._infos
                    for member in ("content.xml", "styles.xml")
                )
                and directory not in result
            ):
                result.append(directory)
        return result

    def _referenced_subdocuments(self, candidates: list[str]) -> list[str]:
        """Order embedded documents by first reference in the main XML."""
        remaining = set(candidates)
        result: list[str] = []
        for member in ("content.xml", "styles.xml"):
            info = self._infos.get(member)
            if info is None:
                continue
            validate_archive_members([info])
            root = parse_xml(self.archive.read(info), collect_ids=False)
            for element in root.iter():
                for attribute, value in element.attrib.items():
                    if etree.QName(attribute).localname != "href":
                        continue
                    referenced = _normalise_member_path(value)
                    if referenced in remaining:
                        remaining.remove(referenced)
                        result.append(referenced)
        result.extend(candidate for candidate in candidates if candidate in remaining)
        return result

    def translatable_members(self) -> list[zipfile.ZipInfo]:
        """Return translatable XML members in stable document-reading order."""
        if not any(member in self._infos for member in ("content.xml", "styles.xml")):
            raise KeyError("ODF package has neither content.xml nor styles.xml")

        names: list[str] = []
        if "content.xml" in self._infos:
            names.append("content.xml")

        for directory in self._referenced_subdocuments(self._manifest_subdocuments()):
            names.extend(
                path
                for member in ODF_MEMBER_NAMES
                if (path := f"{directory}/{member}") in self._infos
            )

        names.extend(
            member for member in ("styles.xml", "meta.xml") if member in self._infos
        )
        return [self._infos[name] for name in names]

    def read_translatable_members(self) -> dict[str, bytes]:
        """Read and validate all translatable XML members."""
        return read_archive_members(self.archive, self.translatable_members())

    def write(self, target: ZipInput, replacements: Mapping[str, bytes]) -> None:
        """Copy the package to target, replacing selected members safely."""
        infos = self.archive.infolist()
        validate_archive_members(infos, validate_total_size=False)
        with zipfile.ZipFile(target, "w") as output:
            mimetype = self._infos.get("mimetype")
            if mimetype is not None:
                output.writestr(
                    _clone_info(mimetype, stored=True),
                    replacements.get("mimetype", self.archive.read(mimetype)),
                )
            for info in infos:
                if info.filename == "mimetype":
                    continue
                cloned = _clone_info(info)
                if info.is_dir():
                    output.writestr(cloned, b"")
                else:
                    output.writestr(
                        cloned,
                        replacements.get(info.filename, self.archive.read(info)),
                    )


def open_odf(filename: ZipInput) -> dict[str, bytes]:
    with ODFPackage(filename) as package:
        return package.read_translatable_members()


def copy_odf(
    input_zip: zipfile.ZipFile,
    output_zip: zipfile.ZipFile,
    exclusion_list: Collection[str],
) -> zipfile.ZipFile:
    selected = [
        info for info in input_zip.infolist() if info.filename not in exclusion_list
    ]
    validate_archive_members(selected, validate_total_size=False)
    mimetype = next(
        (info for info in selected if info.filename == "mimetype"),
        None,
    )
    if mimetype is not None:
        output_zip.writestr(
            _clone_info(mimetype, stored=True),
            input_zip.read(mimetype),
        )
    for info in selected:
        if info.filename == "mimetype":
            continue
        if info.is_dir():
            output_zip.writestr(_clone_info(info), b"")
            continue
        output_zip.writestr(_clone_info(info), input_zip.read(info))
    return output_zip
