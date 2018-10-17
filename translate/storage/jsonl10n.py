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

from translate.misc.deprecation import deprecated
from translate.misc.multistring import multistring
from translate.storage import base


class UnitId(object):
    def __init__(self, parts):
        self.parts = parts

    def __str__(self):
        def fmt(element, key):
            if element == 'key':
                return '.{}'.format(key)
            elif element == 'index':
                return '[{}]'.format(key)
            else:
                raise ValueError('Unsupported element: {}'.format(element))
        return ''.join([fmt(*part) for part in self.parts])

    def __add__(self, other):
        if not isinstance(other, list):
            raise ValueError('Not supported type for add: {}'.format(type(other)))
        return UnitId(self.parts + other)

    def encode(self, charset):
        return self.__str__().encode(charset)


class JsonUnit(base.TranslationUnit):
    """A JSON entry"""

    def __init__(self, source=None, item=None, notes=None, **kwargs):
        identifier = str(uuid.uuid4())
        # Global identifier across file
        self._id = UnitId([('key', identifier)])
        # Identifier at this level
        self._item = identifier if item is None else item
        # Type conversion for the unit
        self._type = six.text_type if source is None else type(source)
        if notes:
            self.notes = notes
        if source:
            if issubclass(self._type, six.string_types):
                self.target = source
            else:
                self.target = str(source)
        super(JsonUnit, self).__init__(source)

    @property
    def source(self):
        return self.target

    @source.setter
    def source(self, source):
        self.target = source

    # Deprecated on 2.3.1
    @deprecated("Use `source` property instead")
    def getsource(self):
        return self.source

    def setid(self, value):
        self._id = value

    def getid(self):
        return self._id

    def getlocations(self):
        return [str(self.getid())]

    def __str__(self):
        """Converts to a string representation."""
        return json.dumps(self.getvalue(), separators=(',', ': '), indent=4, ensure_ascii=False)

    def converttarget(self):
        if issubclass(self._type, six.string_types):
            return self.target
        else:
            return self._type(self.target)

    def storevalue(self, result, override_key=None, override_value=None):
        ret = override_value if override_value else self.converttarget()
        target = result
        parts = self.getid().parts
        for pos, part in enumerate(parts[:-1]):
            element, key = part
            default = [] if parts[pos + 1][0] == 'index' else OrderedDict()
            if element == 'index':
                if len(target) <= key:
                    target.append(default)
            elif element == 'key':
                if key not in target:
                    target[key] = default
            else:
                raise ValueError('Unsupported element: {}'.format(element))
            target = target[key]
        if override_key:
            element, key = 'key', override_key
        else:
            element, key = parts[-1]
        if element == 'key':
            target[key] = ret
        elif element == 'index':
            target.append(ret)
        else:
            raise ValueError('Unsupported element: {}'.format(element))

    def getvalue(self):
        """Return value to be stored in JSON file."""
        result = OrderedDict()
        self.storevalue(result)
        return result


class JsonFile(base.TranslationStore):
    """A JSON file"""

    UnitClass = JsonUnit

    def __init__(self, inputfile=None, filter=None, **kwargs):
        """construct a JSON file, optionally reading in from inputfile."""
        super(JsonFile, self).__init__(**kwargs)
        self._filter = filter
        self.filename = ''
        self._file = u''
        self.dump_args = {
            'separators': (',', ': '),
            'indent': 4,
            'ensure_ascii': False,
        }
        if inputfile is not None:
            self.parse(inputfile)

    def serialize(self, out):
        units = OrderedDict()
        for unit in self.unit_iter():
            unit.storevalue(units)
        out.write(json.dumps(units, **self.dump_args).encode(self.encoding))
        out.write(b'\n')

    def _extract_translatables(self, data, stop=None, prev=None, name_node=None,
                               name_last_node=None, last_node=None):
        """Recursive function to extract items from the data files

        :param data: the current branch to walk down
        :param stop: a list of leaves to extract or None to extract everything
        :param prev: the hierarchy of the tree at this iteration
        :param name_node:
        :param name_last_node: the name of the last node
        :param last_node: the last list or dict
        """
        if prev is None:
            prev = UnitId([])
        if isinstance(data, dict):
            for k, v in six.iteritems(data):
                for x in self._extract_translatables(v, stop,
                                                     prev + [('key', k)],
                                                     k, None, data):
                    yield x
        elif isinstance(data, list):
            for i, item in enumerate(data):
                for x in self._extract_translatables(item, stop,
                                                     prev + [('index', i)],
                                                     i, name_node, data):
                    yield x
        # apply filter
        elif (stop is None or
              (isinstance(last_node, dict) and name_node in stop) or
              (isinstance(last_node, list) and name_last_node in stop)):

            yield (prev, data, name_node, '')

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

        for k, data, item, notes in self._extract_translatables(self._file,
                                                                stop=self._filter):
            unit = self.UnitClass(data, item, notes)
            unit.setid(k)
            self.addunit(unit)


class JsonNestedUnit(JsonUnit):
    pass


class JsonNestedFile(JsonFile):
    """A JSON file with nested keys"""

    UnitClass = JsonNestedUnit


class WebExtensionJsonUnit(JsonUnit):
    def storevalue(self, result):
        value = OrderedDict((
            ('message', self.target),
        ))
        if self.notes:
            value['description'] = self.notes
        super(WebExtensionJsonUnit, self).storevalue(result, override_value=value)


class WebExtensionJsonFile(JsonFile):
    """WebExtension JSON file

    See following URLs for doc:

    https://developer.chrome.com/extensions/i18n
    https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization
    """

    UnitClass = WebExtensionJsonUnit

    def _extract_translatables(self, data, stop=None, prev=None, name_node=None,
                               name_last_node=None, last_node=None):
        for item, value in six.iteritems(data):
            yield (UnitId([('key', item)]), value.get('message', ''), item, value.get('description', ''))


class I18NextUnit(JsonNestedUnit):
    """A i18next v3 format, JSON with plurals.

    See https://www.i18next.com/
    """

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
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

        if isinstance(target, multistring):
            count = len(target.strings)
            if not isinstance(self._item, list):
                self._item = [self._item]
            if count != len(self._item):
                # Generate new plural labels
                self._item = get_plurals(count, get_base(self._item))
        elif isinstance(self._item, list):
            # Changing plural to singular
            self._item = get_base(self._item)

        self._rich_target = None
        self._target = target

    def storevalue(self, result):
        if isinstance(self.target, multistring):
            for i, value in enumerate(self.target.strings):
                super(I18NextUnit, self).storevalue(result, self._item[i], value)
        else:
            super(I18NextUnit, self).storevalue(result)


class I18NextFile(JsonNestedFile):
    """A i18next v3 format, this is nested JSON with several additions.

    See https://www.i18next.com/
    """

    UnitClass = I18NextUnit

    def _extract_translatables(self, data, stop=None, prev=None, name_node=None,
                               name_last_node=None, last_node=None):
        if prev is None:
            prev = UnitId([])
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
                    yield prev + [('key', plural_base)], multistring(sources), items, ''
                    continue

                for x in self._extract_translatables(v, stop,
                                                     prev + [('key', k)],
                                                     k, None, data):
                    yield x
        else:
            parent = super(I18NextFile, self)._extract_translatables(
                data, stop, prev, name_node, name_last_node, last_node
            )
            for x in parent:
                yield x
