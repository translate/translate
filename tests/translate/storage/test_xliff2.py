import pytest

from translate.storage import xliff2

from . import test_base


class TestXLIFF2Unit(test_base.TestTranslationUnit):
    UnitClass = xliff2.Xliff2Unit

    def test_notes(self):
        """Test adding and retrieving notes."""
        unit = self.unit
        unit.source = "Test"

        unit.addnote("Test note 1", origin="translator")
        unit.addnote("Test note 2", origin="developer")

        # Get all notes
        all_notes = unit.getnotes()
        assert "Test note 1" in all_notes
        assert "Test note 2" in all_notes

        # Get notes by origin
        translator_notes = unit.getnotes(origin="translator")
        assert "Test note 1" in translator_notes
        assert "Test note 2" not in translator_notes

        unit.removenotes(origin="translator")
        translator_notes = unit.getnotes(origin="translator")
        assert translator_notes == ""

    def test_id_management(self):
        """Test unit id management."""
        unit = self.unit
        unit.source = "Test"

        unit.setid("unit-1")
        assert unit.getid() == "unit-1"


class TestXLIFF2file(test_base.TestTranslationStore):
    StoreClass = xliff2.Xliff2File
    skeleton = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="2.0" xmlns="urn:oasis:names:tc:xliff:document:2.0" srcLang="en">
<file id="f1">
%s
</file>
</xliff>"""

    def test_basic(self):
        """Test basic XLIFF 2.0 file operations."""
        xliff2file = xliff2.Xliff2File()
        assert xliff2file.units == []
        xliff2file.addsourceunit("Hello")
        assert len(xliff2file.units) == 1
        newfile = xliff2.Xliff2File.parsestring(bytes(xliff2file))
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Hello"
        assert newfile.findunit("Hello").source == "Hello"
        assert newfile.findunit("missing") is None

    def test_source_target(self):
        """Test source and target in XLIFF 2.0."""
        xliff2file = xliff2.Xliff2File()
        xliff2file.addsourceunit("Hello")
        xliff2file.units[0].target = "Hola"

        newfile = xliff2.Xliff2File.parsestring(bytes(xliff2file))
        assert newfile.units[0].source == "Hello"
        assert newfile.units[0].target == "Hola"

    def test_language_attributes(self):
        """Test language attributes in XLIFF 2.0."""
        xliff2file = xliff2.Xliff2File()
        xliff2file.setsourcelanguage("en")
        xliff2file.settargetlanguage("es")

        assert xliff2file.getsourcelanguage() == "en"
        assert xliff2file.gettargetlanguage() == "es"

        # Verify it persists after serialization
        newfile = xliff2.Xliff2File.parsestring(bytes(xliff2file))
        assert newfile.getsourcelanguage() == "en"
        assert newfile.gettargetlanguage() == "es"

    def test_namespace(self):
        """Test that XLIFF 2.0 namespace is correct."""
        xliff2file = xliff2.Xliff2File()
        assert xliff2file.namespace == "urn:oasis:names:tc:xliff:document:2.0"

        # Check the namespace in the serialized output
        output = bytes(xliff2file).decode("utf-8")
        assert 'xmlns="urn:oasis:names:tc:xliff:document:2.0"' in output
        assert 'version="2.0"' in output or "version='2.0'" in output

    def test_unit_structure(self):
        """Test the structure of units in XLIFF 2.0."""
        xliff2file = xliff2.Xliff2File()
        xliff2file.addsourceunit("Test string")
        xliff2file.units[0].target = "Cadena de prueba"

        output = bytes(xliff2file).decode("utf-8")
        # Should have unit element, not trans-unit
        assert "<unit" in output
        # Should have segment element
        assert "<segment" in output
        # Should not have trans-unit (that's XLIFF 1.x)
        assert "<trans-unit" not in output

    def test_multiple_units(self):
        """Test handling multiple units."""
        xliff2file = xliff2.Xliff2File()
        xliff2file.addsourceunit("Hello")
        xliff2file.addsourceunit("World")
        xliff2file.addsourceunit("Test")

        assert len(xliff2file.units) == 3
        assert xliff2file.units[0].source == "Hello"
        assert xliff2file.units[1].source == "World"
        assert xliff2file.units[2].source == "Test"

        # Verify after parsing
        newfile = xliff2.Xliff2File.parsestring(bytes(xliff2file))
        assert len(newfile.units) == 3
        assert newfile.units[0].source == "Hello"
        assert newfile.units[1].source == "World"
        assert newfile.units[2].source == "Test"

    def test_parse_xliff2(self):
        """Test parsing a minimal XLIFF 2.0 document."""
        xliff2_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
    <unit id="1">
      <segment>
        <source>Hello</source>
        <target>Bonjour</target>
      </segment>
    </unit>
  </file>
</xliff>"""
        xliff2file = xliff2.Xliff2File.parsestring(xliff2_content)
        assert len(xliff2file.units) == 1
        assert xliff2file.units[0].getid() == "1"
        assert xliff2file.units[0].source == "Hello"
        assert xliff2file.units[0].target == "Bonjour"
        assert xliff2file.getsourcelanguage() == "en"
        assert xliff2file.gettargetlanguage() == "fr"

    def test_multiple_segments_per_unit(self):
        """Test that multiple segments in a unit are exposed as separate units."""
        xliff2_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
    <unit id="unit1">
      <notes>
        <note origin="translator">Test note</note>
      </notes>
      <segment id="seg1">
        <source>First segment</source>
        <target>Premier segment</target>
      </segment>
      <segment id="seg2">
        <source>Second segment</source>
        <target>Deuxieme segment</target>
      </segment>
      <segment id="seg3">
        <source>Third segment</source>
        <target>Troisieme segment</target>
      </segment>
    </unit>
  </file>
