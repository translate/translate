"""Tests for MDX file storage."""

from io import BytesIO

from translate.storage.mdxfile import MDXFile


class TestMDXFileParsing:
    """Test extraction of translation units from MDX files."""

    def test_plain_markdown(self):
        """Plain markdown content is extracted normally."""
        content = b"# Hello World\n\nThis is a paragraph.\n"
        store = MDXFile(inputfile=BytesIO(content))
        units = store.units
        assert len(units) == 2
        assert units[0].source == "Hello World"
        assert units[1].source == "This is a paragraph."

    def test_import_statements_preserved(self):
        """Import statements are not extracted for translation."""
        content = b"""import { Component } from './Component'
import styles from './styles.module.css'

# Title

Some content here.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Some content here." in sources
        # imports should not appear as translation units
        assert not any("import" in s for s in sources)

    def test_export_statements_preserved(self):
        """Export statements are not extracted for translation."""
        content = b"""export const meta = { title: 'My Page' }

# Title

Paragraph text.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Paragraph text." in sources
        assert not any("export" in s for s in sources)

    def test_jsx_self_closing_component(self):
        """Self-closing JSX components are preserved."""
        content = b"""# Title

<MyComponent prop="value" />

More text here.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "More text here." in sources
        assert not any("MyComponent" in s for s in sources)

    def test_jsx_block_component(self):
        """Block JSX components with children are preserved."""
        content = b"""# Title

<Tabs>
  <Tab label="First">
    Content in tab
  </Tab>
  <Tab label="Second">
    More content
  </Tab>
</Tabs>

Text after component.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Text after component." in sources
        assert not any("Tabs" in s for s in sources)
        assert not any("Content in tab" in s for s in sources)

    def test_jsx_expression_block(self):
        """JSX expression blocks are preserved."""
        content = b"""# Title

{/* This is a comment */}

Paragraph after expression.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Paragraph after expression." in sources
        assert not any("comment" in s for s in sources)

    def test_multiline_import(self):
        """Multi-line imports are properly handled."""
        content = b"""import {
  Component1,
  Component2,
  Component3
} from './components'

# Hello
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Hello" in sources
        assert not any("Component" in s for s in sources)

    def test_mdx_roundtrip(self):
        """MDX content is preserved during roundtrip."""
        content = b"""import { Alert } from './Alert'

# Welcome

This is the intro.

<Alert type="warning">
  Be careful!
</Alert>

## Next Section

More content.
"""
        store = MDXFile(inputfile=BytesIO(content))
        output = store.filesrc
        # The import and JSX should be preserved in output
        assert "import { Alert } from './Alert'" in output
        assert '<Alert type="warning">' in output
        assert "Be careful!" in output
        assert "</Alert>" in output

    def test_frontmatter_with_mdx(self):
        """Front matter is extracted along with MDX content."""
        content = b"""---
title: My Page
---

import { Component } from './Component'

# Hello

World.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        # Front matter should be extracted
        assert any("title: My Page" in s for s in sources)
        assert "Hello" in sources
        assert "World." in sources

    def test_markdown_between_components(self):
        """Markdown between JSX components is extracted."""
        content = b"""<Header />

# Introduction

First paragraph.

<Divider />

Second paragraph.

<Footer />
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Introduction" in sources
        assert "First paragraph." in sources
        assert "Second paragraph." in sources

    def test_translation_callback(self):
        """Translation callback works with MDX files."""

        def translate(text):
            translations = {
                "Hello": "Hola",
                "World": "Mundo",
            }
            return translations.get(text, text)

        content = b"""import { Box } from './Box'

# Hello

World
"""
        store = MDXFile(inputfile=BytesIO(content), callback=translate)
        output = store.filesrc
        assert "# Hola" in output
        assert "Mundo" in output
        assert "import { Box } from './Box'" in output


