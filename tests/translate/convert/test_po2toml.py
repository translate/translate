from io import BytesIO

import pytest

from translate.convert import po2toml
from translate.storage import toml


class TestPO2TOML:
    TargetStoreClass = toml.TOMLFile

    def po2toml(self, po_source, template_toml_source):
        """Helper to convert PO source to TOML."""
        po_file = BytesIO(po_source.encode())
        toml_file = BytesIO()
        template_file = BytesIO(template_toml_source.encode())
        result = po2toml.run_converter(
            po_file, toml_file, template_file, includefuzzy=False, outputthreshold=None
        )
        assert result == 1
        toml_file.seek(0)
        return self.TargetStoreClass(toml_file)

    def test_simple_convert(self) -> None:
        """Test converting a simple PO file to TOML."""
        template_source = """key1 = "Hello, world!"
key2 = "Goodbye, world!"
"""
        po_source = """
#: key1
msgid "Hello, world!"
msgstr "Hola, mundo!"

#: key2
msgid "Goodbye, world!"
msgstr "Adiós, mundo!"
"""
        toml_store = self.po2toml(po_source, template_source)
        assert len(toml_store.units) == 2
        assert toml_store.units[0].source == "Hola, mundo!"
        assert toml_store.units[1].source == "Adiós, mundo!"

    def test_nested_convert(self) -> None:
        """Test converting nested structures."""
        template_source = """[section]
key1 = "Nested value"

[section.subsection]
key2 = "Deeply nested"
"""
        po_source = """
#: section.key1
msgid "Nested value"
msgstr "Valor anidado"

#: section.subsection.key2
msgid "Deeply nested"
msgstr "Profundamente anidado"
"""
        toml_store = self.po2toml(po_source, template_source)
        assert len(toml_store.units) == 2
        assert toml_store.units[0].getid() == "section.key1"
        assert toml_store.units[0].source == "Valor anidado"
        assert toml_store.units[1].getid() == "section.subsection.key2"
        assert toml_store.units[1].source == "Profundamente anidado"

    def test_template_required(self) -> None:
        """Test that template is required."""
        po_source = """
#: key1
msgid "Hello"
msgstr "Hola"
"""
        with pytest.raises(ValueError):
            po2toml.run_converter(
                BytesIO(po_source.encode()), BytesIO(), None, False, None
            )

    def test_untranslated_uses_source(self) -> None:
        """Test that untranslated strings use source."""
        template_source = """key1 = "Hello"
key2 = "World"
"""
        po_source = """
#: key1
msgid "Hello"
msgstr "Hola"

#: key2
msgid "World"
msgstr ""
"""
        toml_store = self.po2toml(po_source, template_source)
        assert len(toml_store.units) == 2
        assert toml_store.units[0].source == "Hola"
        assert toml_store.units[1].source == "World"  # Uses source when not translated
