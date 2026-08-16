#
# Copyright 2025 translate-toolkit contributors
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

r"""Class that manages TOML data files for translation."""

from __future__ import annotations

import uuid
from io import BytesIO
from typing import IO, TYPE_CHECKING, Any, cast

from tomlrt import Array, Document, Table, TOMLError, dump, load

from translate.lang.data import cldr_plural_categories
from translate.misc.multistring import multistring
from translate.storage import base

if TYPE_CHECKING:
    from collections.abc import Generator


class TOMLUnit(base.DictUnit):
    """
    A TOML translation unit.

    Represents a single translatable string extracted from a TOML file.
    """

    # New nested mappings are rendered as ``[section]`` blocks, not inline tables.
    dict_factory = Table.section

    def __init__(self, source=None, **kwargs) -> None:
        """Initialize a TOML unit with optional source text."""
        # Ensure we have ID (for serialization)
        if source:
            self.source = source
            self._id = hex(hash(source))
        else:
            self._id = str(uuid.uuid4())
        super().__init__(source)

    def setid(self, value, unitid=None) -> None:
        """Set the unit ID, stripping leading separator if present."""
        # Strip leading separator from the string representation
        if isinstance(value, str) and value.startswith(self.IdClass.KEY_SEPARATOR):
            value = value[len(self.IdClass.KEY_SEPARATOR) :]
        self._id = value
        self._unitid = unitid

    @property
    def source(self):
        """Source text (alias for target in monolingual format)."""
        return self.target

    @source.setter
    def source(self, source) -> None:
        """Set the source text (alias for target in monolingual format)."""
        self.target = source

    def getid(self):
        """Get the unit identifier."""
        return self._id

    def getcontext(self):
        return self._id

    def getlocations(self):
        """Get the location(s) of this unit (returns the ID as a single-element list)."""
        return [self.getid()]

    def convert_target(self):
        """Convert the target value for serialization (returns as-is for plain TOML)."""
        return self.target

    def storevalues(self, output: dict[str, Any] | list[Any]) -> None:
        """Store this unit's value in the output structure."""
        self.storevalue(output, self.convert_target())