class TestMDXEdgeCases:
    """Edge cases in MDX JSX parsing."""

    def test_nested_same_name_components(self):
        """Nested components with same name are handled correctly."""
        content = b"""# Title

<Card>
  <Card>
    Inner
  </Card>
</Card>

After.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "After." in sources
        # None of the JSX block content should be extracted
        assert not any("Inner" in s for s in sources)
        assert not any("Card" in s for s in sources)
        # The entire nested structure must be preserved verbatim in output
        assert "<Card>\n  <Card>\n    Inner\n  </Card>\n</Card>" in store.filesrc
        # Verify the outer Card consumed both open/close (depth returned to 0)
        # by checking content after it is still present and not swallowed
        assert store.filesrc.index("After.") > store.filesrc.index("</Card>")

    def test_self_closing_inside_block(self):
        """Self-closing tags inside block components don't break depth tracking."""
        content = b"""# Title

<Layout>
  <Sidebar />
  <Main />
</Layout>

Text.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Text." in sources
        assert not any("Sidebar" in s for s in sources)
        assert "<Layout>" in store.filesrc
        assert "</Layout>" in store.filesrc

    def test_braces_in_jsx_strings(self):
        """Braces inside JSX string props don't break parsing."""
        content = b"""# Title

<Component label="value with {braces}" />

Paragraph.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Paragraph." in sources
        assert not any("Component" in s for s in sources)

    def test_multiline_jsx_expression(self):
        """Multi-line JSX expressions are protected."""
        content = b"""# Title

{items.map((item) => (
  <li key={item.id}>{item.name}</li>
))}

After list.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "After list." in sources
        assert not any("items.map" in s for s in sources)

    def test_component_with_jsx_props(self):
        """Components with JSX expression props are handled."""
        content = b"""# Title

<Button onClick={() => alert('hi')} disabled={true} />

Text.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Text." in sources
        assert not any("Button" in s for s in sources)

    def test_inline_jsx_not_on_own_line(self):
        """Inline JSX within markdown paragraphs is passed through to markdown parser."""
        content = b"""# Title

This has <em>emphasis</em> in it.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert any("emphasis" in s for s in sources)

    def test_export_default_function(self):
        """Export default with multi-line function is protected."""
        content = b"""export default function Layout({
  children
}) {
  return <div>{children}</div>
}

# Page Title
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Page Title" in sources
        assert not any("children" in s for s in sources)
        assert "export default function Layout" in store.filesrc

    def test_mixed_markdown_and_jsx(self):
        """Complex interleaving of markdown and JSX."""
        content = b"""import { Callout } from './Callout'

# Getting Started

Welcome to the tutorial.

<Callout type="tip">
  Remember this!
</Callout>

## Step 1

Do the first thing.

<CodeExample />

## Step 2

Do the second thing.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Getting Started" in sources
        assert "Welcome to the tutorial." in sources
        assert "Step 1" in sources
        assert "Do the first thing." in sources
        assert "Step 2" in sources
        assert "Do the second thing." in sources
        assert not any("Callout" in s for s in sources)
        assert not any("CodeExample" in s for s in sources)
        assert not any("import" in s for s in sources)

    def test_paragraph_starting_with_import_word(self):
        """A paragraph starting with 'import' is not treated as an import statement."""
        content = b"""# Trade

import duties have increased significantly this year.
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        assert "Trade" in sources
        assert any("import duties" in s for s in sources)

    def test_unclosed_jsx_block_does_not_swallow_remaining_content(self):
        """An unclosed JSX tag does not consume all remaining content."""
        content = b"""<Card>
  inner

