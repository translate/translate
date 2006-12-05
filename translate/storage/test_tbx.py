#!/usr/bin/env python

from translate.storage import tbx
from translate.storage import test_base
from translate.misc import wStringIO
from py import test

class TestTBXUnit(test_base.TestTranslationUnit):
    UnitClass = tbx.tbxunit

    def setup_method(self, method):
        self.unit = self.UnitClass("Test Source String")

    def test_markreview(self):
        assert test.raises(NotImplementedError, self.unit.markreviewneeded)

    def test_errors(self):
        """Assert the fact that geterrors() and adderror() is not (yet) implemented.
        This test needs to be removed when these methods get implemented."""
        assert test.raises(NotImplementedError, self.unit.geterrors)
        assert test.raises(NotImplementedError, self.unit.adderror, 'testname', 'Test error')


class TestTBXfile(test_base.TestTranslationStore):
	StoreClass = tbx.tbxfile
	def test_basic(self):
		tbxfile = tbx.tbxfile()
		assert tbxfile.units == []
		tbxfile.addsourceunit("Bla")
		assert len(tbxfile.units) == 1
		newfile = tbx.tbxfile.parsestring(str(tbxfile))
		print str(tbxfile)
		assert len(newfile.units) == 1
		assert newfile.units[0].source == "Bla"
		assert newfile.findunit("Bla").source == "Bla"
		assert newfile.findunit("dit") is None

	def test_source(self):
		tbxfile = tbx.tbxfile()
		tbxunit = tbxfile.addsourceunit("Concept")
		tbxunit.source = "Term"
		newfile = tbx.tbxfile.parsestring(str(tbxfile))
		print str(tbxfile)
		assert newfile.findunit("Concept") is None
		assert newfile.findunit("Term") is not None
	
	def test_target(self):
		tbxfile = tbx.tbxfile()
		tbxunit = tbxfile.addsourceunit("Concept")
		tbxunit.target = "Konsep"
		newfile = tbx.tbxfile.parsestring(str(tbxfile))
		print str(tbxfile)
		assert newfile.findunit("Concept").target == "Konsep"
		