</xliff>
"""
        xliff2file = xliff2.Xliff2File.parsestring(xliff2_content)

        # Should expose 3 separate units (one per segment)
        assert len(xliff2file.units) == 3

        # Check first segment
        assert xliff2file.units[0].getid() == "unit1::seg1"
        assert xliff2file.units[0].source == "First segment"
        assert xliff2file.units[0].target == "Premier segment"

        # Check second segment
        assert xliff2file.units[1].getid() == "unit1::seg2"
        assert xliff2file.units[1].source == "Second segment"
        assert xliff2file.units[1].target == "Deuxieme segment"

        # Check third segment
        assert xliff2file.units[2].getid() == "unit1::seg3"
        assert xliff2file.units[2].source == "Third segment"
        assert xliff2file.units[2].target == "Troisieme segment"

        assert bytes(xliff2file).decode() == xliff2_content.decode()

    def test_mixed_single_and_multiple_segments(self):
        """Test files with both single-segment and multi-segment units."""
        xliff2_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="es">
  <file id="f1">
    <unit id="unit1">
      <segment>
        <source>Single segment unit</source>
        <target>Unidad de segmento unico</target>
      </segment>
    </unit>
    <unit id="unit2">
      <segment id="a">
        <source>Multi A</source>
        <target>Multi A es</target>
      </segment>
      <segment id="b">
        <source>Multi B</source>
        <target>Multi B es</target>
      </segment>
    </unit>
    <unit id="unit3">
      <segment>
        <source>Another single</source>
        <target>Otro unico</target>
      </segment>
    </unit>
  </file>
</xliff>
"""
        xliff2file = xliff2.Xliff2File.parsestring(xliff2_content)

        # Should have 4 units total (unit1=1, unit2=2, unit3=1)
        assert len(xliff2file.units) == 4

        # Check IDs are correct
        assert xliff2file.units[0].getid() == "unit1"
        assert xliff2file.units[1].getid() == "unit2::a"
        assert xliff2file.units[2].getid() == "unit2::b"
        assert xliff2file.units[3].getid() == "unit3"

        assert bytes(xliff2file).decode() == xliff2_content.decode()

        xliff2file.units[2].target = "TEST"
        assert bytes(xliff2file).decode() == xliff2_content.decode().replace(
            "Multi B es", "TEST"
        )

    def test_segments_without_ids(self):
        """Test that segments without IDs get auto-generated IDs."""
        xliff2_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
    <unit id="unit1">
      <segment>
        <source>First segment without ID</source>
        <target>Premier segment sans ID</target>
      </segment>
      <segment state="translated">
        <source>Second segment without ID</source>
        <target>Deuxieme segment sans ID</target>
      </segment>
      <segment state="final">
        <source>Third segment without ID</source>
        <target>Troisieme segment sans ID</target>
      </segment>
    </unit>
  </file>
