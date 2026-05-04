"""Tests for PO to MDX conversion."""

from io import BytesIO

from translate.convert.po2mdx import MDXTranslator
from translate.storage import po


class TestPO2MDX:
    """Test PO to MDX translation."""

    @staticmethod
    def _make_po(units: list[tuple[str, str]]) -> po.pofile:
        """Create a PO store from (source, target) pairs."""
        store = po.pofile()
        for source, target in units:
            unit = store.addsourceunit(source)
            unit.target = target
        return store

    def test_basic_translation(self):
        """Basic MDX content is translated."""
        template = b"""import { Alert } from './Alert'

# Welcome

This is a paragraph.

<Alert type="info" />

Another paragraph.
"""
        postore = self._make_po(
            [
                ("Welcome", "Bienvenido"),
                ("This is a paragraph.", "Este es un parrafo."),
                ("Another paragraph.", "Otro parrafo."),
            ]
        )
        translator = MDXTranslator(
            postore,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "import { Alert } from './Alert'" in output
        assert "# Bienvenido" in output
        assert "Este es un parrafo." in output
        assert '<Alert type="info" />' in output
        assert "Otro parrafo." in output

    def test_jsx_block_preserved_in_translation(self):
        """JSX block components are preserved during translation."""
        template = b"""# Title

<Tabs>
  <Tab label="One">
    Tab content
  </Tab>
</Tabs>

After tabs.
"""
        postore = self._make_po(
            [
                ("Title", "Titulo"),
                ("After tabs.", "Despues de tabs."),
            ]
        )
        translator = MDXTranslator(
            postore,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "# Titulo" in output
        assert "<Tabs>" in output
        assert "</Tabs>" in output
        assert "Tab content" in output
        assert "Despues de tabs." in output

    def test_untranslated_units_use_source(self):
        """Untranslated units fall back to source text."""
        template = b"""# Hello

World.
"""
        postore = self._make_po([("Hello", "Hola")])
        translator = MDXTranslator(
            postore,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "# Hola" in output
        assert "World." in output  # untranslated, kept as source

    def test_export_preserved(self):
        """Export statements are preserved in output."""
        template = b"""export const meta = { title: 'Test' }

# Heading
"""
        postore = self._make_po([("Heading", "Encabezado")])
        translator = MDXTranslator(
            postore,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "export const meta = { title: 'Test' }" in output
        assert "# Encabezado" in output