class TOMLFile(base.DictStore[TOMLUnit]):
    """
    A TOML localization file.

    Handles plain TOML files with key-value pairs and nested structures.
    Uses tomlrt library to preserve formatting and comments during roundtrips.
    """

    UnitClass = TOMLUnit

    def __init__(self, inputfile=None, **kwargs) -> None:
        """Construct a TOML file, optionally reading from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self._original = self.get_root_node()
        if inputfile is not None:
            self.parse(inputfile)

    def get_root_node(self) -> Document:
        """Return an empty root node for serialization."""
        return Document()

    def serialize(self, out: IO[bytes]) -> None:
        """Serialize the store to a file."""
        # Always start with valid root even if original file was empty
        if self._original is None:
            self._original = self.get_root_node()

        self.serialize_units(self._original)

        dump(self._original, out)

    def _parse_dict(
        self,
        data: Table | Document,
        prev: base.UnitId,
    ) -> Generator[tuple[base.UnitId, str, str]]:
        """Parse a TOML table/dictionary recursively, yielding units."""
        comments = data.leading_comments
        for k, v in data.items():
            yield from self._flatten(
                v, prev.extend("key", k), comment="\n".join(comments.get(k, ()))
            )

    def _flatten(
        self,
        data: Any,
        prev: base.UnitId | None = None,
        comment: str = "",
    ) -> Generator[tuple[base.UnitId, str, str]]:
        """
        Flatten TOML structure recursively into translatable units.

        Converts nested TOML structures into flat units with hierarchical IDs
        and extracts comments associated with keys when available.
        """
        if prev is None:
            prev = self.UnitClass.IdClass([])
        if isinstance(data, dict):
            yield from self._parse_dict(data, prev)
        elif isinstance(data, str):
            yield (prev, data, comment)
        elif isinstance(data, (bool, int, float)):
            yield (prev, str(data), comment)
        elif isinstance(data, list):
            # Only an Array carries element comments; an AoT keeps them on the
            # headers of its entries, which _parse_dict reads.
            comments = data.leading_comments if isinstance(data, Array) else {}
            for k, v in enumerate(data):
                yield from self._flatten(
                    v, prev.extend("index", k), comment="\n".join(comments.get(k, ()))
                )
        elif data is None:
            pass
        else:
            raise ValueError(
                "We don't handle these values:\n"
                f"Type: {type(data)}\n"
                f"Data: {data}\n"
                f"Previous: {prev}"
            )

    def parse(self, input: str | bytes | BytesIO) -> None:  # ty:ignore[invalid-method-override]
        """
        Parse the given file, file object, or string content.

        Extracts translatable units from TOML content and stores them
        with their associated comments.
        """
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            src = input.read()  # ty:ignore[call-non-callable]
            input.close()  # ty:ignore[unresolved-attribute]
            input = src
        if isinstance(input, str):
            # TOML is defined to be UTF-8, load() decodes it as such.
            input = input.encode("utf-8")
        if input and not input.endswith(b"\n"):
            # Ensure output ends with a newline, matching the file's line endings.
            input += b"\r\n" if b"\r\n" in input else b"\n"
        try:
            self._original = load(BytesIO(input))
        except TOMLError as e:
            raise base.ParseError(e) from e

        for k, data, comment in self._flatten(self._original):
            unit = self.UnitClass(data)
            unit.set_unitid(k)
            if comment:
                unit.addnote(comment, origin="developer")
            self.addunit(unit)

    def removeunit(self, unit: base.TranslationUnit) -> None:
        """Remove a unit from the store and its underlying TOML structure."""
        if self._original is not None:
            unit.storevalue(self._original, None, unset=True)  # ty:ignore[unresolved-attribute]
        super().removeunit(unit)  # ty:ignore[invalid-argument-type]


class GoI18nTOMLUnit(TOMLUnit):
    """
    A TOML entry for Go i18n format with plural support.

    Handles CLDR plural categories (zero, one, two, few, many, other) for
    pluralized strings used in Go applications and Hugo static sites.
    """

    def hasplural(self) -> bool:
        """Check if this unit contains plural strings (more than one form)."""
        return isinstance(self.target, multistring) and len(self.target.strings) > 1

    def convert_target(self) -> Table:
        """
        Convert the target value for serialization.

        For Go i18n format, returns a table with CLDR plural category keys.
        Singular strings are wrapped in {"other": value} to preserve structure.
        """
        if not isinstance(self.target, multistring):
            # For Go i18n format, even singular strings should be in a table with "other"
            # key to preserve the table structure
            return Table.section({"other": self.target})

        tags = self._store.get_plural_tags(self.target)  # ty:ignore[unresolved-attribute]

        # Sync plural_strings elements to plural_tags count. TOML has no null, so
        # untranslated forms are serialized as blank strings.
        strings = self.sync_plural_count(self.target, tags)

        # Return a table with plural tags as keys
        return Table.section(dict(zip(tags, strings, strict=True)))


class GoI18nTOMLFile(TOMLFile):
    """
    TOML file for Go i18n format with plural support.

    This format uses CLDR plural categories (zero, one, two, few, many, other)
    as keys for pluralized strings. It's commonly used by:
    - Go applications using the go-i18n library
    - Hugo static site generators (e.g., Anatole theme)
    - Let's Encrypt website translations

    Example::

        [reading_time]
        one = "One minute to read"
        other = "{{ .Count }} minutes to read"

        [category]
        other = "category"  # Single "other" key treated as singular

    """

    UnitClass = GoI18nTOMLUnit

    def _parse_dict(
        self,
        data: Table | Document,
        prev: base.UnitId,
    ) -> Generator[tuple[base.UnitId, str | multistring, str]]:
        """
        Parse a TOML table, checking for plural forms.

        Detects pluralized strings where all keys are CLDR plural categories.
        Special case: a table with only "other" key is treated as singular.

        Such a table is a single unit, so its header comment is that unit's note.
        """
        header_comment = "\n".join(data.header_leading_comments)

        # Special case: table with only "other" key is treated as singular
        if data and len(data) == 1 and "other" in data:
            yield (prev, str(data["other"]), header_comment)
            return

        # Does this look like a plural?
        # Need at least 2 keys and all keys must be CLDR plural categories
        if data and len(data) >= 2 and all(x in cldr_plural_categories for x in data):
            # Extract plural forms in CLDR order
            values = cast(
                "list[str]",
                [data[tag] for tag in cldr_plural_categories if tag in data],
            )

            # Skip blank values (all plurals are None or empty)
            if values and not all(not value for value in values):
                # Use blank string instead of None for missing forms
                yield (prev, multistring(values), header_comment)

            return

        # Handle normal dict
        yield from super()._parse_dict(data, prev)
