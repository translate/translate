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
