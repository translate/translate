#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.misc import wStringIO
from translate.storage import ini, test_monolingual


class TestINIUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = ini.iniunit

    def test_difficult_escapes(self):
        pass


class TestINIFile(test_monolingual.TestMonolingualStore):
    StoreClass = ini.inifile

    def parse_ini(self, ini_source):
        """Helper that parses INI source without requiring files."""
        dummy_file = wStringIO.StringIO(ini_source)
        ini_file = self.StoreClass(dummy_file)
        return ini_file

    def regen_ini(self, ini_source):
        """Helper that converts INI source to inifile object and back."""
        return str(self.parse_ini(ini_source))
