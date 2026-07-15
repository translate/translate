"""Tests for MDX to PO conversion."""

from io import BytesIO

from translate.convert.mdx2po import MDX2POOptionParser
from translate.storage import po


class TestMDX2PO:
    """Test MDX to PO conversion."""

    @staticmethod
    def mdx2po(
        mdx_content: bytes, template_content: bytes | None = None, **kwargs
    ) -> po.pofile:
        """Helper to convert MDX bytes to a PO store."""
        inputfile = BytesIO(mdx_content)
        templatefile = (
            BytesIO(template_content) if template_content is not None else None
        )
        outputfile = BytesIO()
        parser = MDX2POOptionParser()
        parser._extract_translation_units(
            inputfile, outputfile, templatefile, "msgctxt", "single", **kwargs
        )
        outputfile.seek(0)
        return po.pofile(outputfile)

    def test_basic_extraction(self):
        """Basic MDX content is extracted to PO."""
        content = b"""import { Alert } from './Alert'

# Welcome

This is a paragraph.

<Alert title="Info">
  Important note
</Alert>

Another paragraph.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Welcome" in sources
        assert "This is a paragraph." in sources
        assert "Info" in sources
        assert "Important note" in sources
        assert "Another paragraph." in sources
        assert not any("import" in source for source in sources)
        assert not any("Alert" in source for source in sources)

    def test_explicit_heading_id_extraction(self):
        """Heading IDs are preserved outside MDX translation units."""
        store = self.mdx2po(
            b"### Anonymous learners {/* #anonymous */}\n"
            b"### Registered learners {#registered}\n"
        )

        sources = [unit.source for unit in store.units if unit.source]
        assert sources == ["Anonymous learners", "Registered learners"]

    def test_no_code_blocks(self):
        """Code blocks can be excluded from extraction."""
        content = b"""# Title

```js
const x = 1;
```

Text.
"""
        store = self.mdx2po(content, extract_code_blocks=False)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Title" in sources
        assert "Text." in sources
        assert not any("const" in source for source in sources)

    def test_no_frontmatter_option(self):
        """Front matter is not extracted when --no-frontmatter is given."""
        content = b"""---
title: My Page
---

# Heading

Paragraph.
"""
        store = self.mdx2po(content, extract_frontmatter=False)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Heading" in sources
        assert "Paragraph." in sources
        assert not any("title" in source for source in sources)

    def test_inline_jsx_attribute_in_markdown_text_is_not_extracted(self):
        """Inline MDX component attributes in Markdown are not extracted."""
        content = b'See <Badge label="New" /> now.\n'
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "New" not in sources
        assert "See {1} now." in sources

    def test_inline_jsx_expression_prop_attribute_is_not_extracted(self):
        """A brace-containing paragraph is conservatively opaque."""
        content = b'Click <Button label="Save" icon={Icon} /> now.\n'
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Save" not in sources
        assert sources == []

    def test_no_placeholders_inline_jsx_keeps_paragraph_unit(self):
        """No-placeholders mode keeps inline JSX in the paragraph unit."""
        content = b"""This is
inline <Badge label="New" />
paragraph.
"""
        store = self.mdx2po(content, no_placeholders=True)
        sources = [unit.source for unit in store.units if unit.source]
        assert "New" not in sources
        assert len(sources) == 1
        assert sources[0].replace("\n", " ") == (
            'This is inline <Badge label="New" /> paragraph.'
        )

    def test_same_line_jsx_children_are_opaque(self):
        """Same-line JSX children are preserved but not extracted."""
        content = b"<Callout>Text</Callout>\n\nAfter.\n"
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Text" not in sources
        assert "After." in sources
        assert not any("MDX_BLOCK" in source for source in sources)

    def test_inline_jsx_expression_prop_children_are_opaque(self):
        """Same-line JSX children with expression props stay opaque."""
        content = b"Text <Callout kind={kind}>Child</Callout>\n\nAfter.\n"
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Child" not in sources
        assert "After." in sources

    def test_unsupported_jsx_block_children_are_opaque(self):
        """Unsupported JSX blocks do not expose child text."""
        content = b"""<Callout>Intro
