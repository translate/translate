"""Tests for PO to MDX conversion."""

from io import BytesIO

from translate.convert.po2mdx import MDXTranslator
from translate.storage import po
from translate.storage.mdxfile import MDXFile


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

    @classmethod
    def translate(
        cls, template: bytes, units: list[tuple[str, str]], **kwargs
    ) -> bytes:
        """Translate MDX bytes with a PO store."""
        translator = MDXTranslator(
            cls._make_po(units),
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
            **kwargs,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(template), outputfile)
        return outputfile.getvalue()

    def test_basic_translation(self):
        """Basic MDX content is translated."""
        template = b"""import { Alert } from './Alert'

# Welcome

This is a paragraph.

<Alert type="info" />

Another paragraph.
"""
        output = self.translate(
            template,
            [
                ("Welcome", "Welcome translated"),
                ("This is a paragraph.", "Paragraph translated."),
                ("Another paragraph.", "Another paragraph translated."),
            ],
        ).decode()
        assert "import { Alert } from './Alert'" in output
        assert "# Welcome translated" in output
        assert "Paragraph translated." in output
        assert '<Alert type="info" />' in output
        assert "Another paragraph translated." in output

    def test_standalone_jsx_block_children_and_attrs_translate(self):
        """Standalone JSX tag attrs and child Markdown are translated."""
        template = b"""# Title

<Tab label="One">
  Tab content
</Tab>

After tabs.
"""
        output = self.translate(
            template,
            [
                ("Title", "Title translated"),
                ("One", "One translated"),
                ("Tab content", "Tab content translated"),
                ("After tabs.", "After tabs translated."),
            ],
        ).decode()
        assert "# Title translated" in output
        assert '<Tab label="One translated">' in output
        assert "Tab content translated" in output
        assert "</Tab>" in output
        assert "After tabs translated." in output

    def test_inline_jsx_attribute_translation_is_not_applied(self):
        """Inline MDX component attributes in Markdown are not translated."""
        template = b'See <Badge label="New" /> now.\n'
        output = self.translate(template, [("New", "New translated")])
        assert output == template

    def test_inline_jsx_expression_prop_attribute_translation_is_not_applied(self):
        """Expression props do not make inline JSX attributes translatable."""
        template = b'Click <Button label="Save" icon={Icon} /> now.\n'
        output = self.translate(template, [("Save", "Save translated")])
        assert output == template

    def test_no_placeholders_inline_jsx_uses_paragraph_lookup(self):
        """Soft-wrapped inline JSX keeps no-placeholders paragraph context."""
        template = b"""This is
inline <Badge label="New" />
paragraph.
"""
        source = (
            MDXFile(inputfile=BytesIO(template), no_placeholders=True).units[0].source
        )
        output = self.translate(
            template,
            [
                (
                    source,
                    'Translated <Badge label="New translated" /> paragraph.',
                )
            ],
            no_placeholders=True,
        )
        assert output == b'Translated <Badge label="New translated" /> paragraph.\n'

    def test_no_placeholders_inline_jsx_attribute_fallback_is_not_applied(self):
        """Attr-only translations do not apply to inline JSX."""
        template = b'See <Badge label="New" /> now.\n'
        output = self.translate(
            template,
            [("New", "New translated")],
            no_placeholders=True,
        )
        assert output == template

    def test_no_placeholders_inline_code_is_not_attr_fallback(self):
        """Attr-only translations do not rewrite JSX-looking inline code."""
        template = b'Use `<Badge label="New" />` literally.\n'
        output = self.translate(
            template,
            [("New", "New translated")],
            no_placeholders=True,
        )
        assert output == template

    def test_no_placeholders_raw_html_is_not_attr_fallback(self):
        """Attr-only translations do not rewrite JSX-looking raw HTML."""
        template = b"Text <span title=\"<Card title='No' />\">hello</span>\n"
        output = self.translate(
            template,
            [("No", "No translated")],
            no_placeholders=True,
        )
        assert output == template

    def test_same_line_jsx_children_are_opaque(self):
        """Same-line JSX child text is not translated by the limited parser."""
        template = b"<Callout>Text</Callout>\n\nAfter.\n"
        output = self.translate(
            template,
            [("Text", "Changed"), ("After.", "After translated.")],
        ).decode()
        assert "<Callout>Text</Callout>" in output
        assert "Changed" not in output
        assert "After translated." in output

    def test_inline_jsx_expression_prop_children_are_opaque(self):
        """Same-line JSX children with expression props are not translated."""
        template = b"Text <Callout kind={kind}>Child</Callout>\n\nAfter.\n"
        output = self.translate(
            template,
            [("Child", "Child translated"), ("After.", "After translated.")],
        ).decode()
        assert "Child translated" not in output
        assert "Text <Callout kind={kind}>Child</Callout>" in output
        assert "After translated." in output

    def test_nested_unsupported_jsx_block_children_are_opaque(self):
        """Nested same-name JSX in unsupported blocks is not translated."""
        template = b"""<Callout>Intro
<Callout>Inner</Callout>
More text
</Callout>

After.
"""
        output = self.translate(
            template,
            [
                ("Intro", "Intro translated"),
                ("Inner", "Inner translated"),
                ("More text", "More translated"),
                ("After.", "After translated."),
            ],
        ).decode()
        assert "Intro translated" not in output
        assert "Inner translated" not in output
        assert "More translated" not in output
        assert "More text" in output
        assert "After translated." in output

    def test_same_line_jsx_attributes_are_not_translated(self):
        """Same-line opaque JSX does not translate simple attrs."""
        template = b'<Callout title="Open">Text</Callout>\n'
        output = self.translate(template, [("Open", "Open translated")])
        assert output == template

    def test_multiline_standalone_opening_tag_is_opaque(self):
        """Multiline standalone tags are preserved without partial translation."""
        template = b"""<Callout
  title="Open"
>
  Copy
</Callout>
"""
        output = self.translate(
            template,
            [("Open", "Open translated"), ("Copy", "Copy translated")],
        ).decode()
        assert output == template.decode()

    def test_jsx_expression_block_preserved(self):
        """Standalone JSX expression blocks are preserved."""
        template = b"""# Title

{someVariable}

Text.
"""
        output = self.translate(
            template,
            [("Title", "Title translated"), ("Text.", "Text translated.")],
        ).decode()
        assert "{someVariable}" in output
        assert "# Title translated" in output
        assert "Text translated." in output

    def test_multiline_inline_expression_is_not_translated_as_jsx(self):
        """Component-looking code inside multiline inline expressions is opaque."""
        template = b"""Before {items.map(
  item => <Card title="No" />
)} after.

After.
"""
        output = self.translate(
            template,
            [("No", "No translated"), ("After.", "After translated.")],
        ).decode()
        assert '<Card title="No" />' in output
        assert "No translated" not in output
        assert "After translated." in output

    def test_translate_off_region_is_opaque(self):
        """translate:off regions are not changed by JSX preprocessing."""
        template = b"""<!-- translate:off -->
<Card title="Do not translate">
  Child
</Card>
<!-- translate:on -->

After.
"""
        output = self.translate(
            template,
            [
                ("Do not translate", "Translated"),
                ("Child", "Translated"),
                ("After.", "After translated."),
            ],
        ).decode()
        assert 'title="Do not translate"' in output
        assert "\n  Child\n" in output
        assert "After translated." in output

    def test_no_code_blocks_preserves_indented_code_with_inline_jsx(self):
        """Inline JSX inside disabled code extraction is not translated."""
        template = b"""    const button = <Button label="Save" />;

After.
"""
        output = self.translate(
            template,
            [("Save", "Save translated"), ("After.", "After translated.")],
            extract_code_blocks=False,
        )
        assert b'<Button label="Save" />' in output
        assert b"Save translated" not in output
        assert b"After translated." in output

    def test_no_code_blocks_preserves_indented_code_starting_with_jsx(self):
        """Line-start JSX inside disabled indented code is not translated."""
        template = b"""    <Button label="Save" />

After.
"""
        output = self.translate(
            template,
            [("Save", "Save translated"), ("After.", "After translated.")],
            extract_code_blocks=False,
        )
        assert b'<Button label="Save" />' in output
        assert b"Save translated" not in output
        assert b"After translated." in output

    def test_no_code_blocks_preserves_jsx_child_indented_code(self):
        """Indented code inside JSX children stays opaque when code is disabled."""
        template = b"""<Callout>
    const x = 1
</Callout>

After.
"""
        output = self.translate(
            template,
            [("const x = 1", "const y = 2"), ("After.", "After translated.")],
            extract_code_blocks=False,
        )
        assert b"\n    const x = 1\n" in output
        assert b"const y = 2" not in output
        assert b"After translated." in output

    def test_nested_jsx_child_fence_is_opaque(self):
        """Fenced code inside nested JSX children is preserved."""
        template = b"""<Steps>
  <Step>
    ```js
    const x = 1
    ```
  </Step>
</Steps>
"""
        output = self.translate(template, [("const x = 1", "const y = 2")]).decode()
        assert "const y = 2" not in output
        assert "const x = 1" in output
        assert "```js" in output

    def test_raw_html_attribute_with_jsx_like_text_is_not_translated(self):
        """JSX-looking text in raw HTML is not translated as JSX."""
        template = b"""Text <span title="<Card title='No' />">hello</span>

After.
"""
        output = self.translate(
            template,
            [("No", "No translated"), ("After.", "After translated.")],
        ).decode()
        assert "<Card title='No' />" in output
        assert "No translated" not in output
        assert "After translated." in output

    def test_nested_jsx_html_comment_and_raw_html_are_not_code(self):
        """Indented comments and raw HTML inside JSX children stay opaque."""
        template = b"""<Outer>
  <Inner>
    <!--
    <Card title="Draft" />
    -->
    <span>html</span>
  </Inner>
</Outer>

After.
"""
        output = self.translate(
            template,
            [
                ('<Card title="Draft" />', "Changed card"),
                ("<span>html</span>", "Changed span"),
                ("After.", "After translated."),
            ],
        ).decode()
        assert '    <Card title="Draft" />' in output
        assert "    <span>html</span>" in output
        assert "Changed card" not in output
        assert "Changed span" not in output
        assert "After translated." in output

    def test_script_after_blank_line_with_jsx_like_text_is_not_translated(self):
        """Script raw HTML blocks remain opaque across blank lines."""
        template = b"""<script>

<Card title="No" />
</script>

After.
"""
        output = self.translate(
            template,
            [("No", "No translated"), ("After.", "After translated.")],
        ).decode()
        assert '<Card title="No" />' in output
        assert "No translated" not in output
        assert "After translated." in output

    def test_raw_html_child_does_not_keep_jsx_stack_open(self):
        """Raw HTML inside JSX does not make following ESM translatable."""
        template = b"""<Callout>
  <span>html</span>
</Callout>

import { Thing } from './thing'

After.
"""
        output = self.translate(
            template,
            [
                ("import { Thing } from './thing'", "changed import"),
                ("After.", "After translated."),
            ],
        ).decode()
        assert "import { Thing } from './thing'" in output
        assert "changed import" not in output
        assert "After translated." in output

    def test_link_metadata_with_jsx_like_text_is_not_translated(self):
        """JSX-looking text in Markdown link metadata is not translated as JSX."""
        template = b"""[text](https://example.com "<Title>")

[<Bar>]: /url

[text][<Bar>]
"""
        output = self.translate(
            template,
            [("<Title>", "Title translated"), ("<Bar>", "Bar translated")],
        ).decode()
        assert "Title translated" in output
        assert "Bar translated" in output
        assert "MDX_BLOCK" not in output

    def test_attribute_backslashes_preserved(self):
        """Untranslated JSX attributes keep existing backslashes."""
        template = b'<Comp path="C:\\\\tmp" />\n'
        assert self.translate(template, []) == template

    def test_attribute_escaped_quotes_preserved(self):
        """Untranslated JSX attributes keep existing escaped quotes."""
        template = b'<Comp title="A \\"quote\\"" />\n'
        assert self.translate(template, []) == template

    def test_untranslated_units_use_source(self):
        """Untranslated units fall back to source text."""
        template = b"""# Hello

World.
"""
        output = self.translate(template, [("Hello", "Hello translated")]).decode()
        assert "# Hello translated" in output
        assert "World." in output

    def test_fuzzy_unit_skipped_without_flag(self):
        """Fuzzy units are not used when includefuzzy=False."""
        store = po.pofile()
        unit = store.addsourceunit("Hello")
        unit.target = "Hello translated"
        unit.markfuzzy(True)
        unit2 = store.addsourceunit("World.")
        unit2.target = "World translated."

        translator = MDXTranslator(
            store,
            includefuzzy=False,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(b"# Hello\n\nWorld.\n"), outputfile)
        output = outputfile.getvalue().decode()
        assert "# Hello" in output
        assert "World translated." in output

    def test_fuzzy_unit_used_with_flag(self):
        """Fuzzy units are used when includefuzzy=True."""
        store = po.pofile()
        unit = store.addsourceunit("Hello")
        unit.target = "Hello translated"
        unit.markfuzzy(True)

        translator = MDXTranslator(
            store,
            includefuzzy=True,
            outputthreshold=None,
            maxlength=0,
        )
        outputfile = BytesIO()
        translator.translate(BytesIO(b"# Hello\n"), outputfile)
        assert b"# Hello translated" in outputfile.getvalue()
