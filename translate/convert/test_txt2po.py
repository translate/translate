#!/usr/bin/env python

from translate.convert import txt2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import txt

class TestTxt2PO:
    def txt2po(self, txtsource, template=None):
        """helper that converts txt source to po source without requiring files"""
        inputfile = wStringIO.StringIO(txtsource)
        inputtxt = txt.TxtFile(inputfile)
        convertor = txt2po.txt2po()
        outputpo = convertor.convertfile(inputtxt)
        return outputpo

    def singleelement(self, storage):
        """checks that the pofile contains a single non-header element, and returns it"""
        print storage.getoutput()
        assert len(storage.units) == 1
        return storage.units[0]

    def test_simple(self):
        """test the most basic txt conversion"""
        txtsource = "A simple string"
        poexpected = '''msgid "A simple string"
msgstr ""
'''
        poresult = self.txt2po(txtsource)
        assert str(poresult.units[1]) == poexpected

    def test_miltiple_units(self):
        """test that we can handle txt with multiple units"""
        txtsource = """First unit
Still part of first unit

Second unit is a heading
------------------------

Third unit with blank after but no more units.

"""
        poresult = self.txt2po(txtsource)
        assert poresult.units[0].isheader()
        assert len(poresult.units) == 4

class TestTxt2POCommand(test_convert.TestConvertCommand, TestTxt2PO):
    """Tests running actual txt2po commands on files"""
    convertmodule = txt2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "--duplicates", last=True)