# After
"""
        store = MDXFile(inputfile=BytesIO(content))
        sources = [u.source for u in store.units]
        # "After" must still be extracted despite the unclosed <Card>
        assert "After" in sources


class TestMakePlaceholder:
    """Unit tests for MDXFile._make_placeholder indentation and line-count behaviour."""

    def _store(self) -> MDXFile:
        """Return a freshly initialised (empty) store."""
        store = MDXFile()
        store._mdx_block_counter = 0
        store._mdx_blocks = {}
        return store

    def test_no_indent_single_line(self):
        """A single-line block with no indentation produces a single-line placeholder."""
        store = self._store()
        content = "<Button />"
        ph = store._make_placeholder(content)
        assert ph == "<!-- MDX_BLOCK_1 -->"
        assert "\n" not in ph

    def test_leading_spaces_preserved(self):
        """Leading spaces on the first content line are preserved after restoration."""
        store = self._store()
        content = "  <Card>\n  inner\n  </Card>"
        store._make_placeholder(content)
        key = "<!-- MDX_BLOCK_1 -->"
        # The placeholder itself does NOT carry indentation (the renderer may
        # change it); indentation is recovered from the stored content.
        restored = store._restore_mdx_blocks(key)
        assert restored.startswith("  <Card>")

    def test_leading_tab_preserved(self):
        """A leading tab on the first content line is kept after restoration."""
        store = self._store()
        content = "\t<Component />"
        store._make_placeholder(content)
        key = "<!-- MDX_BLOCK_1 -->"
        restored = store._restore_mdx_blocks(key)
        assert restored.startswith("\t<Component />")

    def test_line_count_matches_original_single_line(self):
        """A single-line block (no newlines) produces a placeholder with no trailing newlines."""
        store = self._store()
        content = "<Foo />"
        ph = store._make_placeholder(content)
        assert ph.count("\n") == 0

    def test_line_count_matches_original_multiline(self):
        """A multi-line block produces a placeholder with the same number of newlines."""
        store = self._store()
        content = "<Alert>\n  This is important.\n</Alert>"  # 2 newlines
        ph = store._make_placeholder(content)
        assert ph.count("\n") == 2

    def test_line_count_matches_four_lines(self):
        """Placeholder newline count equals the original block's newline count."""
        store = self._store()
        content = "line1\nline2\nline3\nline4"  # 3 newlines
        ph = store._make_placeholder(content)
        assert ph.count("\n") == 3

    def test_key_stored_for_restoration(self):
        """The block content is stored under the bare key (no indent)."""
        store = self._store()
        content = "<Widget prop='x' />"
        store._make_placeholder(content)
        key = "<!-- MDX_BLOCK_1 -->"
        assert key in store._mdx_blocks
        stored_content, _ = store._mdx_blocks[key]
        assert stored_content == content

    def test_counter_increments(self):
        """Each call produces a unique, sequentially numbered key."""
        store = self._store()
        ph1 = store._make_placeholder("<A />")
        ph2 = store._make_placeholder("<B />")
        assert "MDX_BLOCK_1" in ph1
        assert "MDX_BLOCK_2" in ph2

    def test_indented_block_roundtrip(self):
        """
        An indented JSX block is protected and restored without losing indentation
        and without extra blank lines being inserted (regression for the padding
        newline double-count bug).
        """
        raw = "# Title\n\n  <Card>\n    Some nested content.\n  </Card>\n\nParagraph after.\n"
        content = raw.encode()
        store = MDXFile(inputfile=BytesIO(content))
        # The serialised source must be byte-for-byte identical to the input.
        assert store.filesrc == raw
        # Normal translatable content must still be extracted.
        sources = [u.source for u in store.units]
        assert "Title" in sources
        assert "Paragraph after." in sources

    def test_multiline_indented_block_line_numbers(self):
        """
        The placeholder occupies the same number of lines as the original block,
        so the line offset of content following the block is unchanged.

        File layout (1-indexed):
            1: # Heading
            2: (blank)
            3: <Card>
            4:   Body
            5: </Card>
            6: (blank)
            7: Trailing paragraph.
        """
        content = b"# Heading\n\n<Card>\n  Body\n</Card>\n\nTrailing paragraph.\n"
        store = MDXFile(inputfile=BytesIO(content))
        # Locate the "Trailing paragraph." unit and verify its line reference.
        trailing = next(u for u in store.units if u.source == "Trailing paragraph.")
        locations = trailing.getlocations()
        assert locations, "unit must have at least one location"
        # Location format is "filename:lineno"; take the last colon-separated part.
        location_line = int(locations[0].rsplit(":", 1)[-1])
        assert location_line == 7