</xliff>
"""
        xliff2file = xliff2.Xliff2File.parsestring(xliff2_content)

        # Should expose 3 separate units with auto-generated segment IDs
        assert len(xliff2file.units) == 3

        # Check auto-generated IDs (seg1, seg2, seg3)
        assert xliff2file.units[0].getid() == "unit1::segment-1"
        assert xliff2file.units[0].source == "First segment without ID"
        assert xliff2file.units[0].istranslated()

        assert xliff2file.units[1].getid() == "unit1::segment-2"
        assert xliff2file.units[1].source == "Second segment without ID"
        assert xliff2file.units[1].istranslated()

        assert xliff2file.units[2].getid() == "unit1::segment-3"
        assert xliff2file.units[2].source == "Third segment without ID"
        assert xliff2file.units[2].istranslated()

        assert bytes(xliff2file).decode() == xliff2_content.decode()

    def test_escaped_inline_tags(self):
        """
        Test escaped inline tags in content.

        This tests escaped inline tags like &lt;1&gt;text&lt;/1&gt; in content.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="en">
  <file id="translation">
    <unit id="unit1">
      <segment>
        <source>Click &lt;1&gt;here&lt;/1&gt; to continue.</source>
        <target>Click &lt;1&gt;here&lt;/1&gt; to continue.</target>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.Xliff2File.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "unit1"
        assert "here" in store.units[0].source
        assert "<1>" in store.units[0].source  # Escaped tags become part of text

        # Test modification and serialization
        store.units[0].target = "Modified text"
        serialized = bytes(store)

        # Verify modification preserved
        store2 = xliff2.Xliff2File.parsestring(serialized)
        assert store2.units[0].target == "Modified text"

    def test_simple_source_target_pairs(self):
        """
        Test simple source/target pairs.

        This tests basic source and target text with language codes.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en-US" trgLang="fr">
  <file id="f1">
    <unit id="1">
      <segment>
        <source>Welcome</source>
        <target>Bienvenue</target>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.Xliff2File.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "1"
        assert store.units[0].source == "Welcome"
        assert store.units[0].target == "Bienvenue"

        # Test round-trip
        serialized = bytes(store)
        store2 = xliff2.Xliff2File.parsestring(serialized)
        assert store2.units[0].getid() == "1"
        assert store2.units[0].source == "Welcome"
        assert store2.units[0].target == "Bienvenue"

    def test_malformed_xml_declaration(self):
        """
        Test that malformed XML declarations are handled correctly.

        Tests that files with malformed XML declarations (missing quotes or
        spaces) fail gracefully with a clear error.
        """
        # Missing closing quote on version attribute
        malformed_content = b"""<?xml version="1.0 encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">
  <file>
    <unit id="test">
      <segment>
        <source>Test</source>
      </segment>
    </unit>
  </file>
</xliff>"""

        # This should raise an XML parsing error
        with pytest.raises(Exception) as exc_info:
            xliff2.Xliff2File.parsestring(malformed_content)

        # The error should be about XML syntax
        assert "XML" in str(exc_info.value) or "String" in str(exc_info.value)

    def test_variable_placeholders(self):
        """
        Test variable placeholders in content.

        Tests that variable placeholders like {variable} are preserved.
        """
        xliff_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en">
  <file>
    <unit id="greeting" name="greeting">
      <segment>
        <source>Hello {name}</source>
      </segment>
    </unit>
  </file>
</xliff>"""

        store = xliff2.Xliff2File.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "greeting"
        assert "{name}" in store.units[0].source

        # Test serialization
        serialized = bytes(store)
        store2 = xliff2.Xliff2File.parsestring(serialized)
        assert "{name}" in store2.units[0].source

    def test_add_unit(self):
        xliff2_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
  </file>
