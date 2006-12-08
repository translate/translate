from translate.storage import factory
import sys
import os.path
sys.path.append(os.path.join(sys.path[0], ".."))
from Status import *
import unittest
import World

class TestStatus(unittest.TestCase):

    def setUp(self):
        self.store = factory.getobject("../example/webarchiver.po")
        self.status = Status(self.store.units)
        self.total = self.status.numTotal
        self.fuzzy = self.status.numFuzzy
        self.translated = self.status.numTranslated
        self.untranslated = self.status.numUntranslated
    
    def testAddNumFuzzy(self):
        self.status.addNumFuzzy(1)
        self.assertEqual(self.status.numFuzzy, self.fuzzy + 1)
    
    def testAddnumTranslated(self):
        self.status.addNumTranslated(2)
        self.assertEqual(self.status.numTranslated, self.translated + 2)
    
    def testGetStatus(self):
        unitstate = 0
        unit = self.store.units[1]
        if unit.isfuzzy():
            unitstate += World.fuzzy
        if unit.istranslated():
            unitstate += World.translated
        else:
            unitstate += World.untranslated
        self.assertEqual(self.status.getStatus(unit), unitstate)
    
    def testStatusString(self):
        status = "Total: " + str(self.total)  +  "  |  Fuzzy: " +  str(self.fuzzy) + \
                "  |  Translated: " +  str(self.translated) + "  |  Untranslated: " + str(self.untranslated)
        self.assertEqual(self.status.statusString(), status)
        
if __name__ == '__main__':
    unittest.main()
