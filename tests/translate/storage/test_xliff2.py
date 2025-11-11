import pytest

from translate.storage import xliff2

from . import test_base


class TestXLIFF2Unit(test_base.TestTranslationUnit):
    UnitClass = xliff2.xliff2unit

    def test_rich_get(self):
        """Test getting rich source and target."""
        unit = self.unit
        unit.source = "Test source"
        unit.target = "Test target"

        assert str(unit.rich_source[0]) == "Test source"
        assert str(unit.rich_target[0]) == "Test target"

    def test_segment_structure(self):
        """Test that XLIFF 2.0 uses segment structure."""
        unit = self.unit
        unit.source = "Test"
        unit.target = "Prueba"

        # Check that segment element exists
        segment = unit._get_segment()
        assert segment is not None
        assert segment.tag == unit.namespaced("segment")

        # Check that source and target are within segment
        source = unit._get_source_from_segment(segment)
        target = unit._get_target_from_segment(segment)
        assert source is not None
        assert target is not None

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

    def test_id_management(self):
        """Test unit id management."""
        unit = self.unit
        unit.source = "Test"

        unit.setid("unit-1")
        assert unit.getid() == "unit-1"


class TestXLIFF2file(test_base.TestTranslationStore):
    StoreClass = xliff2.xliff2file
    skeleton = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="2.0" xmlns="urn:oasis:names:tc:xliff:document:2.0" srcLang="en">
<file id="f1">
%s
</file>
</xliff>"""

    def test_basic(self):
        """Test basic XLIFF 2.0 file operations."""
        xliff2file = xliff2.xliff2file()
        assert xliff2file.units == []
        xliff2file.addsourceunit("Hello")
        assert len(xliff2file.units) == 1
        newfile = xliff2.xliff2file.parsestring(bytes(xliff2file))
        print(bytes(xliff2file))
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Hello"
        assert newfile.findunit("Hello").source == "Hello"
        assert newfile.findunit("missing") is None

    def test_source_target(self):
        """Test source and target in XLIFF 2.0."""
        xliff2file = xliff2.xliff2file()
        xliff2file.addsourceunit("Hello")
        xliff2file.units[0].target = "Hola"

        newfile = xliff2.xliff2file.parsestring(bytes(xliff2file))
        assert newfile.units[0].source == "Hello"
        assert newfile.units[0].target == "Hola"

    def test_language_attributes(self):
        """Test language attributes in XLIFF 2.0."""
        xliff2file = xliff2.xliff2file()
        xliff2file.setsourcelanguage("en")
        xliff2file.settargetlanguage("es")

        assert xliff2file.getsourcelanguage() == "en"
        assert xliff2file.gettargetlanguage() == "es"

        # Verify it persists after serialization
        newfile = xliff2.xliff2file.parsestring(bytes(xliff2file))
        assert newfile.getsourcelanguage() == "en"
        assert newfile.gettargetlanguage() == "es"

    def test_namespace(self):
        """Test that XLIFF 2.0 namespace is correct."""
        xliff2file = xliff2.xliff2file()
        assert xliff2file.namespace == "urn:oasis:names:tc:xliff:document:2.0"

        # Check the namespace in the serialized output
        output = bytes(xliff2file).decode("utf-8")
        assert 'xmlns="urn:oasis:names:tc:xliff:document:2.0"' in output
        assert 'version="2.0"' in output or "version='2.0'" in output

    def test_unit_structure(self):
        """Test the structure of units in XLIFF 2.0."""
        xliff2file = xliff2.xliff2file()
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
        xliff2file = xliff2.xliff2file()
        xliff2file.addsourceunit("Hello")
        xliff2file.addsourceunit("World")
        xliff2file.addsourceunit("Test")

        assert len(xliff2file.units) == 3
        assert xliff2file.units[0].source == "Hello"
        assert xliff2file.units[1].source == "World"
        assert xliff2file.units[2].source == "Test"

        # Verify after parsing
        newfile = xliff2.xliff2file.parsestring(bytes(xliff2file))
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
        xliff2file = xliff2.xliff2file.parsestring(xliff2_content)
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
</xliff>"""
        xliff2file = xliff2.xliff2file.parsestring(xliff2_content)

        # Should expose 3 separate units (one per segment)
        assert len(xliff2file.units) == 3

        # Check first segment
        assert xliff2file.units[0].getid() == "unit1:seg1"
        assert xliff2file.units[0].source == "First segment"
        assert xliff2file.units[0].target == "Premier segment"

        # Check second segment
        assert xliff2file.units[1].getid() == "unit1:seg2"
        assert xliff2file.units[1].source == "Second segment"
        assert xliff2file.units[1].target == "Deuxieme segment"

        # Check third segment
        assert xliff2file.units[2].getid() == "unit1:seg3"
        assert xliff2file.units[2].source == "Third segment"
        assert xliff2file.units[2].target == "Troisieme segment"

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
</xliff>"""
        xliff2file = xliff2.xliff2file.parsestring(xliff2_content)

        # Should have 4 units total (unit1=1, unit2=2, unit3=1)
        assert len(xliff2file.units) == 4

        # Check IDs are correct
        assert xliff2file.units[0].getid() == "unit1"
        assert xliff2file.units[1].getid() == "unit2:a"
        assert xliff2file.units[2].getid() == "unit2:b"
        assert xliff2file.units[3].getid() == "unit3"

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
      <segment>
        <source>Second segment without ID</source>
        <target>Deuxieme segment sans ID</target>
      </segment>
      <segment>
        <source>Third segment without ID</source>
        <target>Troisieme segment sans ID</target>
      </segment>
    </unit>
  </file>
</xliff>"""
        xliff2file = xliff2.xliff2file.parsestring(xliff2_content)

        # Should expose 3 separate units with auto-generated segment IDs
        assert len(xliff2file.units) == 3

        # Check auto-generated IDs (seg1, seg2, seg3)
        assert xliff2file.units[0].getid() == "unit1:seg1"
        assert xliff2file.units[0].source == "First segment without ID"

        assert xliff2file.units[1].getid() == "unit1:seg2"
        assert xliff2file.units[1].source == "Second segment without ID"

        assert xliff2file.units[2].getid() == "unit1:seg3"
        assert xliff2file.units[2].source == "Third segment without ID"

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

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "unit1"
        assert "here" in store.units[0].source
        assert "<1>" in store.units[0].source  # Escaped tags become part of text

        # Test modification and serialization
        store.units[0].target = "Modified text"
        serialized = bytes(store)

        # Verify modification preserved
        store2 = xliff2.xliff2file.parsestring(serialized)
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

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "1"
        assert store.units[0].source == "Welcome"
        assert store.units[0].target == "Bienvenue"

        # Test round-trip
        serialized = bytes(store)
        store2 = xliff2.xliff2file.parsestring(serialized)
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
            xliff2.xliff2file.parsestring(malformed_content)

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

        store = xliff2.xliff2file.parsestring(xliff_content)
        assert len(store.units) == 1
        assert store.units[0].getid() == "greeting"
        assert "{name}" in store.units[0].source

        # Test serialization
        serialized = bytes(store)
        store2 = xliff2.xliff2file.parsestring(serialized)
        assert "{name}" in store2.units[0].source
