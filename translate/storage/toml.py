#
# Copyright 2025 translate-toolkit contributors
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

r"""Class that manages TOML data files for translation."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from tomlkit import TOMLDocument, document, loads
from tomlkit.exceptions import TOMLKitError
from tomlkit.items import Comment as TOMLComment
from tomlkit.items import Table

from translate.lang.data import cldr_plural_categories
from translate.misc.multistring import multistring
from translate.storage import base

if TYPE_CHECKING:
    from collections.abc import Generator
    from io import BytesIO


class TOMLUnit(base.DictUnit):
    """
    A TOML translation unit.

    Represents a single translatable string extracted from a TOML file.
    """

    def __init__(self, source=None, **kwargs):
        """Initialize a TOML unit with optional source text."""
        # Ensure we have ID (for serialization)
        if source:
            self.source = source
            self._id = hex(hash(source))
        else:
            self._id = str(uuid.uuid4())
        super().__init__(source)

    def setid(self, value, unitid=None):
        """Set the unit ID, stripping leading separator if present."""
        # Strip leading separator from the string representation
        if isinstance(value, str) and value.startswith(self.IdClass.KEY_SEPARATOR):
            value = value[len(self.IdClass.KEY_SEPARATOR) :]
        self._id = value
        self._unitid = unitid

    @property
    def source(self):
        """Get the source text (alias for target in monolingual format)."""
        return self.target

    @source.setter
    def source(self, source):
        """Set the source text (alias for target in monolingual format)."""
        self.target = source

    def getid(self):
        """Get the unit identifier."""
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


class TOMLFile(base.DictStore):
    """
    A TOML localization file.

    Handles plain TOML files with key-value pairs and nested structures.
    Uses tomlkit library to preserve formatting and comments during roundtrips.
    """

    UnitClass = TOMLUnit

    def __init__(self, inputfile=None, **kwargs):
        """Construct a TOML file, optionally reading from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self._original = self.get_root_node()
        if inputfile is not None:
            self.parse(inputfile)

    def get_root_node(self) -> TOMLDocument:
        """Return an empty root node for serialization."""
        return document()

    def serialize(self, out: BytesIO) -> None:
        """Serialize the store to a file."""
        # Always start with valid root even if original file was empty
        if self._original is None:
            self._original = self.get_root_node()

        self.serialize_units(self._original)

        # Convert TOMLDocument to string
        result = self._original.as_string()
        # Add trailing newline if not empty and not already present
        if result and not result.endswith("\n"):
            result += "\n"

        # Write to file
        out.write(result.encode(self.encoding))

    def _get_key_comment(
        self, table: Table | TOMLDocument | None, key: str | int | None
    ) -> str | None:
        """
        Extract the comment that appears before a key in a TOML table.

        TOML comments appear in the body as (None, Comment) tuples.
        Returns comment text without the '#' prefix, or None if no comment.
        """
        if not isinstance(table, (Table, TOMLDocument)):
            return None

        # Check if the table has a body attribute
        if not hasattr(table, "body"):
            return None

        # Find comments that appear before this key in the body
        comments = []

        for item in table.body:
            if not isinstance(item, tuple) or len(item) != 2:
                continue

            item_key, item_value = item

            # If this is our key, we found it
            if item_key is not None and str(item_key).strip() == str(key):
                # Return the collected comments for this key
                return "\n".join(comments) if comments else None

            # If we hit another key before finding ours, reset comments
            if item_key is not None:
                comments = []
                continue

            # Collect comments that appear before our key
            # Check if this is a Comment (not Whitespace)
            if item_key is None and isinstance(item_value, TOMLComment):
                # Get the comment text directly
                comment_text = str(item_value)
                if comment_text.startswith("#"):
                    comments.append(comment_text[1:].strip())

        return None

    def _parse_dict(
        self, data: dict[str, Any], prev: base.UnitId
    ) -> Generator[tuple[base.UnitId, str, str | None]]:
        """Parse a TOML table/dictionary recursively, yielding units."""
        for k, v in data.items():
            yield from self._flatten(v, prev.extend("key", k), parent_map=data, key=k)

    def _flatten(
        self,
        data: Any,
        prev: base.UnitId | None = None,
        parent_map: dict[str, Any] | list[Any] | None = None,
        key: str | int | None = None,
    ) -> Generator[tuple[base.UnitId, str, str | None]]:
        """
        Flatten TOML structure recursively into translatable units.

        Converts nested TOML structures into flat units with hierarchical IDs
        and extracts comments associated with keys when available.
        """
        if prev is None:
            prev = self.UnitClass.IdClass([])
        if isinstance(data, (Table, TOMLDocument, dict)):
            yield from self._parse_dict(data, prev)
        elif isinstance(data, str):
            yield (prev, data, self._get_key_comment(parent_map, key))
        elif isinstance(data, (bool, int, float)):
            yield (prev, str(data), self._get_key_comment(parent_map, key))
        elif isinstance(data, list):
            for k, v in enumerate(data):
                yield from self._flatten(
                    v, prev.extend("index", k), parent_map=data, key=k
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

    def parse(self, input: str | bytes | BytesIO) -> None:
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
            src = input.read()
            input.close()
            input = src
        if isinstance(input, bytes):
            input = input.decode(self.encoding)
        try:
            self._original = loads(input)
        except TOMLKitError as e:
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
            unit.storevalue(self._original, None, unset=True)
        super().removeunit(unit)


class GoI18nTOMLUnit(TOMLUnit):
    """
    A TOML entry for Go i18n format with plural support.

    Handles CLDR plural categories (zero, one, two, few, many, other) for
    pluralized strings used in Go applications and Hugo static sites.
    """

    def hasplural(self) -> bool:
        """Check if this unit contains plural strings (more than one form)."""
        return isinstance(self.target, multistring) and len(self.target.strings) > 1

    def convert_target(self) -> str | dict[str, str | None]:
        """
        Convert the target value for serialization.

        For Go i18n format, returns a dict with CLDR plural category keys.
        Singular strings are wrapped in {"other": value} to preserve structure.
        """
        if not isinstance(self.target, multistring):
            # For Go i18n format, even singular strings should be in a dict with "other" key
            # to preserve the table structure
            return {"other": self.target}

        tags = self._store.get_plural_tags()

        # Sync plural_strings elements to plural_tags count.
        strings = self.sync_plural_count(self.target, tags)
        if any(strings):
            # Replace blank strings by None to distinguish not completed translations
            strings = [string or None for string in strings]

        # Return a dict with plural tags as keys
        return dict(zip(tags, strings, strict=True))


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
        self, data: dict[str, Any], prev: base.UnitId
    ) -> Generator[tuple[base.UnitId, str | multistring, str | None]]:
        """
        Parse a TOML table, checking for plural forms.

        Detects pluralized strings where all keys are CLDR plural categories.
        Special case: a table with only "other" key is treated as singular.
        """
        # Special case: table with only "other" key is treated as singular
        if data and len(data) == 1 and "other" in data:
            yield (prev, data["other"], None)
            return

        # Does this look like a plural?
        # Need at least 2 keys and all keys must be CLDR plural categories
        if data and len(data) >= 2 and all(x in cldr_plural_categories for x in data):
            # Extract plural forms in CLDR order
            values = [data[tag] for tag in cldr_plural_categories if tag in data]

            # Skip blank values (all plurals are None or empty)
            if values and not all(not value for value in values):
                # Use blank string instead of None for missing forms
                yield (prev, multistring(values), None)

            return

        # Handle normal dict
        yield from super()._parse_dict(data, prev)
