from io import BytesIO

from translate.convert import toml2po
from translate.storage import po, toml

from . import test_convert


class TestTOML2PO:
    def toml2po(self, toml_source, template_toml_source=None):
        """Helper to convert TOML source to PO."""
        toml_file = BytesIO(toml_source.encode())
        po_file = BytesIO()
        template_file = None
        if template_toml_source:
            template_file = BytesIO(template_toml_source.encode())
        result = toml2po.run_converter(
            toml_file, po_file, template_file, pot=False, duplicatestyle="msgctxt"
        )
        assert result == 1
        po_file.seek(0)
        return po.pofile(po_file.read())

    def test_simple_convert(self):
        """Test converting a simple TOML file to PO."""
        toml_source = """key1 = "Hello, world!"
key2 = "Goodbye, world!"
"""
        po_file = self.toml2po(toml_source)
        assert len(po_file.units) == 3  # header + 2 units
        assert po_file.units[1].source == "Hello, world!"
        assert po_file.units[2].source == "Goodbye, world!"

    def test_nested_convert(self):
        """Test converting nested TOML structures."""
        toml_source = """[section]
key1 = "Nested value"

[section.subsection]
key2 = "Deeply nested"
"""
        po_file = self.toml2po(toml_source)
        assert len(po_file.units) == 3  # header + 2 units
        assert po_file.units[1].getlocations() == ["section.key1"]
        assert po_file.units[1].source == "Nested value"
        assert po_file.units[2].getlocations() == ["section.subsection.key2"]
        assert po_file.units[2].source == "Deeply nested"

    def test_comment_extraction(self):
        """Test that comments are extracted from TOML."""
        toml_source = """# This is a developer comment
key1 = "Value with comment"
"""
        po_file = self.toml2po(toml_source)
        assert len(po_file.units) == 2  # header + 1 unit
        assert "This is a developer comment" in po_file.units[1].getnotes()

    def test_merge_with_template(self):
        """Test merging two TOML files."""
        template_source = """key1 = "Hello"
key2 = "World"
"""
        translated_source = """key1 = "Hola"
key2 = "Mundo"
"""
        po_file = self.toml2po(translated_source, template_source)
        assert len(po_file.units) == 3  # header + 2 units
        assert po_file.units[1].source == "Hello"
        assert po_file.units[1].target == "Hola"
        assert po_file.units[2].source == "World"
        assert po_file.units[2].target == "Mundo"
