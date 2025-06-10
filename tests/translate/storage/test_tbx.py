from translate.storage import tbx

from . import test_base


class TestTBXUnit(test_base.TestTranslationUnit):
    UnitClass = tbx.tbxunit


class TestTBXfile(test_base.TestTranslationStore):
    StoreClass = tbx.tbxfile

    def test_basic(self):
        tbxfile = tbx.tbxfile()
        assert tbxfile.units == []
        tbxfile.addsourceunit("Bla")
        assert len(tbxfile.units) == 1
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Bla"
        assert newfile.findunit("Bla").source == "Bla"
        assert newfile.findunit("dit") is None

    def test_source(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.source = "Term"
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert newfile.findunit("Concept") is None
        assert newfile.findunit("Term") is not None

    def test_target(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.target = "Konsep"
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert newfile.findunit("Concept").target == "Konsep"

    def test_setid(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.setid("testid")
        newfile = tbx.tbxfile.parsestring(bytes(tbxfile))
        print(bytes(tbxfile))
        assert newfile.findunit("Concept").getid() == "testid"

    def test_indent(self):
        tbxfile = tbx.tbxfile()
        tbxunit = tbxfile.addsourceunit("Concept")
        tbxunit.setid("testid")
        assert (
            bytes(tbxfile).decode()
            == """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX" xml:lang="en">
    <martifHeader>
        <fileDesc>
            <sourceDesc>
                <p>Translate Toolkit</p>
            </sourceDesc>
        </fileDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="testid">
                <langSet xml:lang="en"><tig><term>Concept</term></tig></langSet>
            </termEntry>
        </body>
    </text>
</martif>
"""
        )

    def test_descrip(self):
        tbxdata = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX" xml:lang="en">
    <martifHeader>
        <fileDesc>
            <sourceDesc>
                <p>Translate Toolkit</p>
            </sourceDesc>
        </fileDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="testid">
                <langSet xml:lang="en"><tig><term>Concept</term></tig></langSet>
                <descrip>Explanation</descrip>
            </termEntry>
        </body>
    </text>
</martif>
"""
        tbxfile = tbx.tbxfile.parsestring(tbxdata.encode())
        assert bytes(tbxfile).decode() == tbxdata
        assert len(tbxfile.units) == 1
        unit = tbxfile.units[0]
        assert unit.source == "Concept"
        assert unit.getnotes(origin="definition") == "Explanation"
        unit.addnote("Another explanation", origin="definition", position="replace")
        assert bytes(tbxfile).decode() == tbxdata.replace(
            "Explanation", "Another explanation"
        )

    def test_note_from(self):
        tbxdata = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif PUBLIC "ISO 12200:1999A//DTD MARTIF core (DXFcdV04)//EN" "TBXcdv04.dtd">
<martif type="TBX" xml:lang="en">
    <martifHeader>
        <fileDesc>
            <sourceDesc>
                <p>Translate Toolkit</p>
            </sourceDesc>
        </fileDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="testid">
                <langSet xml:lang="en"><tig><term>Concept</term></tig></langSet>
                <note from="translator">Translator note</note>
                <note>Other note</note>
            </termEntry>
        </body>
    </text>
</martif>
"""
        tbxfile = tbx.tbxfile.parsestring(tbxdata.encode())
        assert bytes(tbxfile).decode() == tbxdata
        assert len(tbxfile.units) == 1
        unit = tbxfile.units[0]
        assert unit.source == "Concept"
        assert unit.getnotes(origin="translator") == "Translator note"
        assert unit.getnotes(origin="dev") == ""
        assert unit.getnotes() == "Translator note\nOther note"

    def test_administrative_status_and_translation_needed(self):
        tbxdata = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">
<martif xmlns="urn:iso:std:iso:30042:ed-2" xml:lang="en" type="TBX">
    <martifHeader>
        <fileDesc>
            <sourceDesc>
                <p>Extended Metadata Bilingual TBX Parsing</p>
            </sourceDesc>
        </fileDesc>
    </martifHeader>
    <text>
        <body>
            <termEntry id="e001">
                <descrip type="definition">Superseded but still found in older manuals.</descrip>
                <descrip type="Translation needed">Yes</descrip>
                <langSet xml:lang="en">
                    <tig>
                        <term id="e001-en">data bus</term>
                        <termNote type="administrativeStatus">deprecated</termNote>
                    </tig>
                </langSet>
                <langSet xml:lang="fr">
                    <tig>
                        <term id="e001-fr">bus de données</term>
                        <termNote type="administrativeStatus">deprecatedTerm-admn-sts</termNote>
                    </tig>
                </langSet>
            </termEntry>
            <termEntry id="e002">
                <descrip type="definition">An internal code identifier not to be localized.</descrip>
                <descrip type="Translation needed">No</descrip>
                <langSet xml:lang="en">
                    <tig>
                        <term id="e002-en">SYS_ERR_406</term>
                        <note from="developer">Do not translate error codes.</note>
                    </tig>
                </langSet>
                <langSet xml:lang="fr">
                    <tig>
                        <term id="e002-fr">SYS_ERR_406</term>
                    </tig>
                </langSet>
            </termEntry>
        </body>
    </text>
</martif>
"""
        tbxfile = tbx.tbxfile.parsestring(tbxdata.encode())
        assert bytes(tbxfile).decode() == tbxdata
        assert len(tbxfile.units) == 2
        unit = tbxfile.units[0]
        assert unit.source == "data bus"
        assert unit.isobsolete()
        assert unit.istranslatable()
        assert (
            unit.getnotes(origin="definition")
            == "Superseded but still found in older manuals."
        )
        unit = tbxfile.units[1]
        assert unit.source == "SYS_ERR_406"
        assert not unit.isobsolete()
        assert not unit.istranslatable()
