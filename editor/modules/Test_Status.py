#!/usr/bin/python
# -*- coding: utf8 -*-
#

import sys
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

    def testMarkTranslated(self):
        unit = self.pofile.units[0]
        numFuzzy = self.status.numFuzzy
        numTranslated = self.status.numTranslated
        # unit is fuzzy, making it translated should change it
        self.assertEqual(unit.x_editor_state, World.fuzzy)
        self.status.markTranslated(unit, True)
        self.assertEqual(unit.x_editor_state, World.translated)
        self.assertEqual(self.status.numFuzzy, numFuzzy - 1)
        self.assertEqual(self.status.numTranslated, numTranslated + 1)
        # unit is translated, making it untranslated should change it
        self.status.markTranslated(unit, False)
        self.assertEqual(unit.x_editor_state, World.untranslated)
        self.assertEqual(self.status.numFuzzy, numFuzzy - 1)
        self.assertEqual(self.status.numTranslated, numTranslated)

    def testMarkFuzzy(self):
        unit = self.pofile.units[0]
        numFuzzy = self.status.numFuzzy
        numTranslated = self.status.numTranslated
        # unit is fuzzy, making it fuzzy again should not change it
        self.assertEqual(unit.x_editor_state, World.fuzzy)
        self.status.markFuzzy(unit, True)
        self.assertEqual(unit.x_editor_state, World.fuzzy)
        self.assertEqual(self.status.numFuzzy, numFuzzy)
        self.assertEqual(self.status.numTranslated, numTranslated)
        # setting it to not fuzzy should change it
        self.status.markFuzzy(unit, False)
        self.assertEqual(unit.x_editor_state, World.translated)
        self.assertEqual(self.status.numFuzzy, numFuzzy - 1)
        self.assertEqual(self.status.numTranslated, numTranslated + 1)
        # setting it to fuzzy again should change it back
        self.status.markFuzzy(unit, True)
        self.assertEqual(unit.x_editor_state, World.fuzzy)
        self.assertEqual(self.status.numFuzzy, numFuzzy)
        self.assertEqual(self.status.numTranslated, numTranslated)

    def testGetStatus(self):
        unitstate = World.fuzzy
        unit = self.pofile.units[0]
        self.assertEqual(self.status.getStatus(unit), unitstate)
        self.assertEqual(unit.x_editor_state, unitstate)
    
    def testStatusString(self):
        status = self.status.statusString()
        self.assertEqual(len(status) > 0, True )
        self.assertEqual(type(status), str)
        
if __name__ == '__main__':
    unittest.main()
