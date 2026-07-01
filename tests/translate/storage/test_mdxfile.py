"""Tests for the deliberately limited MDX storage contract."""

from io import BytesIO

import pytest

from translate.storage.mdxfile import MDXFile


def mdx_store(content: bytes, **kwargs) -> MDXFile:
    """Parse MDX bytes and return the storage object."""
    return MDXFile(inputfile=BytesIO(content), **kwargs)


def sources(store: MDXFile) -> list[str]:
    """Return source strings from all extracted units."""
    return [str(unit.source) for unit in store.units]


class TestSupportedSubset:
    """Extraction supported without parsing JSX or JavaScript."""

    def test_plain_markdown(self):
        store = mdx_store(b"# Hello World\n\nThis is a paragraph.\n")
        assert sources(store) == ["Hello World", "This is a paragraph."]

    def test_top_level_esm_is_opaque(self):
        content = b"""import {
  Alert,
  Button,
} from './components'
export const metadata = {title: 'Example'}

# Heading

Paragraph.
"""
        store = mdx_store(content)
        assert sources(store) == ["Heading", "Paragraph."]
        assert store.filesrc == content.decode()

    def test_default_plus_namespace_import_is_opaque(self):
        content = b"""import React, * as ReactDOM from 'react-dom'

# Heading
"""
        store = mdx_store(content)
        assert sources(store) == ["Heading"]
        assert store.filesrc == content.decode()

    def test_prose_starting_with_import_is_markdown(self):
        store = mdx_store(b"import taxes before submitting the form.\n")
        assert sources(store) == ["import taxes before submitting the form."]

    def test_self_closing_component_attribute(self):
        content = b'<Step title="Open" optional />\n'
        store = mdx_store(
            content,
            callback=lambda text: "Open translated" if text == "Open" else text,
        )
        assert sources(store) == ["Open"]
        assert store.filesrc == '<Step title="Open translated" optional />\n'
        assert store.units[0].getdocpath() == "jsx-attr[1]/Step.@title"

    def test_simple_component_children_are_isolated_markdown(self):
        content = b"""# Heading

<Callout title="Warning">
  Text with **Markdown**.

  - First line
    continued
</Callout>

After.
"""
        translations = {
            "Warning": "Warning translated",
            "Text with **Markdown**.": "Translated **Markdown**.",
            "First line continued": "Translated list item",
        }
        store = mdx_store(content, callback=lambda text: translations.get(text, text))

        assert sources(store) == [
            "Heading",
            "Warning",
            "Text with **Markdown**.",
            "First line continued",
            "After.",
        ]
        assert '<Callout title="Warning translated">' in store.filesrc
        assert "  Translated **Markdown**." in store.filesrc
        assert "  - Translated list item" in store.filesrc
        assert store.filesrc.endswith("\nAfter.\n")

    def test_simple_child_locations_and_docpaths(self):
        content = b"""# Heading

<Callout title="Open">
  Copy.
</Callout>
"""
        store = mdx_store(content)
        assert [unit.getlocations() for unit in store.units] == [
            [":1"],
            [":3"],
            [":4"],
        ]
        assert store.units[2].getdocpath() == "jsx-block[1]/p[1]"

    def test_units_follow_document_order(self):
        content = b"""# Heading

Body.

<Step title="Open" />
"""
        assert sources(mdx_store(content)) == ["Heading", "Body.", "Open"]

    def test_units_follow_document_order_after_frontmatter(self):
        content = b"""---
title: Metadata
---

# Heading

<Step title="Open" />

After.
"""
        store = mdx_store(content)
        assert sources(store) == [
            "---\ntitle: Metadata\n---\n\n",
            "Heading",
            "Open",
            "After.",
        ]

    def test_no_placeholders_is_forwarded_to_child_markdown(self):
        content = b"""<Callout>
  Read [the docs](https://example.com).
</Callout>
"""
        store = mdx_store(content, no_placeholders=True)
        assert sources(store) == ["Read [the docs](https://example.com)."]
        assert store.filesrc == content.decode()

    def test_code_option_is_forwarded_to_child_markdown(self):
        content = b"""<Callout>
  ```text
  literal code
  ```
</Callout>
"""
        assert sources(mdx_store(content, extract_code_blocks=False)) == []
        assert sources(mdx_store(content)) == ["literal code"]

    def test_component_children_can_contain_fenced_code(self):
        content = b"""<Callout title="Example">
  ```js
  function example() { return <Card />; }
  </Callout>
  ```

  After code.
</Callout>
"""
        store = mdx_store(content)
        assert sources(store) == [
            "Example",
            "function example() { return <Card />; }\n</Callout>",
            "After code.",
        ]
        assert store.filesrc == content.decode()

    def test_ellipsis_child_is_markdown(self):
        content = b"""<Callout title="Note">
  ...and then continue.
</Callout>
"""
        store = mdx_store(content)
        assert sources(store) == ["Note", "...and then continue."]
        assert store.filesrc == content.decode()

    def test_crlf_component_syntax_is_supported(self):
        content = (
            b'<Step title="Open" />\r\n\r\n'
            b'<Callout title="Warning">\r\n  Copy.\r\n</Callout>\r\n'
        )
        translations = {
            "Open": "Abrir",
            "Warning": "Aviso",
            "Copy.": "Copiar.",
        }
        store = mdx_store(content, callback=lambda text: translations.get(text, text))
        assert sources(store) == ["Open", "Warning", "Copy."]
        assert '<Step title="Abrir" />' in store.filesrc
        assert '<Callout title="Aviso">' in store.filesrc
        assert "  Copiar." in store.filesrc

    def test_simple_component_preserves_trailing_spaces(self):
        content = (
            b'<Step title="Open" />  \n\n'
            b'<Callout title="Warning">  \n'
            b"  Copy.\n"
            b"</Callout>  \n"
        )
        store = mdx_store(content)
        assert sources(store) == ["Open", "Warning", "Copy."]
        assert store.filesrc == content.decode()


