# -*- coding: utf-8 -*-
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
from collections import OrderedDict

import six

from translate.misc.multistring import multistring
from translate.storage import base


class JsonUnit(base.TranslationUnit):
    """A JSON entry"""

    def __init__(self, source=None, ref=None, item=None, **kwargs):
        identifier = str(uuid.uuid4())
        self._id = '.' + identifier
        self._item = identifier if item is None else item
        self._ref = OrderedDict() if ref is None else ref
        if ref is None and item is None:
            self._ref[self._item] = ""
        if source:
            self.source = source
        super(JsonUnit, self).__init__(source)

    def getsource(self):
        return self.target

    def setsource(self, source):
        self.target = source
    source = property(getsource, setsource)

    def gettarget(self):

        def change_type(value):
            if isinstance(value, bool):
                return str(value)
            return value

        if isinstance(self._ref, list):
            return change_type(self._ref[self._item])
        elif isinstance(self._ref, dict):
            return change_type(self._ref[self._item])

    def settarget(self, target):

        def change_type(oldvalue, newvalue):
            if isinstance(oldvalue, bool):
                newvalue = bool(newvalue)
            return newvalue

        if isinstance(self._ref, list):
            self._ref[int(self._item)] = change_type(self._ref[int(self._item)],
                                                     target)
        elif isinstance(self._ref, dict):
            self._ref[self._item] = change_type(self._ref[self._item], target)
        else:
            raise ValueError("We don't know how to handle:\n"
                             "Type: %s\n"
                             "Value: %s" % (type(self._ref), target))
    target = property(gettarget, settarget)

    def setid(self, value):
        self._id = value

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def __str__(self):
        """Converts to a string representation."""
        return ", ".join([
            "%s: %s" % (k, self.__dict__[k]) for k in sorted(self.__dict__.keys()) if k not in ('_store', '_ref')
        ])


class JsonFile(base.TranslationStore):
    """A JSON file"""

    UnitClass = JsonUnit

    def __init__(self, inputfile=None, filter=None, **kwargs):
        """construct a JSON file, optionally reading in from inputfile."""
        super(JsonFile, self).__init__(**kwargs)
        self._filter = filter
        self.filename = ''
        self._file = u''
        if inputfile is not None:
            self.parse(inputfile)

    def serialize_units(self):
        units = OrderedDict()
        for unit in self.unit_iter():
            path = unit.getid().lstrip('.')
            units[path] = unit.target
        return units

    def serialize(self, out):
        units = self.serialize_units()
        out.write(json.dumps(units, separators=(',', ': '),
                             indent=4, ensure_ascii=False).encode(self.encoding))
        out.write(b'\n')

    def _extract_translatables(self, data, stop=None, prev="", name_node=None,
                               name_last_node=None, last_node=None):
        """Recursive function to extract items from the data files

        :param data: the current branch to walk down
        :param stop: a list of leaves to extract or None to extract everything
        :param prev: the hierarchy of the tree at this iteration
        :param name_node:
        :param name_last_node: the name of the last node
        :param last_node: the last list or dict
        """
        if isinstance(data, dict):
            for k, v in six.iteritems(data):
                for x in self._extract_translatables(v, stop,
                                                     "%s.%s" % (prev, k),
                                                     k, None, data):
                    yield x
        elif isinstance(data, list):
            for i, item in enumerate(data):
                for x in self._extract_translatables(item, stop,
                                                     "%s[%s]" % (prev, i),
                                                     i, name_node, data):
                    yield x
        # apply filter
        elif (stop is None or
              (isinstance(last_node, dict) and name_node in stop) or
              (isinstance(last_node, list) and name_last_node in stop)):

            if isinstance(data, six.string_types):
                yield (prev, data, last_node, name_node)
            elif isinstance(data, bool):
                yield (prev, str(data), last_node, name_node)
            elif data is None:
                pass
            else:
                raise ValueError("We don't handle these values:\n"
                                 "Type: %s\n"
                                 "Data: %s\n"
                                 "Previous: %s" % (type(data), data, prev))

    def parse(self, input):
        """parse the given file or file source string"""
        if hasattr(input, 'name'):
            self.filename = input.name
        elif not getattr(self, 'filename', ''):
            self.filename = ''
        if hasattr(input, "read"):
            src = input.read()
            input.close()
            input = src
        if isinstance(input, bytes):
            input = input.decode('utf-8')
        try:
            self._file = json.loads(input, object_pairs_hook=OrderedDict)
        except ValueError as e:
            raise base.ParseError(e.message)

        for k, data, ref, item in self._extract_translatables(self._file,
                                                              stop=self._filter):
            unit = self.UnitClass(data, ref, item)
            unit.setid(k)
            self.addunit(unit)


