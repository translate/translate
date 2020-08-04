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


class YAMLUnit(base.DictUnit):
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

    def getkey(self):
        return self.getid().split('->')

    def convert_target(self):
        return self.target

    def getvalue(self):
        ret = self.convert_target()
        for k in reversed(self.getkey()):
            if '[' in k and k[-1] == ']':
                k, pos = k[:-1].split('[')
                ret = (int(pos), ret)
                if not k:
                    continue
            ret = {k: ret}
        return ret


class YAMLFile(base.DictStore):
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


class RubyYAMLUnit(YAMLUnit):
    def convert_target(self):
        if not isinstance(self.target, multistring):
            return self.target

        tags = plural_tags.get(self._store.targetlanguage, plural_tags['en'])

        strings = [str(s) for s in self.target.strings]

        # Sync plural_strings elements to plural_tags count.
        if len(strings) < len(tags):
            strings += [''] * (len(tags) - len(strings))
        strings = strings[:len(tags)]

        return CommentedMap(zip(tags, strings))


class RubyYAMLFile(YAMLFile):
    """Ruby YAML file, it has language code as first node."""

    UnitClass = RubyYAMLUnit

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
