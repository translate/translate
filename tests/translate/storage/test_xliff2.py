from lxml import etree

from translate.misc.xml_helpers import setXMLspace
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
        output = bytes(xliff2file).decode('utf-8')
        assert 'xmlns="urn:oasis:names:tc:xliff:document:2.0"' in output
        assert 'version="2.0"' in output or "version='2.0'" in output

    def test_unit_structure(self):
        """Test the structure of units in XLIFF 2.0."""
        xliff2file = xliff2.xliff2file()
        xliff2file.addsourceunit("Test string")
        xliff2file.units[0].target = "Cadena de prueba"
        
        output = bytes(xliff2file).decode('utf-8')
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
        assert xliff2file.units[0].source == "Hello"
        assert xliff2file.units[0].target == "Bonjour"
        assert xliff2file.getsourcelanguage() == "en"
        assert xliff2file.gettargetlanguage() == "fr"