More text
</Callout>

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Intro" not in sources
        assert "More text" not in sources
        assert "After." in sources

    def test_nested_unsupported_jsx_block_children_are_opaque(self):
        """Nested same-name JSX in unsupported blocks does not close early."""
        content = b"""<Callout>Intro
<Callout>Inner</Callout>
More text
</Callout>

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Intro" not in sources
        assert "Inner" not in sources
        assert "More text" not in sources
        assert "After." in sources

    def test_marker_prefixed_same_line_jsx_is_markdown_owned(self):
        """Container-prefixed JSX is not interpreted by the MDX preprocessor."""
        content = b"""> <Callout>Text</Callout>
> After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert len(sources) == 1
        assert sources[0].replace("\n", " ") == "Text{1} After."

    def test_multiline_standalone_jsx_block_is_opaque(self):
        """Multiline opening tags are outside the supported subset."""
        content = b"""<Callout
  title="Open"
>
  Copy
</Callout>
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert sources == []

    def test_jsx_in_opaque_regions_is_not_scanned(self):
        """Comments, expressions, raw HTML, and code stay opaque to JSX attrs."""
        content = b"""<!--
<Card title="Comment" />
-->

Before {items.map(
  item => <Card title="Expression" />
)} after.

<span title="<Card title='HTML' />">hello</span>

```jsx
<Card title="Code" />
```

After.
"""
        store = self.mdx2po(content, extract_code_blocks=False)
        sources = [unit.source for unit in store.units if unit.source]
        assert "After." in sources
        assert "Comment" not in sources
        assert "Expression" not in sources
        assert "HTML" not in sources
        assert "Code" not in sources
        assert not any("MDX_BLOCK" in source for source in sources)

    def test_nested_jsx_html_comment_and_raw_html_are_not_code(self):
        """Indented comments and raw HTML inside JSX children stay opaque."""
        content = b"""<Outer>
  <Inner>
    <!--
    <Card title="Draft" />
    -->
    <span>html</span>
  </Inner>
</Outer>

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "After." in sources
        assert not any("Card" in source for source in sources)
        assert not any("span" in source for source in sources)

    def test_quoted_raw_html_blank_line_ends_block(self):
        """Container-prefixed JSX attributes are not extracted."""
        content = b"""> <span>
> html
>
> <Badge label="New" />
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "New" not in sources

    def test_jsx_in_script_after_blank_line_is_not_scanned(self):
        """Script raw HTML blocks stay opaque across blank lines."""
        content = b"""<script>

<Card title="No" />
</script>

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "No" not in sources
        assert "After." in sources

    def test_raw_html_child_does_not_keep_jsx_stack_open(self):
        """Raw HTML inside JSX does not make following ESM translatable."""
        content = b"""<Callout>
  <span>html</span>
</Callout>

import { Thing } from './thing'

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "After." in sources
        assert not any("import" in source for source in sources)

    def test_indented_code_starting_with_jsx_is_not_scanned(self):
        """Disabled indented code does not emit JSX attribute units."""
        content = b"""    <Button label="Save" />

After.
"""
        store = self.mdx2po(content, extract_code_blocks=False)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Save" not in sources
        assert "After." in sources

    def test_no_code_blocks_preserves_jsx_child_indented_code(self):
        """Indented code inside JSX children is not extracted when disabled."""
        content = b"""<Callout>
    const x = 1
</Callout>

After.
"""
        store = self.mdx2po(content, extract_code_blocks=False)
        sources = [unit.source for unit in store.units if unit.source]
        assert "const x = 1" not in sources
        assert "After." in sources

    def test_html_code_fence_does_not_affect_following_jsx(self):
        """Raw HTML-looking code fence lines do not affect following JSX."""
        content = b"""```html
<div>
```

<Alert title="Hi" />

