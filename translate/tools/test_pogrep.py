#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import po
from translate.storage import xliff
from translate.tools import pogrep
from translate.misc import wStringIO

class TestPOGrep:
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        pofile = po.pofile(dummyfile)
        return pofile

    def pogrep(self, posource, searchstring, cmdlineoptions=None):
        """helper that parses po source and passes it through a filter"""
        if cmdlineoptions is None:
            cmdlineoptions = []
        options, args = pogrep.cmdlineparser().parse_args(["xxx.po"] + cmdlineoptions)
        grepfilter = pogrep.pogrepfilter(searchstring, options.searchparts, options.ignorecase, options.useregexp, options.invertmatch, options.accelchar)
        tofile = grepfilter.filterfile(self.poparse(posource))
        print str(tofile)
        return str(tofile)

    def test_simplegrep_msgid(self):
        """grep for a string in the source"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poresult = self.pogrep(posource, "test", ["--search=msgid"])
        assert poresult == posource
        poresult = self.pogrep(posource, "rest", ["--search=msgid"])
        assert poresult == ""

    def test_simplegrep_msgstr(self):
        """grep for a string in the target"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poresult = self.pogrep(posource, "rest", ["--search=msgstr"])
        assert poresult == posource
        poresult = self.pogrep(posource, "test", ["--search=msgstr"])
        assert poresult == ""

    def test_simplegrep_source(self):
        """grep for a string in the source"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poresult = self.pogrep(posource, "test.c", ["--search=source"])
        assert poresult == posource
        poresult = self.pogrep(posource, "rest.c", ["--search=source"])
        assert poresult == ""

    def test_simplegrep_comments(self):
        """grep for a string in the comments"""
        posource = '# (review) comment\n#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poresult = self.pogrep(posource, "review", ["--search=comment"])
        assert poresult == posource
        poresult = self.pogrep(posource, "test", ["--search=comment"])
        assert poresult == ""

    def test_unicode_message_searchstring(self):
        """check that we can grep unicode messages and use unicode search strings"""
        poascii = '# comment\n#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        pounicode = '# comment\n#: test.c\nmsgid "test"\nmsgstr "rešṱ"\n'
        queryascii = 'rest'
        queryunicode = 'rešṱ'
        for source, search, expected in [(poascii, queryascii, poascii), 
                                         (poascii, queryunicode, ''),
                                         (pounicode, queryascii, ''),
                                         (pounicode, queryunicode, pounicode)]:
          print "Source:\n%s\nSearch: %s\n" % (source, search)
          poresult = self.pogrep(source, search)
          assert poresult == expected

    def test_unicode_message_regex_searchstring(self):
        """check that we can grep unicode messages and use unicode regex search strings"""
        poascii = '# comment\n#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        pounicode = '# comment\n#: test.c\nmsgid "test"\nmsgstr "rešṱ"\n'
        queryascii = 'rest'
        queryunicode = 'rešṱ'
        for source, search, expected in [(poascii, queryascii, poascii), 
                                         (poascii, queryunicode, ''),
                                         (pounicode, queryascii, ''),
                                         (pounicode, queryunicode, pounicode)]:
          print "Source:\n%s\nSearch: %s\n" % (source, search)
          poresult = self.pogrep(source, search, ["--regexp"])
          assert poresult == expected

class TestXLiffGrep:
    xliff_skeleton = '''<?xml version="1.0" ?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
  <file original="filename.po" source-language="en-US" datatype="po">
    <body>
        %s
    </body>
  </file>
</xliff>'''

    xliff_text = xliff_skeleton % '''<trans-unit>
  <source>red</source>
  <target>rooi</target>
</trans-unit>'''

    def xliff_parse(self, xliff_text):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(xliff_text)
        xliff_file = xliff.xlifffile(dummyfile)
        return xliff_file

    def xliff_grep(self, xliff_text, searchstring, cmdlineoptions=None):
        """helper that parses xliff text and passes it through a filter"""
        if cmdlineoptions is None:
            cmdlineoptions = []
        options, args = pogrep.cmdlineparser().parse_args(["xxx.xliff"] + cmdlineoptions)
        grepfilter = pogrep.pogrepfilter(searchstring, options.searchparts, options.ignorecase, options.useregexp, options.invertmatch, options.accelchar)
        tofile = grepfilter.filterfile(self.xliff_parse(xliff_text))
        return str(tofile)

    def test_simplegrep(self):
        """grep for a simple string."""
        xliff_text = self.xliff_text
        xliff_file = self.xliff_parse(xliff_text)
        xliff_result = self.xliff_parse(self.xliff_grep(xliff_text, "red"))
        assert xliff_result.units[0].getsource() == u"red"
        assert xliff_result.units[0].gettarget() == u"rooi"

        xliff_result = self.xliff_parse(self.xliff_grep(xliff_text, "unavailable string"))
        assert xliff_result.isempty()


