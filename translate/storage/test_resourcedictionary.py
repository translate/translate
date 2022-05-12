#
# Copyright 2022 Michal Čihař
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Module for testing ReosurceDictionary files."""

from translate.storage import resourcedictionary, test_monolingual


class TestResourceDictionaryUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = resourcedictionary.ResourceDictionaryUnit


class TestResourceDictionaryFile(test_monolingual.TestMonolingualStore):
    StoreClass = resourcedictionary.ResourceDictionaryFile

    def test_roundtrip(self):
        """Test that parser fails on inconsistent root name configuration"""
        xmlsource = """<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns:system="clr-namespace:System;assembly=mscorlib">
    <system:String x:Key="ApplicationNameShort">Weblate</system:String>
</ResourceDictionary>
"""
        expected = xmlsource.replace("Weblate", "Test")

        store = self.StoreClass()
        store.parse(xmlsource)
        assert len(store.units) == 1
        unit = store.units[0]
        assert unit.source == "ApplicationNameShort"
        assert unit.target == "Weblate"

        unit.target = "Test"

        expected = xmlsource.replace("Weblate", "Test")
        assert bytes(store).decode() == expected
