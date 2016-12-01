# -*- coding: utf-8 -*-
#
# Copyright 2016 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

from codecs import iterencode

from l20n.format.parser import FTLParser as L20nParser
from l20n.format.serializer import FTLSerializer as L20nSerializer

from translate.storage import base


def dump_l20n_entity_value(entity):
    serializer = L20nSerializer()
    value = serializer.dumpPattern(entity['value'])

    if len(entity['traits']):
        traits = serializer.dumpMembers(entity['traits'], 2)
        return u'{}\n{}'.format(value, traits)

    return value


def get_l20n_entry(value):
    return u'unit = {}'.format(value)


class l20nunit(base.TranslationUnit):
    """Single L20n Entity"""

    def __init__(self, source='', id='', comment=''):
        super(l20nunit, self).__init__(source)
        self.id = id
        self.value = source
        self.comment = comment

    # Note that source and target are equivalent for monolingual units
    def getsource(self):
        return self.value

    def setsource(self, source):
        self.value = source

    source = property(getsource, setsource)

    def gettarget(self):
        return self.value

    def settarget(self, target):
        self.value = target

    target = property(gettarget, settarget)

    def getid(self):
        return self.id

    def setid(self, new_id):
        self.id = new_id

    def getoutput(self):
        return u"%s = %s\n" % (self.id, self.value)


class l20nfile(base.TranslationStore):
    UnitClass = l20nunit
    encoding = 'utf8'

    def __init__(self, inputfile=None):
        super(l20nfile, self).__init__(unitclass=self.UnitClass)
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
            l20nsrc = inputfile.read()
            self.parse(l20nsrc)
            self.makeindex()

    def parse_entity(self, entity):
        translation = dump_l20n_entity_value(entity)
        comment = ''
        if entity['comment']:
            comment = entity['comment']['content']

        newl20n = l20nunit(
            source=translation,
            id=entity['id']['name'],
            comment=comment
        )
        self.addunit(newl20n)

    def parse(self, l20nsrc):
        text, encoding = self.detect_encoding(
            l20nsrc, default_encodings=[self.encoding])
        if not text:
            raise IOError("Cannot detect encoding for %s." % (self.filename or
                                                              "given string"))
        l20nsrc = text

        parser = L20nParser()
        ast, errors = parser.parseResource(l20nsrc)

        for entry in ast['body']:
            if entry['type'] == 'Entity':
                self.parse_entity(entry)

    def serialize(self, out):
        """Write the units back to file."""
        # Thanks to iterencode, a possible BOM is written only once
        for chunk in iterencode((unit.getoutput() for unit in self.units), self.encoding):
            out.write(chunk)
