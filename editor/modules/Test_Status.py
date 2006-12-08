#!/usr/bin/python
# -*- coding: utf8 -*-
#

import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
from translate.tools import pocount
from translate.misc import wStringIO
from Status import *
from translate.storage import po
import unittest
import World

class TestStatus(unittest.TestCase):

    def setUp(self):
        unit = '''# aaaaa
#: kfaximage.cpp:189
#, fuzzy
msgid "Unable to open file for reading."
msgstr "unable to read file"
'''
        self.pofile = self.poparse(unit)
        units = self.pofile.units
        self.total = len(units)
        self.fuzzy = len(pocount.fuzzymessages(units))
        self.translated = len(pocount.translatedmessages(units))
        self.untranslated = self.total - self.translated
        self.status = Status(self.pofile.units)

    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        return po.pofile(dummyfile)
    
    def testAddNumFuzzy(self):
        self.status.addNumFuzzy(1)
        self.assertEqual(self.status.numFuzzy, self.fuzzy + 1)
   
    def testAddnumTranslated(self):
        self.status.addNumTranslated(2)
        self.assertEqual(self.status.numTranslated, self.translated + 2)
        
    def testGetStatus(self):
        unitstate = World.fuzzy + World.untranslated
        unit = self.pofile.units[0]
        self.assertEqual(self.status.getStatus(unit), unitstate)
    
    def testStatusString(self):
        status = self.status.statusString()
        self.assertEqual(len(status) > 0, True )
        self.assertEqual(type(status), str)
        
if __name__ == '__main__':
    unittest.main()