class TestOpaqueSyntax:
    """Syntax outside the strict subset is never partially interpreted."""

    @pytest.mark.parametrize(
        "component",
        [
            '<Callout title="Open">Text</Callout>',
            "<Callout kind={kind}>\n  Text\n</Callout>",
            '<Callout\n  title="Open"\n>\n  Text\n</Callout>',
            '<Outer>\n  <Inner title="Open">\n    Text\n  </Inner>\n</Outer>',
            "<Outer>\n  <>\n    Text\n  </>\n</Outer>",
            "<Callout>Intro\nMore text\n</Callout>",
        ],
    )
    def test_unsupported_component_layout_is_opaque(self, component):
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(
            content,
            callback=lambda text: {
                "Open": "Changed",
                "Text": "Changed",
                "More text": "Changed",
                "After.": "After translated.",
            }.get(text, text),
        )
        assert sources(store) == ["After."]
        assert store.filesrc == f"{component}\n\nAfter translated.\n"

    def test_raw_html_children_are_opaque(self):
        component = """<Callout title="Open">
<div>
HTML child
</div>
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_nested_same_name_component_does_not_close_opaque_block_early(self):
        component = """<Callout>Intro
<Callout>Inner</Callout>
More text
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_opaque_component_stops_at_its_first_standalone_close(self):
        first = """<Callout kind={kind}>
Opaque text
</Callout>"""
        content = f"""{first}

Between.

<Callout title="Open">
  Copy.
</Callout>
""".encode()
        store = mdx_store(content)
        assert sources(store) == ["Between.", "Open", "Copy."]
        assert first in store.filesrc

    def test_standalone_same_name_nesting_stays_opaque(self):
        component = """<Callout kind={kind}>
<Callout>
Inner text
</Callout>

Outer text
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_non_simple_same_name_nesting_stays_opaque(self):
        component = """<Callout kind={outer}>
<Callout kind={inner}>
Inner text
</Callout>

