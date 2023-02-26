#
# Copyright 2007,2009-2011 Zuza Software Foundation
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

r"""Class that manages JSON data files for translation

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


TODO:

- Handle ``\u`` and other escapes in Unicode
- Manage data type storage and conversion. True --> "True" --> True

"""

import json
import uuid

from translate.lang.data import cldr_plural_categories, plural_tags
from translate.misc.multistring import multistring
from translate.storage import base


class BaseJsonUnit(base.DictUnit):
    """A JSON entry"""

    ID_FORMAT = ".{}"

    def __init__(self, source=None, item=None, notes=None, placeholders=None, **kwargs):
        if source:
            identifier = hex(hash(source))
        else:
            identifier = str(uuid.uuid4())
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
    def source(self, source):
        self.target = source

    def setid(self, value, unitid=None):
        super().setid(value, unitid)
        self.get_unitid()
        self._item = self._unitid.parts[-1][1]

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def __str__(self):
        """Converts to a string representation."""
        return json.dumps(
            self.getvalue(), separators=(",", ": "), indent=4, ensure_ascii=False
        )

    def converttarget(self):
        try:
            return self._type(self.target)
        except ValueError:
            return str(self.target)

    def storevalues(self, output):
        self.storevalue(output, self.converttarget())


class FlatUnitId(base.UnitId):
    @classmethod
    def from_string(cls, text):
        if text.startswith("."):
            key = text[1:]
        else:
            key = text
        return cls([("key", key)])


class FlatJsonUnit(BaseJsonUnit):
    IdClass = FlatUnitId


