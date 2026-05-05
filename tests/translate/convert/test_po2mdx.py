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

    def test_multiline_import_preserved(self):
        """Multi-line import statements are preserved in output."""
        template = b"""import {
  Alert,
  Button,
} from './components'

# Title

Text.
"""
        postore = self._make_po(
            [("Title", "Titel"), ("Text.", "Text.")]  # codespell:ignore
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
        assert "import {" in output
        assert "Alert," in output
        assert "} from './components'" in output
        assert "# Titel" in output  # codespell:ignore

    def test_jsx_expression_block_preserved(self):
        """Standalone JSX expression blocks are preserved."""
        template = b"""# Title

{someVariable}

Text.
"""
        postore = self._make_po([("Title", "Titulo"), ("Text.", "Texto.")])
        translator = MDXTranslator(
            postore,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "{someVariable}" in output
        assert "# Titulo" in output
        assert "Texto." in output

    def test_fuzzy_unit_skipped_without_flag(self):
        """Fuzzy units are not used when includefuzzy=False."""
        template = b"""# Hello

World.
"""
        store = po.pofile()
        unit = store.addsourceunit("Hello")
        unit.target = "Hola"
        unit.markfuzzy(True)
        unit2 = store.addsourceunit("World.")
        unit2.target = "Mundo."

        translator = MDXTranslator(
            store,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        # Fuzzy unit falls back to source
        assert "# Hello" in output
        assert "Mundo." in output

    def test_fuzzy_unit_used_with_flag(self):
        """Fuzzy units are used when includefuzzy=True."""
        template = b"""# Hello

World.
"""
        store = po.pofile()
        unit = store.addsourceunit("Hello")
        unit.target = "Hola"
        unit.markfuzzy(True)
        unit2 = store.addsourceunit("World.")
        unit2.target = "Mundo."

        translator = MDXTranslator(
            store,
            includefuzzy=True,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "# Hola" in output
        assert "Mundo." in output

    def test_complex_file(self):
        """A realistic complex MDX file is correctly translated end-to-end."""
        template = b"""\
---
title: Getting Started
sidebar_position: 1
---

import { Callout, Steps } from '@docs/components'
import DocImage from './assets/screenshot.png'

export const toc = [{ value: 'Installation', id: 'installation', level: 2 }]

# Getting Started

Welcome to the **documentation**. Follow the steps below to get up and running.

<Callout type="warning">
  Make sure you have Node.js 18 or later installed before proceeding.
</Callout>

## Installation

<Steps>
  <Steps.Step>

Install the package:

```bash
npm install my-package
```

  </Steps.Step>
  <Steps.Step>

Configure your project by editing `my-package.config.js`:

  </Steps.Step>
</Steps>

{toc.map(item => <a key={item.id} href={`#${item.id}`}>{item.value}</a>)}

For more details, see the [API reference](/api).
"""
        postore = self._make_po(
            [
                ("Getting Started", "Erste Schritte"),
                (
                    "Welcome to the **documentation**. Follow the steps below to get up and running.",
                    "Willkommen in der **Dokumentation**. Folge den Schritten, um loszulegen.",
                ),
                ("Installation", "Installation"),
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

        # Translated prose appears
        assert "# Erste Schritte" in output
        assert "Willkommen in der **Dokumentation**" in output
        assert "## Installation" in output
        # Prose inside <Steps> is not translated (whole block is a JSX placeholder)
        assert "Install the package:" in output
        assert "Configure your project" in output

        # MDX structure is preserved verbatim
        assert "import { Callout, Steps } from '@docs/components'" in output
        assert "import DocImage from './assets/screenshot.png'" in output
        assert "export const toc" in output
        assert '<Callout type="warning">' in output
        assert "</Callout>" in output
        assert "<Steps>" in output
        assert "</Steps>" in output
        assert "toc.map" in output
        assert "npm install my-package" in output

    def test_no_placeholders_mode(self):
        """no_placeholders mode preserves inline content verbatim."""
        template = b"""# Title

Check [the docs](https://example.com) for details.
"""
        postore = self._make_po(
            [
                ("Title", "Titel"),  # codespell:ignore
                (
                    "Check [the docs](https://example.com) for details.",
                    "Bitte [die Docs](https://example.com) prüfen.",
                ),
            ]
        )
        translator = MDXTranslator(
            postore,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
            no_placeholders=True,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        output = outputfile.getvalue().decode()
        assert "Bitte" in output
        assert "Docs" in output
