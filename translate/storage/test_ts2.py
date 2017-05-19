# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Tests for Qt Linguist storage class

Reference implementation & tests:
http://code.qt.io/cgit/qt/qttools.git/tree/tests/auto/linguist/lconvert/data
"""

from translate.storage import test_base, ts2 as ts
from translate.storage.placeables import parse, xliff


TS_NUMERUS = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1">
<context>
    <name>Dialog2</name>
    <message numerus="yes">
        <location filename="../tools/qtconfig/mainwindow.cpp" line="+202"/>
        <location filename="../somewhere-else.cpp" line="+2"/>
        <source>%n files</source>
        <translation type="unfinished">
            <numerusform></numerusform>
        </translation>
    </message>
    <message id="this_is_some_id" numerus="yes">
        <source>%n cars</source>
        <translation type="unfinished">
            <numerusform></numerusform>
        </translation>
    </message>
    <message>
        <source>Age: %1</source>
        <translation type="unfinished"></translation>
    </message>
    <message id="this_is_another_id">
        <source>func3</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
"""

xliffparsers = []
for attrname in dir(xliff):
    attr = getattr(xliff, attrname)
    if type(attr) is type and \
       attrname not in ('XLIFFPlaceable') and \
       hasattr(attr, 'parse') and \
       attr.parse is not None:
        xliffparsers.append(attr.parse)


def rich_parse(s):
    return parse(s, xliffparsers)


class TestTSUnit(test_base.TestTranslationUnit):
    UnitClass = ts.tsunit


class TestTSfile(test_base.TestTranslationStore):
    StoreClass = ts.tsfile

    def test_basic(self):
        tsfile = ts.tsfile()
        assert tsfile.units == []
        tsfile.addsourceunit("Bla")
        assert len(tsfile.units) == 1
        newfile = ts.tsfile.parsestring(bytes(tsfile))
        print(bytes(tsfile))
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Bla"
        assert newfile.findunit("Bla").source == "Bla"
        assert newfile.findunit("dit") is None

    def test_source(self):
        tsfile = ts.tsfile()
        tsunit = tsfile.addsourceunit("Concept")
        tsunit.source = "Term"
        newfile = ts.tsfile.parsestring(bytes(tsfile))
        print(bytes(tsfile))
        assert newfile.findunit("Concept") is None
        assert newfile.findunit("Term") is not None

    def test_target(self):
        tsfile = ts.tsfile()
        tsunit = tsfile.addsourceunit("Concept")
        tsunit.target = "Konsep"
        newfile = ts.tsfile.parsestring(bytes(tsfile))
        print(bytes(tsfile))
        assert newfile.findunit("Concept").target == "Konsep"

    def test_plurals(self):
        """Test basic plurals"""
        tsfile = ts.tsfile()
        tsunit = tsfile.addsourceunit("File(s)")
        tsunit.target = [u"Leêr", u"Leêrs"]
        newfile = ts.tsfile.parsestring(bytes(tsfile))
        print(bytes(tsfile))
        checkunit = newfile.findunit("File(s)")
        assert checkunit.target == [u"Leêr", u"Leêrs"]
        assert checkunit.hasplural()

    def test_language(self):
        """Check that we can get and set language and sourcelanguage
        in the header"""
        tsstr = '''<!DOCTYPE TS>
<TS version="2.0" language="fr" sourcelanguage="de">
</TS>
'''
        tsfile = ts.tsfile.parsestring(tsstr)
        assert tsfile.gettargetlanguage() == 'fr'
        assert tsfile.getsourcelanguage() == 'de'
        tsfile.settargetlanguage('pt_BR')
        assert 'pt_BR' in bytes(tsfile).decode('utf-8')
        assert tsfile.gettargetlanguage() == 'pt-br'
        # We convert en_US to en
        tsstr = '''<!DOCTYPE TS>
<TS version="2.0" language="fr" sourcelanguage="en_US">
</TS>
'''
        tsfile = ts.tsfile.parsestring(tsstr)
        assert tsfile.getsourcelanguage() == 'en'

    def test_edit(self):
        """test editing works well"""
        tsstr = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="hu">
<context>
    <name>MainWindow</name>
    <message>
        <source>ObsoleteString</source>
        <translation type="obsolete">Groepen</translation>
    </message>
    <message>
        <source>SourceString</source>
        <translation>TargetString</translation>
    </message>
