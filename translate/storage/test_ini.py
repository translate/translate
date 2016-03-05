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

    def test_section_less(self):
        """Check that a section-less INI is parsed correctly."""
        ini_source = """3dArt=3D art
About=About
AdvancedGameOptions=Advanced Options
"""
        ini_file = self.parse_ini(ini_source)
        assert len(ini_file.units) == 3
        ini_unit = ini_file.units[0]
        assert ini_unit.location == "[default]3dArt"
        assert ini_unit.source == "3D art"
        ini_unit = ini_file.units[1]
        assert ini_unit.location == "[default]About"
        assert ini_unit.source == "About"
        ini_unit = ini_file.units[2]
        assert ini_unit.location == "[default]AdvancedGameOptions"
        assert ini_unit.source == "Advanced Options"

    def test_section_less_source(self):
        """checks that a simple php definition can be regenerated as source"""
        ini_source = """3dArt=3D art
About=About
AdvancedGameOptions=Advanced Options
"""
        regen_ini = self.regen_ini(ini_source)
        assert '[default]\n' + ini_source == regen_ini
