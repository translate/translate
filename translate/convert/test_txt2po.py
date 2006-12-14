#!/usr/bin/env python

from translate.convert import txt2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po

class TestTxt2PO:
    def txt2po(self, txtsource, template=None):
        """helper that converts txt source to po source without requiring files"""
        inputfile = wStringIO.StringIO(txtsource)
        convertor = txt2po.txt2po()
        outputpo = convertor.convertfile(inputfile, "", False)
        return str(outputpo)

    def singleelement(self, storage):
        """checks that the pofile contains a single non-header element, and returns it"""
        print storage.getoutput()
        assert len(storage.units) == 1
        return storage.units[0]

    def test_simple(self):
        """test the most basic txt conversion"""
        txtsource = "A simple string"
        poexpected = '''#: :1
msgid "A simple string"
msgstr ""
'''
        poresult = self.txt2po(txtsource)
        assert poresult == poexpected

class TestTxt2POCommand(test_convert.TestConvertCommand, TestTxt2PO):
    """Tests running actual txt2po commands on files"""
    convertmodule = txt2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot", last=True)