</xliff>
"""
        store = xliff2.Xliff2File.parsestring(xliff2_content)
        assert len(store.units) == 0
        unit = self.StoreClass.UnitClass("source")
        store.addunit(unit)
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
    <unit>
      <segment xml:space="preserve"><source>source</source>
      </segment>
    </unit>
  </file>
</xliff>
"""
        )

    def test_states(self):
        """Test that segments without IDs get auto-generated IDs."""
        xliff2_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="fr">
  <file id="f1">
    <unit id="unit1">
      <segment>
        <source>First segment without ID</source>
        <target>Premier segment sans ID</target>
      </segment>
      <segment state="translated">
        <source>Second segment without ID</source>
        <target>Deuxieme segment sans ID</target>
      </segment>
      <segment state="final">
        <source>Third segment without ID</source>
        <target>Troisieme segment sans ID</target>
      </segment>
      <segment state="initial">
        <source>Fourth segment without ID</source>
        <target>Vierieme segment sans ID</target>
      </segment>
      <segment state="reviewed">
        <source>Sixth segment without ID</source>
        <target>Seirieme segment sans ID</target>
      </segment>
    </unit>
  </file>
</xliff>
"""
        xliff2file = xliff2.Xliff2File.parsestring(xliff2_content)

        # Should expose 3 separate units with auto-generated segment IDs
        assert len(xliff2file.units) == 5

        # Check auto-generated IDs (seg1, seg2, seg3)
        assert not xliff2file.units[0].isapproved()
        assert xliff2file.units[0].istranslated()
        assert not xliff2file.units[0].isfuzzy()
        assert not xliff2file.units[1].isapproved()
        assert xliff2file.units[1].istranslated()
        assert not xliff2file.units[1].isfuzzy()
        assert xliff2file.units[2].isapproved()
        assert xliff2file.units[2].istranslated()
        assert not xliff2file.units[2].isfuzzy()
        assert not xliff2file.units[3].isapproved()
        assert not xliff2file.units[3].istranslated()
        assert xliff2file.units[3].isfuzzy()
        assert xliff2file.units[4].isapproved()
        assert xliff2file.units[4].istranslated()
        assert not xliff2file.units[4].isfuzzy()

        for unit in xliff2file.units[1:]:
            unit.markfuzzy(False)
            assert not unit.isfuzzy()
            assert unit.istranslated()
            assert not unit.isapproved()
        assert bytes(xliff2file).decode() != xliff2_content.decode()
        for unit in xliff2file.units[1:]:
            unit.markfuzzy(True)
            assert unit.isfuzzy()
            assert not unit.istranslated()
            assert not unit.isapproved()
        assert bytes(xliff2file).decode() != xliff2_content.decode()
        for unit in xliff2file.units[1:]:
            unit.marktranslated()
            assert not unit.isfuzzy()
            assert unit.istranslated()
            assert not unit.isapproved()
        assert bytes(xliff2file).decode() != xliff2_content.decode()
        for unit in xliff2file.units[1:]:
            unit.markapproved(False)
            assert not unit.isfuzzy()
            assert unit.istranslated()
            assert not unit.isapproved()
        assert bytes(xliff2file).decode() != xliff2_content.decode()
        for unit in xliff2file.units[1:]:
            unit.markapproved(True)
            assert not unit.isfuzzy()
            assert unit.istranslated()
            assert unit.isapproved()
        assert bytes(xliff2file).decode() != xliff2_content.decode()

        xliff2file.units[1].marktranslated()
        xliff2file.units[2].markapproved()
        xliff2file.units[3].markfuzzy()
        xliff2file.units[4].markapproved()

        assert bytes(xliff2file).decode() == xliff2_content.decode().replace(
            "final", "reviewed"
        )
