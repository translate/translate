#!/usr/bin/env python

from translate.convert import ts2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import ts

class TestTS2PO:
    def ts2po(self, tssource):
        converter = ts2po.ts2po()
        tsfile = wStringIO.StringIO(tssource)
        outputpo = converter.convertfile(tsfile)
        print "The generated po:"
        print str(outputpo)
        return outputpo
        
    def test_basic(self):
        """tests basic conversion"""
        tssource = '''<!DOCTYPE TS><TS>
<context>
    <name>AboutDialog</name>
    <message>
        <source>&amp;About</source>
        <translation>&amp;Giới thiệu</translation>
    </message>
</context>
</TS>
'''
        pofile = self.ts2po(tssource)
        assert len(pofile.units) == 2
        assert pofile.units[1].source == "&About"
        assert pofile.units[1].target == "&Giới thiệu"
        

class TestTS2POCommand(test_convert.TestConvertCommand, TestTS2PO):
    """Tests running actual ts2po commands on files"""
    convertmodule = ts2po

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot", last=True)