Outer text
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_closing_tag_in_html_comment_does_not_end_opaque_component(self):
        component = """<Callout kind={kind}>
<!--
</Callout>
-->

Outer text
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_opaque_component_close_allows_trailing_spaces(self):
        component = """<Callout kind={kind}>
First child.

Second child.
</Callout>  """
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    @pytest.mark.parametrize("fragment", ["<>Text</>", "<>  \nText\n</>  "])
    def test_fragment_layouts_are_opaque(self, fragment):
        content = f"{fragment}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_text_ending_in_self_close_syntax_does_not_end_open_block(self):
        component = """<Callout>Text />
More text
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_closing_tag_literal_in_attribute_does_not_end_open_block(self):
        component = """<Callout marker={"</Callout>"}>
  More text
</Callout>"""
        content = f"{component}\n\nAfter.\n".encode()
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert component in store.filesrc

    def test_spread_makes_the_whole_tag_opaque(self):
        content = b'<Component {...props} title="Open" />\n'
        store = mdx_store(
            content, callback=lambda text: "Changed" if text == "Open" else text
        )
        assert sources(store) == []
        assert store.filesrc == content.decode()

    def test_expression_prop_with_arrow_does_not_hide_following_markdown(self):
        content = b"""<Component render={() => null} />

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_four_space_child_is_ambiguous_and_opaque(self):
        content = b"""<Callout>
    const value = 1
</Callout>
"""
        store = mdx_store(content, extract_code_blocks=False)
        assert sources(store) == []
        assert store.filesrc == content.decode()

    def test_component_literal_in_child_makes_block_opaque(self):
        content = b"""<Outer>
  Use `<Button>` in this example.
</Outer>
"""
        store = mdx_store(content)
        assert sources(store) == []
        assert store.filesrc == content.decode()

    def test_closing_tag_in_link_title_does_not_end_block(self):
        content = b"""<Outer>
  [link](url "</Outer>")
  Copy.
</Outer>

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_expression_paragraph_is_opaque_without_js_balancing(self):
        content = b"""Before {items.map(
item => <Card title="No" />
)}

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_soft_wrapped_expression_paragraph_stays_whole(self):
        content = b"""This paragraph
contains {an_expression}
on several lines.

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_indented_expression_continuation_stays_opaque(self):
        content = b"""Intro
  {items.map(item => item.name)}

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_component_without_blank_boundary_is_wholly_opaque(self):
        content = b"""Before.
<Step title="Open" />
After.
"""
        store = mdx_store(content)
        assert sources(store) == []
        assert store.filesrc == content.decode()


class TestMarkdownOwnership:
    """Contexts outside column-zero block JSX remain Markdown-owned."""

    def test_inline_component_attribute_is_not_separately_extracted(self):
        content = b'See <Badge label="New" /> now.\n'
        store = mdx_store(content)
        assert "New" not in sources(store)
        assert sources(store) == ["See {1} now."]
        assert store.filesrc == content.decode()

    def test_component_literal_in_code_span_keeps_surrounding_prose(self):
        content = b"Use `<Callout>` to show text.\n"
        store = mdx_store(content)
        assert sources(store) == ["Use `<Callout>` to show text."]
        assert store.filesrc == content.decode()

    def test_one_line_raw_html_keeps_markdown_extraction(self):
        content = b"<span>Translatable</span>\n"
        store = mdx_store(content)
        assert sources(store) == ["Translatable"]
        assert store.filesrc == content.decode()

    def test_reference_metadata_is_not_scanned_as_jsx(self):
        content = b'[ref]: /url "<Title>"\n'
        store = mdx_store(content)
        assert sources(store) == ["ref", "<Title>"]
        assert store.filesrc == content.decode()

    def test_fenced_code_is_not_scanned(self):
        content = b"""````jsx
