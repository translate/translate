#!/usr/bin/env python

from translate.convert import po2ts
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po

class TestPO2TS:
    def po2ts(self, posource):
        """helper that converts po source to ts source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2ts.po2ts()
        outputts = convertor.convertfile(inputpo)
        return outputts

    def singleelement(self, storage):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(storage.units) == 1
        return storage.units[0]

    def test_simpleentity(self):
        """checks that a simple po entry definition converts properly to a ts entry"""
        minipo = r'''#: term.cpp
msgid "Term"
msgstr "asdf"'''
        tsfile = self.po2ts(minipo)
        print tsfile
        assert "term.cpp" in tsfile
        assert "Term" in tsfile
        assert "asdf" in tsfile

class TestPO2TSCommand(test_convert.TestConvertCommand, TestPO2TS):
    """Tests running actual po2ts commands on files"""
    convertmodule = po2ts

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-tTEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "-P, --pot", last=True)