class JsonNestedFile(JsonFile):
    """A JSON file with nested keys"""

    def nested_set(self, target, path, value):
        if len(path) > 1:
            if path[0] not in target:
                target[path[0]] = OrderedDict()
            self.nested_set(target[path[0]], path[1:], value)
        else:
            target[path[0]] = value

    def serialize_units(self):
        units = OrderedDict()
        for unit in self.unit_iter():
            path = unit.getid().lstrip('.').split('.')
            self.nested_set(units, path, unit.target)
        return units


class WebExtensionJsonUnit(base.TranslationUnit):
    def __init__(self, source=None, ref=None, item=None):
        identifier = str(uuid.uuid4())
        self._id = identifier
        self._item = identifier if item is None else item
        self.notes = ''
        self._rich_target = None
        if ref:
            self._node = ref
            if 'description' in ref:
                self.notes = ref['description']
            self._target = ref['message']
        else:
            self._node = OrderedDict((('message', source if source else ''), ('description', '')))
            if source:
                self._target = source
        super(WebExtensionJsonUnit, self).__init__()

    def setid(self, value):
        self._id = value

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def getsource(self):
        return self.target

    def setsource(self, source):
        self.target = source
    source = property(getsource, setsource)

    def settarget(self, target):
        super(WebExtensionJsonUnit, self).settarget(target)
        self._node['message'] = target

    def addnote(self, text, origin=None, position="append"):
        super(WebExtensionJsonUnit, self).addnote(text, origin, position)
        self._node['description'] = self.notes

    def removenotes(self):
        super(WebExtensionJsonUnit, self).removenotes()
        if self.notes:
            self._node['description'] = self.notes
        else:
            del self._node['description']

    def __str__(self):
        """Converts to a string representation."""
        return json.dumps(self._node, separators=(',', ': '), indent=4, ensure_ascii=False)


class WebExtensionJsonFile(JsonFile):
    """WebExtension JSON file

    See following URLs for doc:

    https://developer.chrome.com/extensions/i18n
    https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization
    """

    UnitClass = WebExtensionJsonUnit

    def _extract_translatables(self, data, stop=None, prev="", name_node=None,
                               name_last_node=None, last_node=None):
        for item in data:
            yield (item, item, data[item], item)

    def serialize_units(self):
        units = OrderedDict()
        for unit in self.unit_iter():
            units[unit.getid()] = unit._node
        return units


