#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
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
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""classes that hold units of comma-separated values (.csv) files (csvunit)
or entire files (csvfile) for use with localisation
"""

import csv
try:
    import cStringIO as StringIO
except:
    import StringIO

from translate.misc import sparse
from translate.storage import base


class SimpleDictReader:

    def __init__(self, fileobj, fieldnames):
        self.fieldnames = fieldnames
        self.contents = fileobj.read()
        self.parser = sparse.SimpleParser(defaulttokenlist=[",", "\n"], whitespacechars="\r")
        self.parser.stringescaping = 0
        self.parser.quotechars = '"'
        self.tokens = self.parser.tokenize(self.contents)
        self.tokenpos = 0

    def __iter__(self):
        return self

    def getvalue(self, value):
        """returns a value, evaluating strings as neccessary"""
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            return sparse.stringeval(value)
        else:
            return value

    def next(self):
        lentokens = len(self.tokens)
        while self.tokenpos < lentokens and self.tokens[self.tokenpos] == "\n":
            self.tokenpos += 1
        if self.tokenpos >= lentokens:
            raise StopIteration()
        thistokens = []
        while self.tokenpos < lentokens and self.tokens[self.tokenpos] != "\n":
            thistokens.append(self.tokens[self.tokenpos])
            self.tokenpos += 1
        while self.tokenpos < lentokens and self.tokens[self.tokenpos] == "\n":
            self.tokenpos += 1
        fields = []
        # patch together fields since we can have quotes inside a field
        currentfield = ''
        fieldparts = 0
        for token in thistokens:
            if token == ',':
                # a field is only quoted if the whole thing is quoted
                if fieldparts == 1:
                    currentfield = self.getvalue(currentfield)
                fields.append(currentfield)
                currentfield = ''
                fieldparts = 0
            else:
                currentfield += token
                fieldparts += 1
        # things after the last comma...
        if fieldparts:
            if fieldparts == 1:
                currentfield = self.getvalue(currentfield)
            fields.append(currentfield)
        values = {}
        for fieldnum in range(len(self.fieldnames)):
            if fieldnum >= len(fields):
                values[self.fieldnames[fieldnum]] = ""
            else:
                values[self.fieldnames[fieldnum]] = fields[fieldnum]
        return values

csv.register_dialect('default', delimiter=',', doublequote=True, escapechar='\\', lineterminator='\r\n',
                     quotechar = '"', quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)

def from_unicode(text, encoding='utf-8'):
    if isinstance(text, unicode):
        return text.encode(encoding)
    return text

def to_unicode(text, encoding='utf-8'):
    if isinstance(text, unicode):
        return text
    return text.decode(encoding)

class csvunit(base.TranslationUnit):
    spreadsheetescapes = [("+", "\\+"), ("-", "\\-"), ("=", "\\="), ("'", "\\'")]

    def __init__(self, source=None):
        super(csvunit, self).__init__(source)
        self.location = ""
        self.source = source or ""
        self.target = ""
        self.id = ""
        self.fuzzy = False
        self.developer_comments = ""
        self.translator_comments = ""
        self.context = ""

    def getid(self):
        if self.id:
            return self.id

        result  = self.source
        context = self.context
        if context:
            result = u"%s\04%s" % (context, result)

        return result

    def setid(self, value):
        self.id = value

    def getlocations(self):
        #FIXME: do we need to support more than one location
        return [self.location]

    def addlocation(self, location):
        self.location = location

    def getcontext(self):
        return self.context

    def setcontext(self, value):
        self.context = value

    def getnotes(self, origin=None):
        if origin is None:
            result = self.translator_comments
            if self.developer_comments:
                if result:
                    result += '\n' + self.developer_comments
                else:
                    result = self.developer_comments
            return result
        elif origin == "translator":
            return self.translator_comments
        elif origin in ('programmer', 'developer', 'source code'):
            return self.developer_comments
        else:
            raise ValueError("Comment type not valid")

    def addnote(self, text, origin=None, position="append"):
        if origin in ('programmer', 'developer', 'source code'):
            if position == 'append' and self.developer_comments:
                self.developer_comments += '\n' + text
            elif position == 'prepend' and self.developer_comments:
                self.developer_comments = text + '\n' +  self.developer_comments
            else:
                self.developer_comments = text
        else:
            if position == 'append' and self.translator_comments:
                self.translator_comments += '\n' + text
            elif position == 'prepend' and self.translator_comments:
                self.translator_comments = self.translator_comments + '\n' + text
            else:
                self.translator_comments = text

    def removenotes(self):
        self.translator_comments = u''

    def isfuzzy(self):
        return self.fuzzy

    def markfuzzy(self, value=True):
        self.fuzzy = value

    def isheader(self):
        for key, value in self.todict().iteritems():
            if key != value:
                return False
        return True

    def add_spreadsheet_escapes(self, source, target):
        """add common spreadsheet escapes to two strings"""
        for unescaped, escaped in self.spreadsheetescapes:
            if source.startswith(unescaped):
                source = source.replace(unescaped, escaped, 1)
            if target.startswith(unescaped):
                target = target.replace(unescaped, escaped, 1)
        return source, target

    def remove_spreadsheet_escapes(self, source, target):
        """remove common spreadsheet escapes from two strings"""
        for unescaped, escaped in self.spreadsheetescapes:
            if source.startswith(escaped):
                source = source.replace(escaped, unescaped, 1)
            if target.startswith(escaped):
                target = target.replace(escaped, unescaped, 1)
        return source, target

    def fromdict(self, cedict):
        self.source, self.target = self.remove_spreadsheet_escapes(self.source, self.target)
        for key, value in cedict.iteritems():
            rkey = fieldname_map.get(key, key)
            if value is None:
                continue
            value = to_unicode(value)
            if rkey == "id":
                self.id = value
            elif rkey == "source":
                self.source = value
            elif rkey == "target":
                self.target = value
            elif rkey == "location":
                self.location = value
            elif rkey == "fuzzy":
                if value in ('1', 'x', 'X', 'True', 'true', 'TRUE', 'Yes', 'yes', 'YES', 'Fuzzy', 'fuzzy', 'FUZZY'):
                    self.fuzzy = True
                else:
                    self.fuzzy = False

            elif rkey == "context":
                self.context = value
            elif rkey == "translator_comments":
                self.translator_comments = value
            elif rkey == "developer_comments":
                self.developer_comments = value


    def todict(self, encoding='utf-8'):
        #FIXME: use apis?
        comment, source, target = self.comment, self.source, self.target
        source, target = self.add_spreadsheet_escapes(source, target)
        output = {
            'location': from_unicode(self.location, encoding),
            'source': from_unicode(source, encoding),
            'target': from_unicode(target, encoding),
            'id': from_unicode(self.id, encoding),
            'fuzzy': str(self.fuzzy),
            'context': from_unicode(self.context, encoding),
            'translator_comments': from_unicode(self.translator_comments, encoding),
            'developer_comments': from_unicode(self.developer_comments, encoding),
            }

        return output

    def __str__(self):
        return str(self.todict())

canonical_field_names = ('location', 'source', 'target', 'id', 'fuzzy', 'context', 'translator_comments', 'developer_comments')
fieldname_map = {
    'original': 'source',
    'untranslated': 'source',
    'translated': 'target',
    'translation': 'target',
    'identified': 'id',
    'key': 'id',
    'label': 'id',
    'transaltor comments': 'translator_comments',
    'notes': 'translator_comments',
    'developer comments': 'developer_comments',
    'state': 'fuzzy',
}

def try_dialects(inputfile, fieldnames, dialect):
    #FIXME: does it verify at all if we don't actually step through the file?
    try:
        inputfile.seek(0)
        reader = csv.DictReader(inputfile, fieldnames=fieldnames, dialect=dialect)
    except csv.Error:
        try:
            inputfile.seek(0)
            reader = csv.DictReader(inputfile, fieldnames=fieldnames, dialect='default')
        except csv.Error:
            inputfile.seek(0)
            reader = csv.DictReader(inputfile, fieldnames=fieldnames, dialect='excel')
    return reader

def valid_fieldnames(fieldnames):
    """check if fieldnames are valid"""
    for fieldname in fieldnames:
        if fieldname in canonical_field_names and fieldname == 'source':
            return True
        elif fieldname in fieldname_map and fieldname_map[fieldname] == 'source':
            return True
    return False

def detect_header(sample, dialect):
    """Test if file has a header or not, also returns number of columns in first row"""
    inputfile = StringIO.StringIO(sample)
    try:
        reader = csv.reader(inputfile, dialect)
    except csv.Error:
        try:
            inputfile.seek(0)
            reader = csv.reader(inputfile, 'default')
        except csv.Error:
            inputfile.seek(0)
            reader = csv.reader(inputfile, 'excel')

    header = reader.next()
    columns = len(header)
    if valid_fieldnames(header):
        return True, columns
    return False, columns

class csvfile(base.TranslationStore):
    """This class represents a .csv file with various lines.
    The default format contains three columns: location, source, target"""
    UnitClass = csvunit
    Name = _("Comma Separated Value")
    Mimetypes = ['text/comma-separated-values', 'text/csv']
    Extensions = ["csv"]

    def __init__(self, inputfile=None, fieldnames=None):
        base.TranslationStore.__init__(self, unitclass=self.UnitClass)
        self.units = []

        if not fieldnames:
            self.fieldnames = ['location', 'source', 'target', 'id', 'fuzzy', 'context', 'translator_comments', 'developer_comments']
        else:
            if isinstance(fieldnames, basestring):
                fieldnames = [fieldname.strip() for fieldname in fieldnames.split(",")]
            self.fieldnames = fieldnames
        self.filename = getattr(inputfile, 'name', '')
        self.dialect = 'default'
        if inputfile is not None:
            csvsrc = inputfile.read()
            inputfile.close()
            self.parse(csvsrc)

    def parse(self, csvsrc):
        sniffer = csv.Sniffer()
        # FIXME: maybe we should sniff a smaller sample
        sample = csvsrc[:1024]
        if isinstance(sample, unicode):
            sample = sample.encode("utf-8")

        try:
            self.dialect = sniffer.sniff(sample)
            if not self.dialect.escapechar:
                self.dialect.escapechar = '\\'
                if self.dialect.quoting == csv.QUOTE_MINIMAL:
                    #HACKISH: most probably a default, not real detection
                    self.dialect.quoting = csv.QUOTE_ALL
                    self.dialect.doublequote = True
        except csv.Error:
            self.dialect = 'default'

        try:
            has_header, columncount = detect_header(sample, self.dialect)
            columncount = max(3, columncount)
        except csv.Error:
            has_header = False
            columncount = None

        if not has_header:
            fieldnames = self.fieldnames[:columncount]
        else:
            fieldnames = None

        inputfile = csv.StringIO(csvsrc)
        reader = try_dialects(inputfile, fieldnames, self.dialect)

        if has_header:
            self.fieldnames = reader.fieldnames
        #reader = SimpleDictReader(csvfile, fieldnames=fieldnames, dialect=dialect)
        for row in reader:
            newce = self.UnitClass()
            newce.fromdict(row)
            self.addunit(newce)

    def __str__(self):
        """convert to a string. double check that unicode is handled somehow here"""
        source = self.getoutput()
        if isinstance(source, unicode):
            return source.encode(getattr(self, "encoding", "UTF-8"))
        return source

    def getoutput(self):
        outputfile = StringIO.StringIO()
        writer = csv.DictWriter(outputfile, self.fieldnames, extrasaction='ignore', dialect=self.dialect)
        # write header
        hdict = dict(map(None, self.fieldnames, self.fieldnames))
        writer.writerow(hdict)
        for ce in self.units:
            cedict = ce.todict()
            writer.writerow(cedict)
        outputfile.seek(0)
        return "".join(outputfile.readlines())