After.
"""
        store = self.mdx2po(content, extract_code_blocks=False)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Hi" in sources
        assert "After." in sources

    def test_nested_jsx_child_fence_is_opaque(self):
        """Fenced code inside nested JSX children is not extracted."""
        content = b"""<Steps>
  <Step>
    ```js
    const x = 1
    ```
  </Step>
</Steps>
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "const x = 1" not in sources
        assert not any(source.startswith("```") for source in sources)

    def test_translate_off_skips_jsx_attributes(self):
        """translate:off regions are opaque before JSX attribute extraction."""
        content = b"""<!-- translate:off -->
<Card title="Do not translate">
  Child
</Card>
<!-- translate:on -->

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "After." in sources
        assert "Do not translate" not in sources
        assert "Child" not in sources

    def test_translate_off_text_is_not_control_comment(self):
        """Literal mentions of translate:off remain translatable."""
        content = b"""This paragraph mentions translate:off in prose.

After.
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "This paragraph mentions translate:off in prose." in sources
        assert "After." in sources

    def test_jsx_like_text_in_link_metadata_is_not_protected(self):
        """Markdown link metadata keeps JSX-looking literal text visible."""
        content = b"""[text](https://example.com "<Title>")

[<Bar>]: /url

[text][<Bar>]
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "<Title>" in sources
        assert "<Bar>" in sources
        assert not any("MDX_BLOCK" in source for source in sources)

    def test_merge_with_template(self):
        """Merging a translated MDX with a template matches by docpath."""
        template = b"""# Hello

<Step title="Open" />

World.
"""
        translated = b"""# Hallo

<Step title="Ouvrir" />

Welt.
"""
        store = self.mdx2po(translated, template)
        units = {unit.source: unit.target for unit in store.units if unit.source}
        assert units.get("Hello") == "Hallo"
        assert units.get("Open") == "Ouvrir"
        assert units.get("World.") == "Welt."

    def test_merge_simple_component_children_with_template(self):
        """Isolated child Markdown uses stable component docpaths."""
        template = b"""<Callout title="Warning">
  Source copy.
</Callout>
"""
        translated = b"""<Callout title="Achtung">
  Translated copy.
</Callout>
"""
        store = self.mdx2po(translated, template)
        units = {unit.source: unit.target for unit in store.units if unit.source}
        assert units == {
            "Warning": "Achtung",
            "Source copy.": "Translated copy.",
        }

    def test_merge_attribute_positions_across_empty_value(self):
        """Empty values still reserve their attribute docpath position."""
        template = b'<Comp first="First" second="Second" />\n'
        translated = b'<Comp first="" second="Deuxieme" />\n'
        store = self.mdx2po(translated, template)
        units = {unit.source: unit.target for unit in store.units if unit.source}
        assert units.get("Second") == "Deuxieme"

    def test_complex_file(self):
        """A realistic MDX file extracts the supported subset."""
        content = b"""\
---
title: Getting Started
sidebar_position: 1
---

import { Callout, Steps } from '@docs/components'

export const toc = [{ value: 'Installation', id: 'installation', level: 2 }]

# Getting Started

Welcome to the **documentation**.

<Callout type="warning" title="Warning">
  Make sure you have Node.js 18 or later installed before proceeding.
</Callout>

## Installation

<Steps>
  <Step title="Install">
    Install the package:
  </Step>
</Steps>

{toc.map(item => <a key={item.id}>{item.value}</a>)}

For more details, see the [API reference](/api).
"""
        store = self.mdx2po(content)
        sources = [unit.source for unit in store.units if unit.source]
        assert "Getting Started" in sources
        assert "Welcome to the **documentation**." in sources
        assert "Warning" in sources
        assert (
            "Make sure you have Node.js 18 or later installed before proceeding."
            in sources
        )
        assert "Installation" in sources
        assert "Install" not in sources
        assert "Install the package:" not in sources
        assert "For more details, see the {1} or open an {2}." not in sources
        assert not any("import" in source for source in sources)
        assert not any("export" in source for source in sources)
        assert not any("toc.map" in source for source in sources)
        assert not any("MDX_BLOCK" in source for source in sources)