class TestCodeFenceBehaviour:
    """
    Tests for code-fence tracking in _protect_mdx_blocks.

    CommonMark §4.5 rules exercised here:
    - Closing fence must use the same character as the opener.
    - Closing fence must be at least as long as the opener.
    - A shorter fence of the same character does not close the block.
    - A fence of a different character does not close the block.
    - Tilde fences (~~~) are treated symmetrically to backtick fences.
    - JSX-like lines inside a fenced block are not swallowed as MDX blocks.
    """

    @staticmethod
    def _sources(content: bytes) -> list[str]:
        store = MDXFile(inputfile=BytesIO(content))
        return [u.source for u in store.units]

    def test_basic_backtick_fence_not_swallowed(self):
        """JSX inside a triple-backtick fence is not extracted as an MDX block."""
        content = b"""# Title

```jsx
<MyComponent prop="value" />
```

Text.
"""
        sources = self._sources(content)
        assert "Title" in sources
        assert "Text." in sources

    def test_basic_tilde_fence_not_swallowed(self):
        """JSX inside a triple-tilde fence is not extracted as an MDX block."""
        content = b"""# Title

~~~jsx
<MyComponent />
~~~

Text.
"""
        sources = self._sources(content)
        assert "Title" in sources
        assert "Text." in sources

    def test_four_backtick_fence_closed_by_four(self):
        """A 4-backtick opener is closed by a 4-backtick closing fence."""
        content = b"""# Heading

````js
const x = <Foo />;
````

After.
"""
        sources = self._sources(content)
        assert "Heading" in sources
        assert "After." in sources

    def test_four_backtick_fence_not_closed_by_three(self):
        """
        A 4-backtick opener is NOT closed by a 3-backtick fence (CommonMark §4.5).

        The triple-backtick line is inside the fence and the block continues
        until the real 4-backtick closer.  Content after the real closer must
        not disappear.

        Note: mistune (the underlying Markdown parser) only recognises
        triple-backtick fences, so the 4-backtick block is rendered as a
        paragraph by mistune.  The important assertion here is that our
        *protection* logic does not prematurely close the fence and thereby
        expose "After." as lost content — i.e. "After." must still be present.
        """
        content = b"""# Heading

````
```
still inside
````

After.
"""
        sources = self._sources(content)
        assert "Heading" in sources
        # "After." follows the real closing fence and must be extracted.
        assert "After." in sources

    def test_backtick_fence_not_closed_by_tilde(self):
        """A backtick fence cannot be closed by a tilde fence."""
        content = b"""# Heading

```
code
~~~

After.
"""
        # The ~~~ does not close the ``` fence; "After." is still inside the
        # fence and will not be extracted as a translation unit (it is treated
        # as literal code).  The important assertion is that "Heading" is still
        # extracted and the parser does not crash.
        sources = self._sources(content)
        assert "Heading" in sources

    def test_tilde_fence_not_closed_by_backtick(self):
        """A tilde fence cannot be closed by a backtick fence."""
        content = b"""# Heading

~~~
code
```

After.
"""
        sources = self._sources(content)
        assert "Heading" in sources

    def test_jsx_after_fence_is_protected(self):
        """JSX block appearing after a properly closed fence is still protected."""
        content = b"""# Title

```js
<Fake />
```

<Real prop="x" />

Text.
"""
        sources = self._sources(content)
        assert "Title" in sources
        assert "Text." in sources
        # The real JSX block must not leak into sources as raw markup.
        assert not any("<Real" in s for s in sources)

    def test_nested_fence_depth_not_tracked(self):
        """Fences do not nest; the first matching close ends the block."""
        content = b"""# Title

```
outer
```

After.
"""
        sources = self._sources(content)
        assert "Title" in sources
        assert "After." in sources

    def test_fence_with_info_string_closed_correctly(self):
        """Fences with an info string (e.g. ```python) are closed by a plain fence."""
        content = b"""# Title

```python
x = 1
```

After.
"""
        sources = self._sources(content)
        assert "Title" in sources
        assert "After." in sources

    def test_five_tilde_fence_not_closed_by_three(self):
        """A 5-tilde opener is not closed by a 3-tilde fence."""
        content = b"""# Heading

~~~~~
~~~
still inside
~~~~~

After.
"""
        sources = self._sources(content)
        assert "Heading" in sources
        assert "After." in sources
