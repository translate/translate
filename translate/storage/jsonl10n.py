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

    def __init__(self, source=None, item=None, notes=None, **kwargs):
        identifier = str(uuid.uuid4())
        # Global identifier across file
        self._id = '.' + identifier
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

    def getsource(self):
        return self.target

    def setsource(self, source):
        self.target = source
    source = property(getsource, setsource)

    def setid(self, value):
        self._id = value

    def getid(self):
        return self._id

    def getlocations(self):
        return [self.getid()]

    def __str__(self):
        """Converts to a string representation."""
        return json.dumps(self.getvalue(), separators=(',', ': '), indent=4, ensure_ascii=False)

    def getkey(self):
        return self.getid().lstrip('.')

    def converttarget(self):
        if issubclass(self._type, six.string_types):
            return self.target
        else:
            return self._type(self.target)

    def getvalue(self):
        """Return value to be stored in JSON file."""
        return {self.getkey(): self.converttarget()}


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
        def merge(d1, d2):
            for k in d2:
                if k in d1 and isinstance(d1[k], dict) and isinstance(d2[k], dict):
                    merge(d1[k], d2[k])
                else:
                    d1[k] = d2[k]
        units = OrderedDict()
        for unit in self.unit_iter():
            merge(units, unit.getvalue())
        out.write(json.dumps(units, **self.dump_args).encode(self.encoding))
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

    def getkey(self):
        return self.getid().lstrip('.').split('.')

    def getvalue(self):
        ret = self.converttarget()
        for k in reversed(self.getkey()):
            ret = {k: ret}
        return ret


class JsonNestedFile(JsonFile):
    """A JSON file with nested keys"""

    UnitClass = JsonNestedUnit


class WebExtensionJsonUnit(JsonUnit):
    def getvalue(self):
        value = OrderedDict((
            ('message', self.target),
        ))
        if self.notes:
            value['description'] = self.notes
        return {self.getid(): value}


class WebExtensionJsonFile(JsonFile):
    """WebExtension JSON file

    See following URLs for doc:

    https://developer.chrome.com/extensions/i18n
    https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Internationalization
    """

    UnitClass = WebExtensionJsonUnit

    def _extract_translatables(self, data, stop=None, prev="", name_node=None,
                               name_last_node=None, last_node=None):
        for item, value in six.iteritems(data):
            yield (item, value.get('message', ''), item, value.get('description', ''))


class I18NextUnit(JsonNestedUnit):
    """A i18next v3 format, JSON with plurals.

    See https://www.i18next.com/
    """

    def settarget(self, target):
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
        super(I18NextUnit, self).settarget(target)
    target = property(lambda self: self._target, settarget)

    def getvalue(self):
        if not isinstance(self.target, multistring):
            return super(I18NextUnit, self).getvalue()

        ret = OrderedDict()
        for i, value in enumerate(self.target.strings):
            ret[self._item[i]] = value

        path = self.getid().lstrip('.').split('.')[:-1]
        for k in reversed(path):
            ret = {k: ret}
        return ret


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
                    yield ("%s.%s" % (prev, plural_base), multistring(sources), items, '')
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
