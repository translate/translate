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

r"""Class that manages YAML data files for translation
"""


import uuid

from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.comments import CommentedMap

from translate.lang.data import cldr_plural_categories, plural_tags
from translate.misc.multistring import multistring
from translate.storage import base


class YAMLUnit(base.TranslationUnit):
    """A YAML entry"""

    def __init__(self, source=None, **kwargs):
        self._id = None
        if source:
            self.source = source
        super().__init__(source)

    @property
    def source(self):
        return self.target

    @source.setter
    def source(self, source):
        self.target = source

    def setid(self, value):
        self._id = value

    def getid(self):
        # Ensure we have ID (for serialization)
        if self._id is None:
            self._id = str(uuid.uuid4())
        return self._id

    def getlocations(self):
        return [self.getid()]


class YAMLFile(base.TranslationStore):
    """A YAML file"""

    UnitClass = YAMLUnit

    def __init__(self, inputfile=None, **kwargs):
        """construct a YAML file, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = ''
        self._original = self.get_root_node()
        self.dump_args = {
            'default_flow_style': False,
            'preserve_quotes': True,
        }
        if inputfile is not None:
            self.parse(inputfile)

    def get_root_node(self):
        """Returns root node for serialize"""
        return CommentedMap()

    def serialize_value(self, value):
        return value

    @property
    def yaml(self):
        yaml = YAML()
        for arg, value in self.dump_args.items():
            setattr(yaml, arg, value)
        return yaml

    def serialize(self, out):
        def nested_set(target, path, value):
            value = self.serialize_value(value)
            if len(path) > 1:
                if len(path) >= 2 and path[1] and path[1][0] == '[' and path[1][-1] == ']' and path[1][1:-1].isdigit():
                    if path[0] not in target:
                        target[path[0]] = []
                    if len(path) > 2:
                        value = nested_set(CommentedMap(), path[2:], value)
                    pos = int(path[1][1:-1])
                    if len(target[path[0]]) < pos + 1:
                        target[path[0]].append(value)
                    else:
                        target[path[0]][pos] = value
                else:
                    # Add empty dict in case there is value and we
                    # expect dict
                    if path[0] not in target or not isinstance(target[path[0]], dict):
                        target[path[0]] = CommentedMap()
                    nested_set(target[path[0]], path[1:], value)
            else:
                target[path[0]] = value
            return target

        # Always start with valid root even if original file was empty
        if self._original is None:
            self._original = self.get_root_node()

        units = self.preprocess(self._original)
        for unit in self.unit_iter():
            nested_set(units, unit.getid().split('->'), unit.target)
        self.yaml.dump(self._original, out)

    def _parse_dict(self, data, prev):
        # Avoid using merged items, it is enough to have them once
        for k, v in data.non_merged_items():
            if not isinstance(k, str):
                raise base.ParseError(
                    'Key not string: {0}/{1} ({2})'.format(prev, k, type(k))
                )

            for x in self._flatten(v, '->'.join((prev, k)) if prev else k):
                yield x

    def _flatten(self, data, prev=""):
        """Flatten YAML dictionary.
        """
        if isinstance(data, dict):
            for x in self._parse_dict(data, prev):
                yield x
        else:
            if isinstance(data, str):
                yield (prev, data)
            elif isinstance(data, (bool, int)):
                yield (prev, str(data))
            elif isinstance(data, list):
                for k, v in enumerate(data):
                    key = '[{0}]'.format(k)
                    for value in self._flatten(v, '->'.join((prev, key))):
                        yield value
            elif data is None:
                pass
            else:
                raise ValueError("We don't handle these values:\n"
                                 "Type: %s\n"
                                 "Data: %s\n"
                                 "Previous: %s" % (type(data), data, prev))

    def preprocess(self, data):
        """Preprocess hook for child formats"""
        return data

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
            self._original = self.yaml.load(input)
        except YAMLError as e:
            message = e.problem if hasattr(e, 'problem') else e.message
            if hasattr(e, 'problem_mark'):
                message += ' {0}'.format(e.problem_mark)
            raise base.ParseError(message)

        content = self.preprocess(self._original)

        for k, data in self._flatten(content):
            unit = self.UnitClass(data)
            unit.setid(k)
            self.addunit(unit)


class RubyYAMLFile(YAMLFile):
    """Ruby YAML file, it has language code as first node."""

    def preprocess(self, data):
        if isinstance(data, CommentedMap) and len(data) == 1:
            lang = list(data.keys())[0]
            self.settargetlanguage(lang)
            return data[lang]
        return data

    def get_root_node(self):
        """Returns root node for serialize"""
        if self.targetlanguage is not None:
            result = CommentedMap()
            result[self.targetlanguage] = CommentedMap()
            return result
        return CommentedMap()

    def _parse_dict(self, data, prev):
        # Does this look like a plural?
        if data and all((x in cldr_plural_categories for x in data.keys())):
            # Ensure we have correct plurals ordering.
            values = [data[item] for item in cldr_plural_categories if item in data]
            yield (prev, multistring(values))
            return

        # Handle normal dict
        for x in super()._parse_dict(data, prev):
            yield x

    def serialize_value(self, value):
        if not isinstance(value, multistring):
            return value

        tags = plural_tags.get(self.targetlanguage, plural_tags['en'])

        strings = [str(s) for s in value.strings]

        # Sync plural_strings elements to plural_tags count.
        if len(strings) < len(tags):
            strings += [''] * (len(tags) - len(strings))
        strings = strings[:len(tags)]

        return CommentedMap(zip(tags, strings))
