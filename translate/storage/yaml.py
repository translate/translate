# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from __future__ import unicode_literals

import uuid
from collections import OrderedDict

import six
import yaml
import yaml.constructor

from translate.storage import base


class OrderedDictYAMLLoader(yaml.SafeLoader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.SafeLoader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(
                None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark
            )

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    'while constructing a mapping',
                    node.start_mark,
                    'found unacceptable key (%s)' % exc, key_node.start_mark
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


class UnsortableList(list):
    def sort(self, *args, **kwargs):
        pass


class UnsortableOrderedDict(OrderedDict):
    def items(self, *args, **kwargs):
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))


class YAMLDumper(yaml.SafeDumper):
    def represent_unsorted(self, data):
        return self.represent_dict(data.items())


YAMLDumper.add_representer(UnsortableOrderedDict, YAMLDumper.represent_unsorted)


class YAMLUnit(base.TranslationUnit):
    """A YAML entry"""

    def __init__(self, source=None, **kwargs):
        self._id = None
        if source:
            self.source = source
        super(YAMLUnit, self).__init__(source)

    def getsource(self):
        return self.target

    def setsource(self, source):
        self.target = source
    source = property(getsource, setsource)

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
        super(YAMLFile, self).__init__(**kwargs)
        self.filename = ''
        self._file = u''
        if inputfile is not None:
            self.parse(inputfile)

    def get_root_node(self, node):
        """Returns root node for serialize"""
        return node

    def serialize(self, out):
        def nested_set(target, path, value):
            if len(path) > 1:
                if len(path) == 2 and path[1][0] == '[' and path[1][-1] == ']' and path[1][1:-1].isdigit():
                    if path[0] not in target:
                        target[path[0]] = []
                    target[path[0]].append(value)
                else:
                    if path[0] not in target:
                        target[path[0]] = UnsortableOrderedDict()
                    nested_set(target[path[0]], path[1:], value)
            else:
                target[path[0]] = value

        units = UnsortableOrderedDict()
        for unit in self.unit_iter():
            nested_set(units, unit.getid().split(' / '), unit.target)
        out.write(yaml.dump_all(
            [self.get_root_node(units)],
            Dumper=YAMLDumper,
            default_flow_style=False, encoding='utf-8', allow_unicode=True
        ))

    def _flatten(self, data, prev=""):
        """Flatten YAML dictionary.
        """
        if isinstance(data, dict):
            for k, v in six.iteritems(data):
                if not isinstance(k, six.string_types):
                    raise base.ParseError(
                        'Key not string: {0}/{1} ({2})'.format(prev, k, type(k))
                    )

                for x in self._flatten(v, ' / '.join((prev, k)) if prev else k):
                    yield x
        else:
            if isinstance(data, six.string_types):
                yield (prev, data)
            elif isinstance(data, bool):
                yield (prev, str(data))
            elif isinstance(data, list):
                for k, v in enumerate(data):
                    key = '[{0}]'.format(k)
                    yield (' / '.join((prev, key)), six.text_type(v))
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
            self._file = yaml.load(input, OrderedDictYAMLLoader)
        except yaml.YAMLError as e:
            if hasattr(e, 'problem'):
                message = e.problem
            else:
                message = e.message
            if hasattr(e, 'problem_mark'):
                message += ' {0}'.format(e.problem_mark)
            raise base.ParseError(message)

        self._file = self.preprocess(self._file)

        for k, data in self._flatten(self._file):
            unit = self.UnitClass(data)
            unit.setid(k)
            self.addunit(unit)


class RubyYAMLFile(YAMLFile):
    """Ruby YAML file, it has language code as first node."""

    def preprocess(self, data):
        if isinstance(data, OrderedDict) and len(data) == 1:
            lang = list(data.keys())[0]
            self.settargetlanguage(lang)
            return data[lang]
        return data

    def get_root_node(self, node):
        """Returns root node for serialize"""
        if self.targetlanguage is not None:
            result = UnsortableOrderedDict()
            result[self.targetlanguage] = node
            return result
        return node