<Card title="No" />
```
````

<Step title="Open" />
"""
        store = mdx_store(content, extract_code_blocks=False)
        assert sources(store) == ["Open"]
        assert '<Card title="No" />' in store.filesrc

    def test_indented_code_is_not_scanned(self):
        content = b'    <Button label="Save" />\n'
        store = mdx_store(content, extract_code_blocks=False)
        assert sources(store) == []
        assert store.filesrc == content.decode()

    def test_large_indented_code_block_is_processed_linearly(self):
        content = ("    const value = 1\n" * 10_000).encode()
        store = mdx_store(content, extract_code_blocks=False)
        assert sources(store) == []
        assert store.filesrc == content.decode()


class TestOpaqueRegions:
    """Regions Markdown or MDX defines as opaque are not pre-scanned."""

    def test_multiline_html_comment(self):
        content = b"""<!--
<Card title="No" />
-->

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_script_block_stays_opaque_across_blank_lines(self):
        content = b"""<script>

<Card title="No" />
</script>

<Step title="Open" />
"""
        store = mdx_store(content)
        assert sources(store) == ["Open"]
        assert store.filesrc == content.decode()

    def test_translate_off_control_is_exact_and_opaque(self):
        content = b"""<!-- translate:off -->
<Card title="No" />
<!-- translate:on -->

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()

    def test_translate_off_words_are_normal_prose(self):
        content = b"The literal text translate:off is documented here.\n"
        assert sources(mdx_store(content)) == [
            "The literal text translate:off is documented here."
        ]

    def test_frontmatter_is_not_preprocessed(self):
        content = b"""---
body: |
  <Card title="No">
    Copy
  </Card>
---

After.
"""
        store = mdx_store(content, extract_frontmatter=False)
        assert sources(store) == ["After."]
        assert store.filesrc == content.decode()


class TestAttributeSerialization:
    """Simple string attributes serialize without changing JSX syntax."""

    def test_delimiter_quotes_use_entities(self):
        content = b"<Comp title=\"Say\" note='It' />\n"
        store = mdx_store(
            content,
            callback=lambda text: {
                "Say": 'Say "hello"',
                "It": "It's ready",
            }.get(text, text),
        )
        assert store.filesrc == (
            "<Comp title=\"Say &quot;hello&quot;\" note='It&apos;s ready' />\n"
        )

    def test_less_than_in_translation_uses_entity(self):
        content = b'<Comp title="Small" />\n'
        store = mdx_store(
            content,
            callback=lambda text: "Small < medium" if text == "Small" else text,
        )
        assert store.filesrc == '<Comp title="Small &lt; medium" />\n'

    def test_backslashes_round_trip_and_terminal_one_is_doubled(self):
        content = b'<Comp path="C:\\tmp" title="Ends" />\n'
        store = mdx_store(
            content,
            callback=lambda text: "Ends\\" if text == "Ends" else text,
        )
        assert store.filesrc == '<Comp path="C:\\tmp" title="Ends\\\\" />\n'

    def test_untranslated_terminal_backslash_is_preserved(self):
        content = b'<Comp title="Ends\\" />\n'
        store = mdx_store(content)
        assert sources(store) == ["Ends\\"]
        assert store.filesrc == content.decode()

    def test_empty_attributes_keep_docpath_positions_stable(self):
        content = b'<Comp first="" second="Value" />\n'
        store = mdx_store(content)
        assert sources(store) == ["Value"]
        assert store.units[0].getdocpath() == "jsx-attr[2]/Comp.@second"

    def test_source_escaped_quote_is_outside_supported_subset(self):
        content = b'<Comp title="Say \\"hello\\"" />\n'
        store = mdx_store(content)
        assert sources(store) == []
        assert store.filesrc == content.decode()


class TestPlaceholders:
    """Opaque placeholders do not leak or collide with source content."""

    def test_placeholder_prefix_avoids_source_collision(self):
        content = b"""<!-- MDX_BLOCK_1 -->

<Step title="Open" />
"""
        store = mdx_store(content)
        assert sources(store) == ["Open"]
        assert store.filesrc == content.decode()

    def test_no_placeholder_leaks_to_units(self):
        content = b"""<Callout>Text</Callout>

After.
"""
        store = mdx_store(content)
        assert sources(store) == ["After."]
        assert not any("MDX_BLOCK" in source for source in sources(store))
