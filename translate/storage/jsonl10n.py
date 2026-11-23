#
# Copyright 2007,2009-2011 Zuza Software Foundation
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

r"""
Class that manages JSON data files for translation.

JSON is an acronym for JavaScript Object Notation, it is an open standard
designed for human-readable data interchange.

JSON basic types:

- Number (integer or real)
- String (double-quoted Unicode with backslash escaping)
- Boolean (true or false)
- Array (an ordered sequence of values, comma-separated and enclosed in square
  brackets)
- Object (a collection of key:value pairs, comma-separated and enclosed in
  curly braces)
- null

Example:
--------
.. code-block:: json

   {
        "firstName": "John",
        "lastName": "Smith",
        "age": 25,
        "address": {
            "streetAddress": "21 2nd Street",
            "city": "New York",
            "state": "NY",
            "postalCode": "10021"
        },
        "phoneNumber": [
            {
              "type": "home",
              "number": "212 555-1234"
            },
            {
              "type": "fax",
              "number": "646 555-4567"
            }
        ]
   }


Todo:
-----
- Handle ``\u`` and other escapes in Unicode
- Manage data type storage and conversion. True --> "True" --> True


"""

from __future__ import annotations

import json
import re
import uuid
from collections import defaultdict
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Generic,
    Never,
    NotRequired,
    Self,
    TextIO,
    TypedDict,
    TypeVar,
    cast,
)

from translate.lang.data import cldr_plural_categories
from translate.misc.multistring import multistring
from translate.storage import base

if TYPE_CHECKING:
    from collections.abc import Generator


class BaseJsonUnit(base.DictUnit):
    """A JSON entry."""

    ID_FORMAT = ".{}"

    def __init__(
        self, source=None, item=None, notes=None, placeholders=None, **kwargs
    ) -> None:
        identifier = hex(hash(source)) if source else str(uuid.uuid4())
        # Global identifier across file
        self._id = self.ID_FORMAT.format(identifier)
        # Identifier at this level
        self._item = identifier if item is None else item
        # Type conversion for the unit
        self._type = str if source is None else type(source)
        if notes:
            self.notes = notes
        self.placeholders = placeholders
        if source:
            if issubclass(self._type, str):
                self.target = source
            else:
                self.target = str(source)
        super().__init__(source)

    @property
    def source(self):
        return self.target

    @source.setter
    def source(self, source) -> None:
        self._invalidate_store_indexes()
        self.target = source

    def setid(self, value, unitid=None) -> None:
        self._invalidate_store_indexes()
        super().setid(value, unitid)
        unitid = self.get_unitid()
        self._item = unitid.parts[-1][1]

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def __str__(self) -> str:
        """Converts to a string representation."""
        return json.dumps(
            self.getvalue(), separators=(",", ": "), indent=4, ensure_ascii=False
        )

    def converttarget(self):
        if self.target is None:
            return None
        try:
            return self._type(self.target)
        except ValueError:
            return str(self.target)

    def storevalues(self, output) -> None:
        self.storevalue(output, self.converttarget())


class FlatUnitId(base.UnitId):
    @classmethod
    def from_string(cls, text):
        key = text.removeprefix(".")
        return cls([("key", key)])


class FlatJsonUnit(BaseJsonUnit):
    IdClass = FlatUnitId


class DumpArgsType(TypedDict):
    separators: tuple[str, str]
    indent: int
    ensure_ascii: bool
    sort_keys: NotRequired[bool]
    cls: NotRequired[type[json.JSONEncoder]]


JsonUnit = TypeVar("JsonUnit", bound=BaseJsonUnit)


