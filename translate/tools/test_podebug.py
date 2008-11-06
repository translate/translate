# -*- coding: utf-8 -*-

from translate.tools import podebug
from translate.storage import base

class TestPODebug:

    debug = podebug.podebug()

    def test_ignore_gtk(self):
        """Test operation of GTK message ignoring"""
        unit = base.TranslationUnit("default:LTR")
        assert self.debug.ignore_gtk(unit) == True

    def test_rewrite_blank(self):
        """Test the blank rewrite function"""
        assert self.debug.rewrite_blank("Test") == ""

    def test_rewrite_en(self):
        """Test the en rewrite function"""
        assert self.debug.rewrite_en("Test") == "Test"

    def test_rewrite_xxx(self):
        """Test the xxx rewrite function"""
        assert self.debug.rewrite_xxx("Test") == "xxxTestxxx"
        assert self.debug.rewrite_xxx("Newline\n") == "xxxNewlinexxx\n"

    def test_rewrite_unicode(self):
        """Test the unicode rewrite function"""
        assert self.debug.rewrite_unicode("Test") == u"Ŧḗşŧ"