class I18NextUnit(JsonUnit):
    """A i18next v3 format, JSON with plurals.

    See https://www.i18next.com/
    """

    def gettarget(self):

        def change_type(value):
            if isinstance(value, bool):
                return str(value)
            return value

        if isinstance(self._item, list):
            return multistring([
                self._ref[item] for item in self._item
            ])
        if isinstance(self._ref, list):
            return change_type(self._ref[self._item])
        elif isinstance(self._ref, dict):
            return change_type(self._ref[self._item])

    def settarget(self, target):
        def change_type(oldvalue, newvalue):
            if isinstance(oldvalue, bool):
                newvalue = bool(newvalue)
            return newvalue

        def get_base(item):
            """Return base name for plurals"""
            if '_0' in item[0]:
                return item[0][:-2]
            else:
                return item[0]

        def get_plurals(count, base):
            if count <= 2:
                return [base, base + '_plural'][:count]
            return ['{0}_{1}'.format(base, i) for i in range(count)]

        if isinstance(self._ref, list):
            self._ref[int(self._item)] = change_type(self._ref[int(self._item)],
                                                     target)
        elif isinstance(self._ref, dict):
            cleanup = ()
            if isinstance(target, multistring):
                count = len(target.strings)
                if not isinstance(self._item, list):
                    self._item = [self._item]
                if count != len(self._item):
                    # Generate new plural labels
                    newitems = get_plurals(count, get_base(self._item))
                    cleanup = set(self._item) - set(newitems)
                    self._item = newitems
                # Store plural values
                for i, value in enumerate(target.strings):
                    self._ref[self._item[i]] = value
            elif isinstance(self._item, list):
                # Changing plural to singular
                newitem = get_base(self._item)
                cleanup = set(self._item) - set([newitem])
                self._item = newitem
                self._ref[self._item] = target
            else:
                self._ref[self._item] = change_type(self._ref[self._item], target)
            for item in cleanup:
                if item in self._ref:
                    del self._ref[item]
        else:
            raise ValueError("We don't know how to handle:\n"
                             "Type: %s\n"
                             "Value: %s" % (type(self._ref), target))
    target = property(gettarget, settarget)

    def get_path(self):
        if isinstance(self._item, list):
            base = self.getid().lstrip('.').split('.')[:-1]
            return [base + [item] for item in self._item]
        return self.getid().lstrip('.').split('.')


class I18NextFile(JsonNestedFile):
    """A i18next v3 format, this is nested JSON with several additions.

    See https://www.i18next.com/
    """

    UnitClass = I18NextUnit

    def _extract_translatables(self, data, stop=None, prev="", name_node=None,
                               name_last_node=None, last_node=None):
        if isinstance(data, dict):
            plurals_multiple = [key.rsplit('_', 1)[0] for key in data if key.endswith('_0')]
            plurals_simple = [key.rsplit('_', 1)[0] for key in data if key.endswith('_plural')]
            processed = set()

            for k, v in six.iteritems(data):
                # Check already processed items
                if k in processed:
                    continue
                plurals = []
                plural_base = ''
                if k in plurals_simple or k + '_plural' in plurals_simple:
                    if k.endswith('_plural'):
                        plural_base = k[:-7]
                    else:
                        plural_base = k
                    plurals_simple.remove(plural_base)
                    plurals = [k, k + '_plural']
                elif '_' in k:
                    plural_base, digit = k.rsplit('_', 1)
                    if plural_base in plurals_multiple and digit.isdigit():
                        plurals_multiple.remove(plural_base)
                        plurals = ['{0}_{1}'.format(plural_base, order) for order in range(10)]
                if plurals:
                    sources = []
                    items = []
                    for key in plurals:
                        if key not in data:
                            break
                        processed.add(key)
                        sources.append(data[key])
                        items.append(key)
                    yield ("%s.%s" % (prev, plural_base), multistring(sources), data, items)
                    continue

                for x in self._extract_translatables(v, stop,
                                                     "%s.%s" % (prev, k),
                                                     k, None, data):
                    yield x
        else:
            parent = super(I18NextFile, self)._extract_translatables(
                data, stop, prev, name_node, name_last_node, last_node
            )
            for x in parent:
                yield x

    def serialize_units(self):
        units = OrderedDict()
        for unit in self.unit_iter():
            target = unit.target
            path = unit.get_path()
            if isinstance(target, multistring):
                for i, value in enumerate(target.strings):
                    self.nested_set(units, path[i], value)
            else:
                self.nested_set(units, path, target)
        return units
