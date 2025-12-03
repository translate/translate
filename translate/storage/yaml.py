#
# Copyright 2016 Michal Čihař
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

r"""Class that manages YAML data files for translation."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.comments import CommentedMap, TaggedScalar
from ruamel.yaml.scalarstring import LiteralScalarString

from translate.lang.data import cldr_plural_categories
from translate.misc.multistring import multistring
from translate.storage import base

if TYPE_CHECKING:
    from collections.abc import Generator


class YAMLUnitId(base.UnitId):
    KEY_SEPARATOR = "->"
    INDEX_SEPARATOR = "->"

    def __str__(self):
        result = super().__str__()
        # Strip leading ->
        if result.startswith(self.KEY_SEPARATOR):
            return result[len(self.KEY_SEPARATOR) :]
        return result


class YAMLUnit(base.DictUnit):
    """A YAML entry."""

    IdClass = YAMLUnitId

    def __init__(self, source=None, **kwargs):
        # Ensure we have ID (for serialization)
        if source:
            self.source = source
            self._id = hex(hash(source))
        else:
            self._id = str(uuid.uuid4())
        super().__init__(source)

    @property
    def source(self):
        return self.target

    @source.setter
    def source(self, source):
        self.target = source

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def convert_target(self):
        return self.target

    def _get_original_value(self, output: dict[str, Any] | list[Any]) -> Any:
        """
        Get the original value from the YAML output structure to check its type.

        Args:
            output: The YAML output structure (dict or list) to navigate

        Returns:
            The original value if it exists, None if navigation fails or value doesn't exist

        """
        target = output
        parts = self.get_unitid().parts

        # Navigate to get the original value
        try:
            for part in parts:
                element, key = part
                if element in {"index", "key"}:
                    target = target[key]
        except (KeyError, IndexError, TypeError):
            return None
        return target

    def storevalue(
        self,
        output: dict[str, Any] | list[Any],
        value: Any,
        override_key: str | None = None,
        unset: bool = False,
    ) -> None:
        """Store value, preserving or converting to LiteralScalarString for multiline strings."""
        # Get the original value to check its type before it gets overwritten
        original_value = self._get_original_value(output)

        # Preserve or convert to LiteralScalarString for better readability
        # Always preserve LiteralScalarString if original was one, or
        # for new values or plain strings, use LiteralScalarString if multiline
        if (
            isinstance(value, str)
            and not unset
            and (
                isinstance(original_value, LiteralScalarString)
                or (
                    "\n" in value
                    and (original_value is None or type(original_value) is str)
                )
            )
        ):
            value = LiteralScalarString(value)
        # Otherwise keep the value as-is (e.g., DoubleQuotedScalarString stays quoted)

        # Call parent storevalue
        super().storevalue(output, value, override_key, unset)

    def storevalues(self, output: dict[str, Any] | list[Any]) -> None:
        self.storevalue(output, self.convert_target())


class YAMLFile(base.DictStore):
    """A YAML file."""

    UnitClass = YAMLUnit

    def __init__(self, inputfile=None, **kwargs):
        """Construct a YAML file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ""
        self._original = self.get_root_node()
        self.dump_args = {
            "default_flow_style": False,
            "preserve_quotes": True,
        }
        if inputfile is not None:
            self.parse(inputfile)

    def get_root_node(self):
        """Returns root node for serialize."""
        return CommentedMap()

    @property
    def yaml(self):
        yaml = YAML()
        for arg, value in self.dump_args.items():
            setattr(yaml, arg, value)
        return yaml

    def serialize(self, out):
        # Always start with valid root even if original file was empty
        if self._original is None:
            self._original = self.get_root_node()

        units = self.preprocess(self._original)
        self.serialize_units(units)
        self.yaml.dump(self._original, out)

    def _extract_comment_lines(self, tokens):
        """Extract comment text from YAML comment tokens."""
        comment_lines = []
        # Ensure tokens is a list
        if not isinstance(tokens, list):
            tokens = [tokens]

        for token in tokens:
            if hasattr(token, "value"):
                for line in token.value.split("\n"):
                    line = line.strip()
                    if line.startswith("#"):
                        comment_lines.append(line[1:].strip())
        return comment_lines

    def _get_key_comment(self, commented_map, key):
        """
        Extract the comment that appears before a key in a CommentedMap.

        Comments can appear in three places:
        1. Top-level comment for the first key (ca.comment[1])
        2. After the previous key's value (ca.items[prev_key][2])
        3. On separate lines before the key (ca.items[key][3])
        """
        if not isinstance(commented_map, CommentedMap) or not hasattr(
            commented_map, "ca"
        ):
            return None

        comment_lines = []
        keys = list(commented_map.keys())

        # Check for top-level comment if this is the first key
        if keys and keys[0] == key:
            ca_comment = getattr(commented_map.ca, "comment", None)
            if ca_comment and len(ca_comment) > 1 and ca_comment[1]:
                comment_lines.extend(self._extract_comment_lines(ca_comment[1]))

        # For non-first keys, check the previous key's end comment
        elif key in keys:
            key_index = keys.index(key)
            if key_index > 0 and hasattr(commented_map.ca, "items"):
                prev_key = keys[key_index - 1]
                prev_comment_info = commented_map.ca.items.get(prev_key)
                if (
                    prev_comment_info
                    and len(prev_comment_info) > 2
                    and prev_comment_info[2]
                ):
                    comment_lines.extend(
                        self._extract_comment_lines(prev_comment_info[2])
                    )

        # Check for comments on separate lines before this key
        if hasattr(commented_map.ca, "items"):
            comment_info = commented_map.ca.items.get(key)
            if comment_info and len(comment_info) > 3 and comment_info[3]:
                comment_lines.extend(self._extract_comment_lines(comment_info[3]))

        return "\n".join(comment_lines) if comment_lines else None

    def _parse_dict(self, data, prev):
        # Avoid using merged items, it is enough to have them once
        for k, v in data.non_merged_items():
            yield from self._flatten(v, prev.extend("key", k), parent_map=data, key=k)

    def _flatten(
        self, data, prev=None, parent_map=None, key=None
    ) -> Generator[tuple[base.UnitId, str, str | None]]:
        """
        Flatten YAML dictionary.

        Yields tuples of (unit_id, data, comment) where comment may be None.
        """
        if prev is None:
            prev = self.UnitClass.IdClass([])
        if isinstance(data, dict):
            yield from self._parse_dict(data, prev)
        elif isinstance(data, str):
            yield (prev, data, self._get_key_comment(parent_map, key))
        elif isinstance(data, (bool, int)):
            yield (prev, str(data), self._get_key_comment(parent_map, key))
        elif isinstance(data, list):
            for k, v in enumerate(data):
                yield from self._flatten(
                    v, prev.extend("index", k), parent_map=data, key=k
                )
        elif isinstance(data, TaggedScalar):
            yield (prev, data.value, self._get_key_comment(parent_map, key))
        elif data is None:
            pass
        else:
            raise ValueError(
                "We don't handle these values:\n"
                f"Type: {type(data)}\n"
                f"Data: {data}\n"
                f"Previous: {prev}"
            )

    @staticmethod
    def preprocess(data):
        """Preprocess hook for child formats."""
        return data

    def parse(self, input):
        """Parse the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            src = input.read()
            input.close()
            input = src
        if isinstance(input, bytes):
            input = input.decode("utf-8")
        try:
            self._original = self.yaml.load(input)
        except YAMLError as e:
            message = getattr(e, "problem", getattr(e, "message", str(e)))
            if hasattr(e, "problem_mark"):
                message += f" {e.problem_mark}"
            raise base.ParseError(message) from e

        content = self.preprocess(self._original)

        for k, data, comment in self._flatten(content):
            unit = self.UnitClass(data)
            unit.set_unitid(k)
            if comment:
                unit.addnote(comment, origin="developer")
            self.addunit(unit)

    def removeunit(self, unit):
        if self._original is not None:
            units = self.preprocess(self._original)
            unit.storevalue(units, None, unset=True)
        super().removeunit(unit)


class RubyYAMLUnit(YAMLUnit):
    def convert_target(self):
        if not isinstance(self.target, multistring):
            return self.target

        tags = self._store.get_plural_tags()

        # Sync plural_strings elements to plural_tags count.
        strings = self.sync_plural_count(self.target, tags)
        if any(strings):
            # Replace blank strings by None to distinguish not completed translations
            strings = [string or None for string in strings]

        return CommentedMap(zip(tags, strings, strict=True))


class RubyYAMLFile(YAMLFile):
    """Ruby YAML file, it has language code as first node."""

    UnitClass = RubyYAMLUnit

    def preprocess(self, data):
        if isinstance(data, CommentedMap) and len(data) == 1:
            lang = next(iter(data.keys()))
            # Handle blank values
            if data[lang] is None:
                data[lang] = CommentedMap()
            # Do not try to parse string only, CommentedMap is dict as well
            if isinstance(data[lang], dict):
                self.settargetlanguage(lang)
                return data[lang]
        return data

    def get_root_node(self):
        """Returns root node for serialize."""
        result = CommentedMap()
        result[self.targetlanguage or "en"] = CommentedMap()
        return result

    def _parse_dict(self, data, prev):
        # Does this look like a plural?
        tags = self.get_plural_tags()
        if data and all(x in cldr_plural_categories for x in data):
            # Ensure we have correct plurals ordering.
            values = [data[item] for item in tags if item in data]

            # Skip blank values (all plurals are None)
            if not all(value is None for value in values):
                # Use blank string instead of None here
                # Note: plurals don't have comments, so we pass None
                yield (prev, multistring([value or "" for value in values]), None)

            return

        # Handle normal dict
        yield from super()._parse_dict(data, prev)
