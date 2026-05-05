"""Tests for MDX to PO conversion."""

from io import BytesIO

from translate.convert.mdx2po import MDX2POOptionParser
from translate.storage import po


class TestMDX2PO:
    """Test MDX to PO conversion."""

    @staticmethod
    def mdx2po(mdx_content: bytes) -> po.pofile:
        """Helper to convert MDX bytes to a PO store."""
        inputfile = BytesIO(mdx_content)
        outputfile = BytesIO()
        parser = MDX2POOptionParser()
        parser._extract_translation_units(
            inputfile, outputfile, None, "msgctxt", "single"
        )
        outputfile.seek(0)
        return po.pofile(outputfile)

    def test_basic_extraction(self):
        """Basic MDX content is extracted to PO."""
        content = b"""import { Alert } from './Alert'

# Welcome

This is a paragraph.

<Alert type="info">
  Important note
</Alert>

Another paragraph.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert "Welcome" in sources
        assert "This is a paragraph." in sources
        assert "Another paragraph." in sources
        # JSX content should not be extracted
        assert not any("Alert" in s for s in sources)
        assert not any("import" in s for s in sources)

    def test_no_code_blocks(self):
        """Code blocks can be excluded from extraction."""
        content = b"""# Title

```js
const x = 1;
```

Text.
"""
        inputfile = BytesIO(content)
        outputfile = BytesIO()
        parser = MDX2POOptionParser()
        parser._extract_translation_units(
            inputfile, outputfile, None, "msgctxt", "single", extract_code_blocks=False
        )
        outputfile.seek(0)
        store = po.pofile(outputfile)
        sources = [u.source for u in store.units if u.source]
        assert "Title" in sources
        assert "Text." in sources
        assert not any("const" in s for s in sources)

    def test_no_placeholder_leakage(self):
        """Internal MDX_BLOCK placeholder markers must not appear in PO sources."""
        content = b"""import { Alert } from './Alert'

# Title

<Alert type="info">Important</Alert>

Paragraph.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert not any("MDX_BLOCK" in s for s in sources)

    def test_jsx_in_code_fence_is_not_protected(self):
        """JSX-like lines inside code fences are not silently removed."""
        content = b"""# Title

```jsx
<MyComponent prop="value" />
```

Text.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert "Title" in sources
        assert "Text." in sources
        # The code fence content should appear in the PO (extract_code_blocks=True)
        assert any("MyComponent" in s for s in sources)

    def test_export_statement_not_extracted(self):
        """Export statements are not extracted as translation units."""
        content = b"""export const meta = { title: 'Test', author: 'Jane' }

# Heading

Paragraph.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert "Heading" in sources
        assert "Paragraph." in sources
        assert not any("export" in s for s in sources)
        assert not any("meta" in s for s in sources)

    def test_multiline_jsx_block_not_extracted(self):
        """Multi-line JSX block components are not extracted."""
        content = b"""# Title

<Card>
  <CardHeader>Header</CardHeader>
  <CardBody>Body content</CardBody>
</Card>

Footer text.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert "Title" in sources
        assert "Footer text." in sources
        assert not any("Card" in s for s in sources)
        assert not any("Header" in s for s in sources)

    def test_self_closing_jsx_not_extracted(self):
        """Self-closing JSX tags are not extracted."""
        content = b"""# Title

<Divider />

Paragraph.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert "Title" in sources
        assert "Paragraph." in sources
        assert not any("Divider" in s for s in sources)

    def test_multiline_import_not_extracted(self):
        """Multi-line import statements are not extracted."""
        content = b"""import {
  Alert,
  Button,
} from './components'

# Title

Text.
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]
        assert "Title" in sources
        assert "Text." in sources
        assert not any("Alert" in s for s in sources)
        assert not any("import" in s for s in sources)

    def test_no_frontmatter_option(self):
        """Front matter is not extracted when --no-frontmatter is given."""
        content = b"""---
title: My Page
---

# Heading

Paragraph.
"""
        inputfile = BytesIO(content)
        outputfile = BytesIO()
        parser = MDX2POOptionParser()
        parser._extract_translation_units(
            inputfile,
            outputfile,
            None,
            "msgctxt",
            "single",
            extract_frontmatter=False,
        )
        outputfile.seek(0)
        store = po.pofile(outputfile)
        sources = [u.source for u in store.units if u.source]
        assert "Heading" in sources
        assert "Paragraph." in sources
        assert not any("title" in s for s in sources)

    def test_complex_file(self):
        """A realistic complex MDX file is correctly extracted."""
        content = b"""\
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

```js
export default {
  theme: 'light',
}
```

  </Steps.Step>
</Steps>

{toc.map(item => <a key={item.id} href={`#${item.id}`}>{item.value}</a>)}

For more details, see the [API reference](/api) or open an [issue](https://github.com/example/repo/issues).
"""
        store = self.mdx2po(content)
        sources = [u.source for u in store.units if u.source]

        # Translatable prose is extracted
        assert "Getting Started" in sources
        assert (
            "Welcome to the **documentation**. Follow the steps below to get up and running."
            in sources
        )
        assert "Installation" in sources
        # Prose inside JSX blocks is NOT extracted (the whole <Steps>…</Steps>
        # block is protected as a single placeholder)
        assert not any("Install the package" in s for s in sources)
        assert not any("Configure your project" in s for s in sources)

        # MDX-specific blocks are not extracted
        assert not any("import" in s for s in sources)
        assert not any("export" in s for s in sources)
        assert not any("Callout" in s for s in sources)
        assert not any("Steps" in s for s in sources)
        assert not any("toc.map" in s for s in sources)
        assert not any("MDX_BLOCK" in s for s in sources)

    def test_merge_with_template(self):
        """Merging a translated MDX with a template produces correctly merged PO."""
        template = b"""# Hello

World.
"""
        translated = b"""# Hallo

Welt.
"""
        inputfile = BytesIO(translated)
        templatefile = BytesIO(template)
        outputfile = BytesIO()
        parser = MDX2POOptionParser()
        parser._extract_translation_units(
            inputfile, outputfile, templatefile, "msgctxt", "single"
        )
        outputfile.seek(0)
        store = po.pofile(outputfile)
        units = {u.source: u.target for u in store.units if u.source}
        assert units.get("Hello") == "Hallo"
        assert units.get("World.") == "Welt."