</context>
</TS>
'''
        tsfile = ts.tsfile.parsestring(tsstr)
        tsfile.units[1].target = 'TestTarget'
        tsfile.units[1].markfuzzy(True)
        newtsstr = tsstr.replace(
            '>TargetString', ' type="unfinished">TestTarget'
        )
        assert newtsstr == bytes(tsfile).decode('utf-8')

    def test_locations(self):
        """test that locations work well"""
        tsstr = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="hu">
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../tools/qtconfig/mainwindow.cpp" line="+202"/>
        <source>Desktop Settings (Default)</source>
        <translation>Asztali beállítások (Alapértelmezett)</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Choose style and palette based on your desktop settings.</source>
        <translation>Stílus és paletta alapú kiválasztása az asztali beállításokban.</translation>
    </message>
    <message>
        <location />
        <source>Choose style and palette based on your desktop settings.</source>
        <translation>Stílus és paletta alapú kiválasztása az asztali beállításokban.</translation>
    </message>
    <message>
        <source>Choose style and palette based on your desktop settings.</source>
        <translation>Stílus és paletta alapú kiválasztása az asztali beállításokban.</translation>
    </message>
</context>
</TS>
'''
        tsfile = ts.tsfile.parsestring(tsstr)
        assert len(tsfile.units) == 4
        assert tsfile.units[0].getlocations() == ['../tools/qtconfig/mainwindow.cpp:+202']
        assert tsfile.units[1].getlocations() == ['+5']
        assert tsfile.units[2].getlocations() == []
        assert tsfile.units[3].getlocations() == []

    def test_merge_with_fuzzies(self):
        """test that merge with fuzzy works well"""
        tsstr1 = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="hu">
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../tools/qtconfig/mainwindow.cpp" line="+202"/>
        <source>Desktop Settings (Default)</source>
        <translation type="unfinished">Asztali beállítások (Alapértelmezett)</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Choose style and palette based on your desktop settings.</source>
        <translation>Stílus és paletta alapú kiválasztása az asztali beállításokban.</translation>
    </message>
</context>
</TS>
'''

        tsstr2 = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="hu">
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../tools/qtconfig/mainwindow.cpp" line="+202"/>
        <source>Desktop Settings (Default)</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location line="+5"/>
        <source>Choose style and palette based on your desktop settings.</source>
        <translation type="unfinished"/>
    </message>
</context>
</TS>
'''
        tsfile = ts.tsfile.parsestring(tsstr1)
        tsfile2 = ts.tsfile.parsestring(tsstr2)
        assert len(tsfile.units) == 2
        assert len(tsfile2.units) == 2

        tsfile2.units[0].merge(tsfile.units[0])  # fuzzy
        tsfile2.units[1].merge(tsfile.units[1])  # not fuzzy
        assert tsfile2.units[0].isfuzzy()
        assert not tsfile2.units[1].isfuzzy()

    def test_getid(self):
        """test that getid works well"""
        tsfile = ts.tsfile.parsestring(TS_NUMERUS)
        assert tsfile.units[0].getid() == "Dialog2%n files"
        assert tsfile.units[1].getid() == "Dialog2\nthis_is_some_id%n cars"
        assert tsfile.units[3].getid() == "Dialog2\nthis_is_another_idfunc3"

    def test_backnforth(self):
        """test that ts files are read and output properly"""
        tsfile = ts.tsfile.parsestring(TS_NUMERUS)
        assert bytes(tsfile).decode('utf-8') == TS_NUMERUS

    def test_context(self):
        tsfile = ts.tsfile.parsestring(TS_NUMERUS)
        unit = tsfile.units[0]

        contexts = [unit.getcontextname()]
        commentnode = unit.xmlelement.find(unit.namespaced("comment"))
        if commentnode is not None and commentnode.text is not None:
            contexts.append(commentnode.text)
        message_id = unit.xmlelement.get('id')
        if message_id is not None:
            contexts.append(message_id)
        context = '\n'.join(filter(None, contexts))
        assert unit.getcontext() == context
        # setting the context does nothing atm - if the unit is inserted
        unit.setcontext("FOO")
        assert unit.getcontext() == context

        # setting the context on a non-inserted unit works tho
        newunit = unit.__class__("New unit")
        assert newunit.getcontext() == ""
        newunit.setcontext("")
        assert newunit.getcontext() == ""
        newunit.setcontext("Some context")
        assert newunit.getcontext() == "Some context"