class JsonFile(base.DictStore):
    """A JSON file"""

    UnitClass = FlatJsonUnit

    def __init__(self, inputfile=None, filter=None, **kwargs):
        """construct a JSON file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self._filter = filter
        self.filename = ""
        self._file = ""
        self.dump_args = {
            "separators": (",", ": "),
            "indent": 4,
            "ensure_ascii": False,
        }
        if inputfile is not None:
            self.parse(inputfile)

    @property
    def plural_tags(self):
        locale = self.gettargetlanguage()
        if locale:
            locale = locale.replace("_", "-").split("-")[0]
        else:
            locale = "en"
        return plural_tags.get(locale, plural_tags["en"])

    def serialize(self, out):
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
        """Recursive function to extract items from the data files

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
                    v, stop, prev + [("key", k)], k, None, data
                )
        elif isinstance(data, list):
            for i, item in enumerate(data):
                yield from self._extract_units(
                    item, stop, prev + [("index", i)], i, name_node, data
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

    def parse(self, input):
        """parse the given file or file source string"""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            src = input.read()
            input.close()
            input = src
        if isinstance(input, bytes):
            # The JSON files should be UTF-8, but implementations
            # that parse JSON texts MAY ignore the presence of a byte order mark
            # rather than treating it as an error, see RFC7159
            input, self.encoding = self.detect_encoding(input)
            if input is None:
                raise base.ParseError(ValueError("Failed to decode JSON string."))
        try:
            self._file = json.loads(input)
        except ValueError as e:
            raise base.ParseError(e)

        for unit in self._extract_units(self._file, stop=self._filter):
            self.addunit(unit)


class JsonNestedUnit(BaseJsonUnit):
    def storevalues(self, output):
        self.storevalue(output, self.converttarget())


class JsonNestedFile(JsonFile):
    """A JSON file with nested keys"""

    UnitClass = JsonNestedUnit


class WebExtensionJsonUnit(BaseJsonUnit):
    def storevalues(self, output):
        value = {"message": self.target}
        if self.notes:
            value["description"] = self.notes
        if self.placeholders:
            value["placeholders"] = self.placeholders
        self.storevalue(output, value)


class WebExtensionJsonFile(JsonFile):
    """WebExtension JSON file

    See following URLs for doc:

    https://developer.chrome.com/extensions/i18n
    https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization
    """

    UnitClass = WebExtensionJsonUnit

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for item, value in data.items():
            unit = self.UnitClass(
                value.get("message", ""),
                item,
                value.get("description", ""),
                value.get("placeholders", None),
            )
            unit.setid(item)
            yield unit


class I18NextUnit(JsonNestedUnit):
    """A i18next v3 format, JSON with plurals.

    See https://www.i18next.com/
    """

    @staticmethod
    def _is_valid_suffix(suffix: str) -> bool:
        return suffix == "0"

    def _get_base_name(self):
        """Return base name for plurals"""
        item = self._item[0]
        if "_" in item:
            plural_base, _sep, suffix = item.rpartition("_")
            if self._is_valid_suffix(suffix):
                return plural_base
        return item

    def _get_plural_labels(self, count):
        base_name = self._get_base_name()
        if count == 2:
            return [base_name, base_name + "_plural"][:count]
        return [f"{base_name}_{i}" for i in range(count)]

    def _fixup_item(self):
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
    def target(self, target):
        self._rich_target = None
        self._target = target

    def storevalues(self, output):
        if not isinstance(self.target, multistring):
            super().storevalues(output)
        else:
            if len(self.target.strings) > len(self._store.plural_tags):
                self.target.strings = self.target.strings[
                    : len(self._store.plural_tags)
                ]
            self._fixup_item()
            for i, value in enumerate(self.target.strings):
                self.storevalue(output, value, override_key=self._item[i])


class I18NextFile(JsonNestedFile):
    """A i18next v3 format, this is nested JSON with several additions.

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
                if k in plurals_simple or k + "_plural" in plurals_simple:
                    if k.endswith("_plural"):
                        plural_base = k[:-7]
                    else:
                        plural_base = k
                    plurals_simple.remove(plural_base)
                    plurals = [k, k + "_plural"]
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
                    newid = prev + [("key", plural_base)]
                    unit.set_unitid(newid)
                    yield unit
                    continue

                yield from self._extract_units(
                    v, stop, prev + [("key", k)], k, None, data
                )
        else:
            yield from super()._extract_units(
                data, stop, prev, name_node, name_last_node, last_node
            )


class I18NextV4Unit(I18NextUnit):
    """A i18next v4 format, JSON with plurals.

    See https://www.i18next.com/
    """

    @staticmethod
    def _is_valid_suffix(suffix: str) -> bool:
        return suffix in cldr_plural_categories

    def _get_plural_labels(self, count):
        base_name = self._get_base_name()
        return [f"{base_name}_{self._store.plural_tags[i]}" for i in range(count)]


class I18NextV4File(JsonNestedFile):
    """A i18next v4 format, this is nested JSON with several additions.

    See https://www.i18next.com/
    """

    UnitClass = I18NextV4Unit

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
            processed = set()

            for k, v in data.items():
                # Check already processed items
                if k in processed:
                    continue

                plurals = []
                suffix = ""
                plural_base = ""

                if "_" in k:
                    plural_base, suffix = k.rsplit("_", 1)

                if suffix in cldr_plural_categories:
                    plurals = [f"{plural_base}_{suffix}" for suffix in self.plural_tags]

                if plurals:
                    sources = []
                    items = []
                    for key in plurals:
                        processed.add(key)
                        sources.append(data.get(key, ""))
                        items.append(key)

                    unit = self.UnitClass(multistring(sources), items)
                    newid = prev + [("key", plural_base)]
                    unit.set_unitid(newid)
                    yield unit
                    continue

                yield from self._extract_units(
                    v, stop, prev + [("key", k)], k, None, data
                )
        else:
            yield from super()._extract_units(
                data, stop, prev, name_node, name_last_node, last_node
            )


class GoTextJsonUnit(BaseJsonUnit):
    ID_FORMAT = "{}"

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
    ):
        super().__init__(source, item, notes, placeholders)
        self.comment = comment
        self.message = message
        self.meaning = meaning
        self.key = key
        self.fuzzy = fuzzy
        self.position = position

    def getvalue(self):
        target = self.target
        if isinstance(target, multistring):
            strings = list(target.strings)
            if len(self._store.plural_tags) > len(target.strings):
                strings += [""] * (len(self._store.plural_tags) - len(target.strings))
            target = {
                "select": {
                    "feature": "plural",
                }
            }
            if self.placeholders:
                target["select"]["arg"] = self.placeholders[0]["id"]
            target["select"]["cases"] = {
                plural: {"msg": strings[offset]}
                for offset, plural in enumerate(self._store.plural_tags)
            }
        value = {"id": self.getid()}
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
        value["translation"] = target
        if self.placeholders:
            value["placeholders"] = self.placeholders
        return value


class GoTextJsonFile(JsonFile):
    """gotext JSON file

    See following URLs for doc:

    https://pkg.go.dev/golang.org/x/text/cmd/gotext
    https://github.com/golang/text/tree/master/cmd/gotext/examples/extract/locales/en-US
    """

    UnitClass = GoTextJsonUnit

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
            lang = data.get("language")
            if lang is not None:
                self.settargetlanguage(lang)
        for value in data["messages"]:
            translation = value.get("translation", "")
            if isinstance(translation, dict):
                cases = translation.get("select", {}).get("cases", {})
                # Ordered list of plurals
                translation = multistring(
                    [
                        cases.get(key, {}).get("msg")
                        for key in cldr_plural_categories
                        if key in cases
                    ]
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
            unit.setid(value.get("id", ""))
            yield unit

    def serialize(self, out):
        units = [unit.getvalue() for unit in self.units]
        file = {
            "language": self.gettargetlanguage(),
            "messages": units,
        }
        out.write(json.dumps(file, **self.dump_args).encode(self.encoding))
        out.write(b"\n")


class GoI18NJsonUnit(BaseJsonUnit):
    ID_FORMAT = "{}"

    def getvalue(self):
        target = self.target
        if isinstance(target, multistring):
            strings = list(target.strings)
            if len(self._store.plural_tags) > len(target.strings):
                strings += [""] * (len(self._store.plural_tags) - len(target.strings))
            target = {
                plural: strings[offset]
                for offset, plural in enumerate(self._store.plural_tags)
            }
        value = {"id": self.getid()}
        if self.notes:
            value["description"] = self.notes
        value["translation"] = target
        return value


class GoI18NJsonFile(JsonFile):
    """go-i18n JSON file

    See following URLs for doc:

    https://github.com/nicksnyder/go-i18n/tree/v1
    https://pkg.go.dev/github.com/nicksnyder/go-i18n
    """

    UnitClass = GoI18NJsonUnit

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for value in data:
            translation = value.get("translation", "")
            if isinstance(translation, dict):
                # Ordered list of plurals
                translation = multistring(
                    [
                        translation.get(key)
                        for key in cldr_plural_categories
                        if key in translation
                    ]
                )
            unit = self.UnitClass(
                translation,
                value.get("id", ""),
                value.get("description", ""),
            )
            unit.setid(value.get("id", ""))
            yield unit

    def serialize(self, out):
        units = [unit.getvalue() for unit in self.units]
        out.write(json.dumps(units, **self.dump_args).encode(self.encoding))
        out.write(b"\n")


class GoI18NV2JsonUnit(BaseJsonUnit):
    ID_FORMAT = "{}"

    def getvalue(self):
        target = self.target

        if isinstance(target, multistring) and len(target.strings) == 1:
            target = str(target.strings[0])

        if isinstance(target, str) and not self.notes:
            return target

        if isinstance(target, multistring):
            strings = list(target.strings)
            if len(self._store.plural_tags) > len(target.strings):
                strings += [""] * (len(self._store.plural_tags) - len(target.strings))
            target = {
                plural: strings[offset]
                for offset, plural in enumerate(self._store.plural_tags)
            }
        else:
            target = {"other": target}

        value = {}
        if self.notes:
            value["description"] = self.notes
        for plural_tag, plural_target in target.items():
            value[plural_tag] = plural_target
        return value


class GoI18NV2JsonFile(JsonFile):
    """go-i18n v2 JSON file

    See following URLs for doc:

    https://github.com/nicksnyder/go-i18n
    https://pkg.go.dev/github.com/nicksnyder/go-i18n/v2
    """

    UnitClass = GoI18NV2JsonUnit

    def _extract_units(
        self,
        data,
        stop=None,
        prev=None,
        name_node=None,
        name_last_node=None,
        last_node=None,
    ):
        for id, value in data.items():
            if isinstance(value, str):
                unit = self.UnitClass(value, id)
            else:
                translation = multistring(
                    [value.get(key) for key in cldr_plural_categories if key in value]
                )
                # Default to str in case of a unique translation
                if len(translation.strings) == 1:
                    translation = str(translation.strings[0])

                unit = self.UnitClass(
                    translation,
                    id,
                    value.get("description", ""),
                )
            unit.setid(id)
            yield unit

    def serialize(self, out):
        units = {unit.getid(): unit.getvalue() for unit in self.units}
        out.write(json.dumps(units, **self.dump_args).encode(self.encoding))
        out.write(b"\n")


class ARBJsonUnit(BaseJsonUnit):
    ID_FORMAT = "{}"

    def __init__(
        self,
        source=None,
        item=None,
        notes=None,
        placeholders=None,
        metadata=None,
        **kwargs,
    ):
        super().__init__(source, item, notes, placeholders, **kwargs)
        self.metadata = metadata or {}

    def storevalues(self, output):
        if self.notes:
            self.metadata["description"] = self.notes
        identifier = self.getid()
        if identifier == "@":
            for key, value in self.metadata.items():
                self.storevalue(output, value, override_key=key)
        else:
            self.storevalue(output, self.target, override_key=identifier)
            self.storevalue(output, self.metadata, override_key=f"@{identifier}")

    def isheader(self):
        return self._id == "@"


class ARBJsonFile(JsonFile):
    """ARB JSON file

    See following URLs for doc:

    https://github.com/google/app-resource-bundle/wiki/ApplicationResourceBundleSpecification
    https://docs.flutter.dev/development/accessibility-and-localization/internationalization#dart-tools
    """

    UnitClass = ARBJsonUnit

    def __init__(self, inputfile=None, filter=None, **kwargs):
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
        # Extract metadata as header
        metadata = {key: value for key, value in data.items() if key.startswith("@@")}
        if metadata:
            unit = self.UnitClass(metadata=metadata)
            unit.setid("@")
            yield unit

        for item, value in data.items():
            if item.startswith("@"):
                continue
            metadata = data.get(f"@{item}", {})
            unit = self.UnitClass(
                value,
                item,
                metadata.get("description", ""),
                metadata.get("placeholders", None),
                metadata=metadata,
            )
            unit.setid(item)
            yield unit