def require_json_dict(data: Any, format_name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise base.ParseError(f"File is not a valid {format_name} JSON file!")
    return data


def require_json_list(data: Any, format_name: str) -> list[Any]:
    if not isinstance(data, list):
        raise base.ParseError(f"File is not a valid {format_name} JSON file!")
    return data


def require_json_string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise base.ParseError(f"{field} does not contain string: {value!r}")
    return value


class JsonFile(base.DictStore[JsonUnit], Generic[JsonUnit]):
    """A JSON file."""

    UnitClass: type[JsonUnit] = FlatJsonUnit  # ty:ignore[invalid-assignment]

    def __init__(self, inputfile=None, filter=None, **kwargs) -> None:
        """Construct a JSON file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self._filter = filter
        self.filename = ""
        self._file = ""
        self.dump_args: DumpArgsType = {
            "separators": (",", ": "),
            "indent": 4,
            "ensure_ascii": False,
        }
        if inputfile is not None:
            self.parse(inputfile)

    def serialize(self, out) -> None:
        units = self.get_root_node()
        self.serialize_units(units)
        out.write(json.dumps(units, **self.dump_args).encode(self.encoding))
        out.write(b"\n")

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        """
        Recursive function to extract items from the data files.

        :param data: the current branch to walk down
        :param stop: a list of leaves to extract or None to extract everything
        :param prev: the hierarchy of the tree at this iteration
        :param name_node:
        :param name_last_node: the name of the last node
        :param last_node: the last list or dict
        """
        if prev is None:
            prev = self.UnitClass.IdClass([])
        if isinstance(data, dict):
            for k, v in data.items():
                yield from self._extract_units(
                    v, stop, prev.extend("key", k), k, None, data
                )
        elif isinstance(data, list):
            for i, item in enumerate(data):
                yield from self._extract_units(
                    item, stop, prev.extend("index", i), i, name_node, data
                )
        # apply filter
        elif prev.parts and (
            stop is None
            or (isinstance(last_node, dict) and name_node in stop)
            or (isinstance(last_node, list) and name_last_node in stop)
        ):
            unit = self.UnitClass(data, name_node)
            unit.set_unitid(prev)
            yield unit

    def preprocess_input(self, text: str) -> str:
        return text

    def parse(self, data: str | bytes | TextIO | BinaryIO) -> None:
        """Parse the given file or file source string."""
        text: str | bytes
        if hasattr(data, "name"):
            self.filename = data.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(data, "read"):
            # Make type checking happy
            data = cast("BinaryIO", data)

            text = data.read()
            data.close()
        else:
            text = data

        if isinstance(text, bytes):
            # The JSON files should be UTF-8, but implementations
            # that parse JSON texts MAY ignore the presence of a byte order mark
            # rather than treating it as an error, see RFC7159
            decoded, self.encoding = self.detect_encoding(text)
            if decoded is None:
                raise base.ParseError(ValueError("Failed to decode JSON string."))
            text = decoded
        text = self.preprocess_input(text)
        try:
            self._file = json.loads(text)
        except ValueError as e:
            raise base.ParseError(e) from e

        for unit in self._extract_units(self._file, stop=self._filter):
            self.addunit(unit)


class JsonNestedUnit(BaseJsonUnit):
    """A nested JSON entry."""


class JsonNestedFile(JsonFile):
    """A JSON file with nested keys."""

    UnitClass = JsonNestedUnit


class WebExtensionJsonUnit(FlatJsonUnit):
    def storevalues(self, output) -> None:
        value = {"message": self.target}
        if self.notes:
            value["description"] = self.notes
        if self.placeholders:
            value["placeholders"] = self.placeholders
        self.storevalue(output, value)


class WebExtensionJsonFile(JsonFile):
    """
    WebExtension JSON file.

    See following URLs for doc:

    https://developer.chrome.com/extensions/i18n
    https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization
    """

    UnitClass = WebExtensionJsonUnit

    COMMENT_RE = re.compile(r'^((?:[^"\n]|"(?:[^"\\\n]|\\.)*")*?)//.*', re.MULTILINE)

    def preprocess_input(self, text: str) -> str:
        return self.COMMENT_RE.sub(r"\1", text)

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for item, value in require_json_dict(data, "WebExtension").items():
            if not isinstance(value, dict):
                raise base.ParseError("File is not a valid WebExtension JSON file!")
            message = value.get("message", "")
            description = value.get("description", "")
            placeholders = value.get("placeholders", None)
            message = require_json_string(message, f"Key {item!r}")
            description = require_json_string(description, f"Key {item!r} description")
            if placeholders is not None and not isinstance(placeholders, dict):
                raise base.ParseError(
                    f"Key {item!r} placeholders do not contain object: {placeholders!r}"
                )
            unit = self.UnitClass(
                message,
                item,
                description,
                placeholders,
            )
            unit.setid(item, unitid=self.UnitClass.IdClass.from_key(item))
            yield unit


class I18NextUnit(JsonNestedUnit):
    """
    A i18next v3 format, JSON with plurals.

    See https://www.i18next.com/
    """

    @staticmethod
    def _is_valid_suffix(suffix: str) -> bool:
        return suffix == "0"

    def _get_base_name(self):
        """Return base name for plurals."""
        item = self._item[0]
        if "_" in item:
            plural_base, _sep, suffix = item.rpartition("_")
            if self._is_valid_suffix(suffix):
                return plural_base
        return item

    def _get_plural_labels(self, count):
        base_name = self._get_base_name()
        if count == 2:
            return [base_name, f"{base_name}_plural"][:count]
        return [f"{base_name}_{i}" for i in range(count)]

    def _fixup_item(self) -> None:
        if isinstance(self._target, multistring):
            count = len(self._target.strings)
            is_list = isinstance(self._item, list)
            if not is_list or count != len(self._item):
                if not is_list:
                    self._item = [self._item]
                # Generate new plural labels
                self._item = self._get_plural_labels(count)
        elif isinstance(self._item, list):
            # Changing plural to singular
            self._item = self._get_base_name()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target) -> None:
        self._rich_target = None
        self._target = target

    def storevalues(self, output) -> None:
        if not isinstance(self.target, multistring):
            super().storevalues(output)
        else:
            plural_tags = self._store.get_plural_tags(self.target)  # ty:ignore[missing-union-attribute]
            if len(self.target.strings) > len(plural_tags):
                self.target.extra_strings = self.target.extra_strings[
                    : len(plural_tags) - 1
                ]
            self._fixup_item()
            for i, value in enumerate(self.target.strings):
                self.storevalue(output, value, override_key=self._item[i])


class I18NextFile(JsonNestedFile):
    """
    A i18next v3 format, this is nested JSON with several additions.

    See https://www.i18next.com/
    """

    UnitClass = I18NextUnit

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        if prev is None:
            prev = self.UnitClass.IdClass([])
        if isinstance(data, dict):
            plurals_multiple = [
                key.rsplit("_", 1)[0] for key in data if key.endswith("_0")
            ]
            plurals_simple = [
                key.rsplit("_", 1)[0] for key in data if key.endswith("_plural")
            ]
            processed = set()

            for k, v in data.items():
                # Check already processed items
                if k in processed:
                    continue
                plurals = []
                plural_base = ""
                if k in plurals_simple or f"{k}_plural" in plurals_simple:
                    plural_base = k.removesuffix("_plural")
                    plurals_simple.remove(plural_base)
                    plurals = [k, f"{k}_plural"]
                elif "_" in k:
                    plural_base, digit = k.rsplit("_", 1)
                    if plural_base in plurals_multiple and digit.isdigit():
                        plurals_multiple.remove(plural_base)
                        plurals = [f"{plural_base}_{order}" for order in range(10)]
                if plurals:
                    sources = []
                    items = []
                    for key in plurals:
                        if key not in data:
                            break
                        processed.add(key)
                        sources.append(data[key])
                        items.append(key)
                    unit = self.UnitClass(multistring(sources), items)
                    newid = prev.extend("key", plural_base)
                    unit.set_unitid(newid)
                    yield unit
                    continue

                yield from self._extract_units(
                    v, stop, prev.extend("key", k), k, None, data
                )
        else:
            yield from super()._extract_units(
                data, stop, prev, name_node, name_last_node, last_node
            )


class I18NextV4Unit(base.NamedPluralUnit, I18NextUnit):
    """
    A i18next v4 format, JSON with plurals.

    See https://www.i18next.com/
    """

    @classmethod
    def from_plural_forms(
        cls, forms: dict[str, str], tags: list[str], name: str
    ) -> Self:
        unit = cls(multistring([forms.get(tag, "") for tag in tags]), name)
        unit.set_plural_projection(forms, tags)
        return unit

    def istranslatable(self) -> bool:
        return self._has_target_text()

    def isblank(self) -> bool:
        return not self._has_target_text()

    def storevalues(self, output) -> None:
        forms = self._get_plural_forms()
        if forms is None:
            super().storevalues(output)
            return
        base_name = (
            self._get_base_name() if isinstance(self._item, list) else self._item
        )
        for tag, value in forms.items():
            self.storevalue(output, value, override_key=f"{base_name}_{tag}")

    @staticmethod
    def _is_valid_suffix(suffix: str) -> bool:
        return suffix in cldr_plural_categories

    def _get_plural_labels(self, count):
        base_name = self._get_base_name()
        plural_tags = self._store.get_plural_tags(self.target)  # ty:ignore[missing-union-attribute]
        return [f"{base_name}_{plural_tags[i]}" for i in range(count)]


class I18NextV4File(JsonNestedFile):
    """
    A i18next v4 format, this is nested JSON with several additions.

    See https://www.i18next.com/
    """

    UnitClass = I18NextV4Unit

    def addunit(self, unit) -> None:
        if isinstance(unit, I18NextV4Unit):
            unit.bind_plural_projection(self)
        super().addunit(unit)

    def serialize_units(self, output) -> None:
        super().serialize_units(output)
        self._restore_key_order(output, self._file)

    @classmethod
    def _restore_key_order(cls, output, original) -> None:
        """Keep interleaved plural groups and ordinary keys in document order."""
        if isinstance(output, dict) and isinstance(original, dict):
            existing = [key for key in original if key in output]
            if existing != [key for key in output if key in original]:
                ordered = {key: output[key] for key in existing}
                ordered.update(output)
                output.clear()
                output.update(ordered)
            for key in existing:
                cls._restore_key_order(output[key], original[key])
        elif isinstance(output, list) and isinstance(original, list):
            for value, previous in zip(output, original, strict=False):
                cls._restore_key_order(value, previous)

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
        plural_tags=None,
    ):
        if prev is None:
            prev = self.UnitClass.IdClass([])
        if plural_tags is None:
            plural_tags = self.get_plural_tags()
        if isinstance(data, dict):
            groups = defaultdict(dict)
            invalid_plural_bases = set()
            for key, value in data.items():
                if "_" not in key:
                    continue
                plural_base, suffix = key.rsplit("_", 1)
                if suffix not in cldr_plural_categories:
                    continue
                if isinstance(value, str):
                    groups[plural_base][suffix] = value
                else:
                    invalid_plural_bases.add(plural_base)
            valid_plural_bases = groups.keys() - invalid_plural_bases

            processed_plural_bases = set()

            for k, v in data.items():
                suffix = ""
                plural_base = ""

                if "_" in k:
                    plural_base, suffix = k.rsplit("_", 1)

                if (
                    suffix in cldr_plural_categories
                    and plural_base in valid_plural_bases
                ):
                    if plural_base in processed_plural_bases:
                        continue
                    processed_plural_bases.add(plural_base)
                    unit = self.UnitClass.from_plural_forms(
                        groups[plural_base], plural_tags, plural_base
                    )
                    unit.set_unitid(prev.extend("key", plural_base))
                    yield unit
                    continue

                yield from self._extract_units(
                    v,
                    stop,
                    prev.extend("key", k),
                    k,
                    None,
                    data,
                    plural_tags,
                )
        else:
            yield from super()._extract_units(
                data, stop, prev, name_node, name_last_node, last_node
            )


class FlatI18NextV4Unit(I18NextV4Unit):
    IdClass = FlatUnitId


class FlatI18NextV4File(I18NextV4File):
    """
    Flat json file with support of i18next v4 format plurals.

    See https://www.i18next.com/
    """

    UnitClass = FlatI18NextV4Unit


class GoTextUnitId(base.UnitId):
    """Preserves id as stored in the JSON file."""

    def __str__(self) -> str:
        return str(self.parts)

    def extend(self, key, value) -> Never:
        raise ValueError("Extend is not supported")

    @classmethod
    def from_string(cls, text):
        return cls(text)


class GoTextJsonUnit(base.NamedPluralUnit, BaseJsonUnit):
    ID_FORMAT = "{}"
    IdClass = GoTextUnitId
    _translation_template: dict | None = None

    def __init__(
        self,
        source=None,
        item=None,
        notes=None,
        placeholders=None,
        comment=None,
        message=None,
        meaning=None,
        key=None,
        fuzzy=None,
        position=None,
        **kwargs,
    ) -> None:
        super().__init__(source, item, notes, placeholders)
        self.comment = comment
        self.message = message
        self.meaning = meaning
        self.key = key
        self.fuzzy = fuzzy
        self.position = position

    rich_source = base.TranslationUnit.rich_target

    def merge(
        self, otherunit, overwrite=False, comments=True, authoritative=False
    ) -> None:
        if not isinstance(otherunit, GoTextJsonUnit):
            super().merge(otherunit, overwrite, comments, authoritative)
            return
        if not overwrite and self._has_target_text():
            return
        # The selector argument, exact cases and case metadata are part of the
        # translation. Keep the receiving message's ID and outer metadata.
        donor = otherunit.copy()
        if self._store is not None:
            donor.bind_plural_projection(self._store)
        self._target = donor.target
        self._forms = donor._forms
        self._projection = donor._projection
        self._projection_language = self._receiver_projection_language(
            self._projection_language
        )
        self._translation_template = donor._translation_template
        self._rich_source = self._rich_target = None
        self._invalidate_store_indexes()

    def bind_plural_projection(self, store) -> None:
        if (
            self._translation_template is None
            or self._translation_template.get("select", {}).get("feature") == "plural"
            or self._projection
        ):
            super().bind_plural_projection(store)

    @base.NamedPluralUnit.target.setter
    def target(self, target) -> None:
        # Exact-only selectors have no positional categories. Writing their
        # empty positional view back must preserve the retained cases.
        if (
            self._translation_template is not None
            and not self._projection
            and isinstance(target, multistring)
            and target == self._target
        ):
            return
        base.NamedPluralUnit.target.fset(self, target)

    def _get_plural_forms(self) -> dict[str, str] | None:
        if (
            self._translation_template is not None
            and self._translation_template.get("select", {}).get("feature") != "plural"
        ):
            return None
        return super()._get_plural_forms()

    def _replace_plural_forms(self, forms: dict[str, str]) -> None:
        if not forms and self._get_plural_forms() == {}:
            return
        super()._replace_plural_forms(forms)

    def __eq__(self, other):
        return super().__eq__(other) and (
            not isinstance(other, GoTextJsonUnit)
            or self._translation() == other._translation()
        )

    __hash__ = base.TranslationUnit.__hash__

    def _has_target_text(self) -> bool:
        if super()._has_target_text():
            return True
        translation = self._translation()
        if not isinstance(translation, dict):
            return False
        return any(
            case.get("msg") if isinstance(case, dict) else case
            for case in translation.get("select", {}).get("cases", {}).values()
        )

    def _translation(self):
        target = self.target
        forms = self._get_plural_forms()
        if forms is not None:
            template = self._translation_template or {}
            selector = dict(template.get("select", {"feature": "plural"}))
            if not template and self.placeholders:
                selector["arg"] = self.placeholders[0]["id"]
            cases = dict(selector.get("cases", {}))
            for key in (cases.keys() & set(cldr_plural_categories)) - forms.keys():
                del cases[key]
            for key, text in forms.items():
                case = cases.get(key, {})
                cases[key] = {**case, "msg": text} if isinstance(case, dict) else text
            target = {**template, "select": {**selector, "cases": cases}}
        elif isinstance(target, multistring) and self._translation_template is not None:
            target = self._translation_template
        return target

    def getvalue(self):
        value = {"id": self._unitid.parts if self._unitid else self.getid()}
        if self.message:
            value["message"] = self.message
        if self.notes:
            value["translatorComment"] = self.notes
        if self.comment:
            value["comment"] = self.comment
        if self.key:
            value["key"] = self.key
        if self.fuzzy:
            value["fuzzy"] = self.fuzzy
        if self.position:
            value["position"] = self.position
        value["translation"] = self._translation()
        if self.placeholders:
            value["placeholders"] = self.placeholders
        return value

    def setid(self, value, unitid=None) -> None:
        self._invalidate_store_indexes()
        if unitid is None:
            unitid = self.IdClass(value)
        # Skip BaseJsonUnit.setid override
        super(BaseJsonUnit, self).setid(str(unitid), unitid)


class GoTextJsonFile(JsonFile):
    """
    gotext JSON file.

    See following URLs for doc:

    https://pkg.go.dev/golang.org/x/text/cmd/gotext
    https://github.com/golang/text/tree/master/cmd/gotext/examples/extract/locales/en-US
    """

    UnitClass = GoTextJsonUnit

    def addunit(self, unit) -> None:
        if isinstance(unit, GoTextJsonUnit):
            unit.bind_plural_projection(self)
        super().addunit(unit)

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        def _get_msg(cases, key):
            value = cases.get(key, None)
            if isinstance(value, dict):
                value = value.get("msg")
            # Direct string value and None as fallback
            return require_json_string(value, f"gotext plural case {key!r}")

        if prev is None:
            data = require_json_dict(data, "gotext")
            lang = data.get("language")
            if lang is not None:
                self.settargetlanguage(require_json_string(lang, "language"))
        messages = data.get("messages", [])
        if not isinstance(messages, list):
            raise base.ParseError("gotext messages do not contain array")
        for value in messages:
            if not isinstance(value, dict):
                raise base.ParseError(
                    f"gotext message does not contain object: {value!r}"
                )
            translation = value.get("translation", "")
            if isinstance(translation, dict):
                select = translation.get("select", {})
                if not isinstance(select, dict):
                    raise base.ParseError(
                        f"gotext translation select does not contain object: {select!r}"
                    )
                cases = select.get("cases", {})
                if not isinstance(cases, dict):
                    raise base.ParseError(
                        f"gotext translation cases do not contain object: {cases!r}"
                    )
                forms = {
                    key: _get_msg(cases, key)
                    for key in cases
                    if key in cldr_plural_categories
                }
                tags = [key for key in cldr_plural_categories if key in forms]
                translation = multistring([forms[key] for key in tags] or [""])
            elif translation is not None and not isinstance(translation, (str, int)):
                raise base.ParseError(
                    f"gotext translation does not contain string: {translation!r}"
                )
            unit = self.UnitClass(
                source=translation,
                item=value.get("id", ""),
                notes=value.get("translatorComment", ""),
                placeholders=value.get("placeholders", []),
                comment=value.get("comment", None),
                message=value.get("message", None),
                meaning=value.get("meaning", None),
                key=value.get("key", None),
                fuzzy=value.get("fuzzy", None),
                position=value.get("position", None),
            )
            if isinstance(translation, multistring):
                unit._translation_template = value["translation"]
                if tags or select.get("feature") == "plural":
                    # Keep a default positional slot for exact-only selectors.
                    # An empty explicit mapping emits no category cases.
                    unit.set_plural_projection(forms, tags or ("other",))
            unit.setid(value.get("id", ""))
            yield unit

    def serialize(self, out) -> None:
        units = [unit.getvalue() for unit in self.units]
        file = {
            "language": self.gettargetlanguage(),
            "messages": units,
        }
        out.write(json.dumps(file, **self.dump_args).encode(self.encoding))
        out.write(b"\n")


class _GoI18NJsonUnit(base.NamedPluralUnit, FlatJsonUnit):
    """Shared support for promoting scalar Go-i18n messages to named forms."""

    # Source and target refer to the same translation in this monolingual format.
    rich_source = base.TranslationUnit.rich_target

    ID_FORMAT = "{}"
    _plural_fields: dict | None = None

    def merge(
        self, otherunit, overwrite=False, comments=True, authoritative=False
    ) -> None:
        forms = otherunit._plural_forms_for_merge()
        if (
            forms
            and self.plural_forms is None
            and (overwrite or not self._has_target_text())
        ):
            tags = tuple(tag for tag in cldr_plural_categories if tag in forms)
            if tags:
                self.set_plural_projection({tag: forms[tag] for tag in tags}, tags)
                self._projection_language = self._receiver_projection_language(
                    self._projection_language
                )
                return
        super().merge(otherunit, overwrite, comments, authoritative)


class GoI18NJsonUnit(_GoI18NJsonUnit):
    def getvalue(self):
        forms = self._get_plural_forms()
        target = (
            self.target if forms is None else {**(self._plural_fields or {}), **forms}
        )
        value = {"id": self.getid()}
        if self.notes:
            value["description"] = self.notes
        value["translation"] = target
        return value


class GoI18NJsonFile(JsonFile):
    """
    go-i18n JSON file.

    See following URLs for doc:

    https://github.com/nicksnyder/go-i18n/tree/v1
    https://pkg.go.dev/github.com/nicksnyder/go-i18n
    """

    UnitClass = GoI18NJsonUnit

    def addunit(self, unit) -> None:
        if isinstance(unit, GoI18NJsonUnit):
            unit.bind_plural_projection(self)
        super().addunit(unit)

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for value in require_json_list(data, "go-i18n"):
            if not isinstance(value, dict):
                raise base.ParseError(
                    f"go-i18n entry does not contain object: {value!r}"
                )
            item = value.get("id", "")
            translation = value.get("translation", "")
            if isinstance(translation, dict):
                # Ordered list of plurals
                forms = {
                    key: require_json_string(text, f"Plural form {key!r}")
                    for key, text in translation.items()
                    if key in cldr_plural_categories
                }
                if not forms:
                    raise base.ParseError("Translation object does not contain plurals")
                tags = [key for key in cldr_plural_categories if key in forms]
                translation = multistring([forms[key] for key in tags])
            elif translation is not None and not isinstance(translation, (str, int)):
                raise base.ParseError(
                    f"go-i18n translation does not contain string: {translation!r}"
                )
            description = value.get("description", "")
            description = require_json_string(description, "description")
            unit = self.UnitClass(
                translation,
                item,
                description,
            )
            if isinstance(translation, multistring):
                unit._plural_fields = {
                    key: text
                    for key, text in value["translation"].items()
                    if key not in cldr_plural_categories
                }
                unit.set_plural_projection(forms, tags)
            unit.setid(item, unitid=self.UnitClass.IdClass.from_key(item))
            yield unit

    def serialize(self, out) -> None:
        units = [unit.getvalue() for unit in self.units]
        out.write(json.dumps(units, **self.dump_args).encode(self.encoding))
        out.write(b"\n")


class GoI18NV2JsonUnit(_GoI18NJsonUnit):
    def merge(
        self, otherunit, overwrite=False, comments=True, authoritative=False
    ) -> None:
        if isinstance(otherunit, GoI18NV2JsonUnit):
            if not overwrite and self._has_target_text():
                return
            forms = otherunit._get_plural_forms()
            if forms is not None:
                self.set_plural_projection(forms, otherunit._projection)
                self._projection_language = self._receiver_projection_language(
                    self._projection_language
                )
                return
        if (
            isinstance(self.target, multistring)
            and self.plural_forms is None
            and isinstance(otherunit.target, str)
            and not isinstance(otherunit.target, multistring)
            and (overwrite or not self._has_target_text())
        ):
            self._merge_scalar_target("other", otherunit.target)
            return
        super().merge(otherunit, overwrite, comments, authoritative)

    def _merge_scalar_target(self, tag: str, text: str) -> None:
        # A scalar replaces the v2 message's translation, retaining its metadata.
        self.set_plural_projection({tag: text}, (tag,))
        self._projection_language = self._receiver_projection_language(
            self._projection_language
        )

    def converttarget(self):
        forms = self._get_plural_forms()
        if forms is None:
            if self.notes:
                return {"description": self.notes, "other": self.target}
            return self.target
        fields = dict(self._plural_fields or {})
        if self.notes:
            fields["description"] = self.notes
        return {**fields, **forms}


class GoI18NV2JsonFile(JsonFile):
    """
    go-i18n v2 JSON file.

    See following URLs for doc:

    https://github.com/nicksnyder/go-i18n
    https://pkg.go.dev/github.com/nicksnyder/go-i18n/v2
    """

    UnitClass = GoI18NV2JsonUnit

    def addunit(self, unit) -> None:
        if isinstance(unit, GoI18NV2JsonUnit):
            unit.bind_plural_projection(self)
        super().addunit(unit)

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for id, value in require_json_dict(data, "go-i18n v2").items():
            if isinstance(value, str):
                unit = self.UnitClass(value, id)
            else:
                if not isinstance(value, dict):
                    raise base.ParseError(
                        f"Key {id!r} does not contain string or object: {value!r}"
                    )
                forms = {
                    key: require_json_string(text, f"Plural form {key!r}")
                    for key, text in value.items()
                    if key in cldr_plural_categories
                }
                if not forms:
                    raise base.ParseError("Translation object does not contain plurals")
                tags = [key for key in cldr_plural_categories if key in forms]
                translation = multistring([forms[key] for key in tags])
                description = value.get("description", "")
                description = require_json_string(
                    description, f"Key {id!r} description"
                )
                unit = self.UnitClass(
                    translation,
                    id,
                    description,
                )
                unit._plural_fields = {
                    key: text
                    for key, text in value.items()
                    if key not in cldr_plural_categories and key != "description"
                }
                unit.set_plural_projection(forms, tags)
            unit.setid(id, unitid=self.UnitClass.IdClass.from_key(id))
            yield unit


class ARBJsonUnit(base.MetadataTranslationUnit, FlatJsonUnit):
    ID_FORMAT = "{}"

    def __init__(
        self,
        source=None,
        item=None,
        notes=None,
        placeholders=None,
        metadata=None,
        **kwargs,
    ) -> None:
        # Pass metadata to MetadataTranslationUnit via super().__init__
        super().__init__(
            source=source,
            item=item,
            notes=notes,
            placeholders=placeholders,
            metadata=metadata,
            **kwargs,
        )

    def storevalues(self, output) -> None:
        if self.notes:
            self.metadata["description"] = self.notes
        identifier = self.getid()
        if identifier == "@":
            for key, value in self.metadata.items():
                self.storevalue(output, value, override_key=key)
        else:
            self.storevalue(output, self.target, override_key=identifier)
            if self.metadata:
                self.storevalue(output, self.metadata, override_key=f"@{identifier}")

    def isheader(self):
        return self._id == "@"


class ARBJsonFile(JsonFile):
    """
    ARB JSON file.

    See following URLs for doc:

    https://github.com/google/app-resource-bundle/wiki/ApplicationResourceBundleSpecification
    https://docs.flutter.dev/development/accessibility-and-localization/internationalization#dart-tools
    """

    UnitClass = ARBJsonUnit

    def __init__(self, inputfile=None, filter=None, **kwargs) -> None:
        super().__init__(inputfile, filter, **kwargs)
        self.dump_args = {
            "separators": (",", ": "),
            "indent": 2,
            "ensure_ascii": False,
        }

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        data = require_json_dict(data, "ARB")
        # Extract metadata as header
        metadata = {key: value for key, value in data.items() if key.startswith("@@")}
        if metadata:
            unit = self.UnitClass(metadata=metadata)
            unit.setid("@")
            yield unit

        for item, value in data.items():
            if item.startswith("@"):
                continue
            if not isinstance(value, (str, int)):
                raise base.ParseError(
                    f"Key {item!r} does not contain string: {value!r}"
                )
            metadata = data.get(f"@{item}", {})
            if not isinstance(metadata, dict):
                raise base.ParseError(
                    f"Key '@{item}' does not contain object: {metadata!r}"
                )
            description = metadata.get("description", "")
            description = require_json_string(description, f"Key '@{item}' description")
            placeholders = metadata.get("placeholders", None)
            if placeholders is not None and not isinstance(placeholders, dict):
                raise base.ParseError(
                    f"Key '@{item}' placeholders do not contain object: "
                    f"{placeholders!r}"
                )
            unit = self.UnitClass(
                value,
                item,
                description,
                placeholders,
                metadata=metadata,
            )
            unit.setid(item, unitid=self.UnitClass.IdClass.from_key(item))
            yield unit


class FormatJSJsonUnit(FlatJsonUnit):
    def storevalues(self, output) -> None:
        value = {"defaultMessage": self.target}
        if self.notes:
            value["description"] = self.notes
        self.storevalue(output, value)


class FormatJSJsonFile(JsonFile):
    """
    FormatJS JSON file.

    See following URLs for doc:

    https://formatjs.github.io/docs/getting-started/message-extraction/
    """

    UnitClass = FormatJSJsonUnit

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for item, value in require_json_dict(data, "FormatJS").items():
            if not isinstance(value, dict):
                raise base.ParseError(
                    f"Not a valid FormatJS file should be a object: {value!r}"
                )
            default_message = value.get("defaultMessage", "")
            default_message = require_json_string(
                default_message, f"Key {item!r} defaultMessage"
            )
            description = value.get("description", "")
            if not isinstance(description, (str, dict)):
                raise base.ParseError(
                    f"Key {item!r} description does not contain string or object: "
                    f"{description!r}"
                )
            unit = self.UnitClass(
                default_message,
                item,
                description,
            )
            unit.setid(item, unitid=self.UnitClass.IdClass.from_key(item))
            yield unit


class NextcloudJsonUnit(FlatJsonUnit):
    """A Nextcloud JSON entry."""

    ID_FORMAT = "{}"

    def converttarget(self) -> Any:
        """Convert target to appropriate format for Nextcloud JSON."""
        if isinstance(self.target, multistring):
            # Return as array for plurals
            return list(self.target.strings)
        return self.target

    @property
    def source(self):
        return self.getid()

    @source.setter
    def source(self, source) -> None:
        self._invalidate_store_indexes()
        self.setid(source)


class NextcloudJsonFile(JsonFile[NextcloudJsonUnit]):
    """
    Nextcloud JSON file.

    Nextcloud apps use a JSON format with translations wrapped in a
    "translations" key. Plurals follow gettext conventions with keys like
    ``_%n singular_::_%n plural_`` and array values.

    See:
    https://docs.nextcloud.com/server/stable/developer_manual/basics/translations.html
    https://github.com/nextcloud-libraries/nextcloud-l10n/
    """

    UnitClass = NextcloudJsonUnit

    def __init__(
        self,
        inputfile: str | bytes | TextIO | BinaryIO | None = None,
        filter: Any = None,
        **kwargs,
    ) -> None:
        """Construct a Nextcloud JSON file."""
        super().__init__(inputfile, filter, **kwargs)
        # Store top-level elements outside 'translations' for preservation
        self._metadata: dict[str, Any] = {}

    def _extract_units(
        self,
        data: Any,
        stop: list[str] | None = None,
        prev: Any = None,
        name_node: str | int | None = None,
        name_last_node: str | int | None = None,
        last_node: dict | list | None = None,
    ) -> Generator[NextcloudJsonUnit]:
        """Extract units from the translations key only."""
        data = require_json_dict(data, "Nextcloud")
        # Store metadata (everything outside 'translations')
        for key, value in data.items():
            if key != "translations":
                self._metadata[key] = value

        # Only parse the translations key
        translations = data.get("translations", {})
        if not isinstance(translations, dict):
            raise base.ParseError(
                f"Nextcloud translations do not contain object: {translations!r}"
            )

        for key, value in translations.items():
            # Check if this is a plural form (gettext style)
            if isinstance(value, list):
                for item in value:
                    require_json_string(item, f"Key {key!r} plural translation")
                # Plural form - array of translations
                unit = self.UnitClass(multistring(value), key)
            elif value is None:
                unit = self.UnitClass(value, key)
            else:
                value = require_json_string(value, f"Key {key!r}")
                # Simple string translation
                unit = self.UnitClass(value, key)

            unit.setid(key, unitid=self.UnitClass.IdClass.from_key(key))
            yield unit

    def serialize(self, out: IO[bytes]) -> None:
        """Serialize to Nextcloud JSON format."""
        # Build translations dictionary
        translations = {}
        for unit in self.units:
            if not unit.istranslated():
                continue
            key = unit.getid()
            value = unit.converttarget()
            translations[key] = value

        # Combine metadata and translations
        output = dict(self._metadata)
        output["translations"] = translations

        out.write(json.dumps(output, **self.dump_args).encode(self.encoding))
        out.write(b"\n")


class RESJSONUnit(base.MetadataTranslationUnit, FlatJsonUnit):
    """A RESJSON entry with metadata support."""

    ID_FORMAT = "{}"

    def __init__(
        self,
        source=None,
        item=None,
        notes=None,
        placeholders=None,
        metadata=None,
        **kwargs,
    ) -> None:
        # Pass metadata to MetadataTranslationUnit via super().__init__
        super().__init__(
            source=source,
            item=item,
            notes=notes,
            placeholders=placeholders,
            metadata=metadata,
            **kwargs,
        )

    def storevalues(self, output) -> None:
        # Sync notes to metadata
        if self.notes:
            self.metadata["comment"] = self.notes
        elif "comment" in self.metadata and not self.notes:
            # Remove comment if notes were cleared
            del self.metadata["comment"]
        if self._source:
            self.metadata["source"] = self._source

        identifier = self.getid()
        # Store the main value
        self.storevalue(output, self.target, override_key=identifier)
        # Store metadata with _KEY.suffix pattern
        for key, value in self.metadata.items():
            metadata_key = f"_{identifier}.{key}"
            self.storevalue(output, value, override_key=metadata_key)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source) -> None:
        self._invalidate_store_indexes()
        self._source = source

    def getcontext(self):
        return self.getid()


class RESJSONFile(JsonFile):
    """
    RESJSON (JavaScript Resource File) format.

    This format uses `_KEY.DATA` syntax to attach metadata to translation strings.

    See following URL for doc:

    https://docs.rws.com/en-US/sdl-passolo-help-785448/add-in-for-javascript-object-notation-json-file-format-types-410873
    """

    UnitClass = RESJSONUnit

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        data = require_json_dict(data, "RESJSON")
        # First pass: identify all actual keys (not metadata)
        key_map = {
            key: key.removeprefix("_").rsplit(".", 1)[0]
            if key.startswith("_") and "." in key[1:]
            else key
            for key in data
        }
        # Second pass: collect metadata for each actual key, preserving order
        metadata = defaultdict(dict)
        translations = defaultdict(str)
        for key, value in data.items():
            if not isinstance(value, (str, int)):
                raise base.ParseError(f"Key {key!r} does not contain string: {value!r}")
            actual_key = key_map[key]
            if actual_key == key:
                # Data
                translations[key] = value
            else:
                suffix = key.rsplit(".", 1)[1]
                metadata[actual_key][suffix] = value

        # Extract units
        processed = set()
        for key in key_map.values():
            if key in processed:
                continue
            processed.add(key)
            unit = self.UnitClass(
                metadata[key].get("source", ""),
                key,
                metadata[key].get("comment", ""),
                metadata[key].get("placeholders", None),
                metadata=metadata[key],
            )
            unit.target = translations[key]
            unit.setid(key, unitid=self.UnitClass.IdClass.from_key(key))
            yield unit
