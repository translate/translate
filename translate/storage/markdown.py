#
# Copyright 2023 Anders Kaplan
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Module for parsing Markdown files for translation.

The principles for extraction of translation units are as follows:

1. Extract all content relevant for translation, at the cost of also
   including some formatting.
2. One translation unit per paragraph.
3. Keep formatting out of the translation units as much as possible.
   Exceptions include *phrase emphasis* and `inline code`.
   Use placeholders {1}, {2}, ..., as needed.
4. Avoid HTML entities in the translation units. Use Unicode
   equivalents if possible.

White space within translation units is normalized, because the PO format does
not preserve white space, and the translated Markdown content may have
to be reflowed anyway.
"""

from __future__ import annotations

import re
from itertools import chain
from typing import TYPE_CHECKING

import mistletoe.token
from mistletoe import block_token, span_token
from mistletoe.markdown_renderer import (
    Fragment,
    LinkReferenceDefinition,
    LinkReferenceDefinitionBlock,
    MarkdownRenderer,
)

from translate.storage import base

if TYPE_CHECKING:
    from collections.abc import Iterable


class MarkdownUnit(base.TranslationUnit):
    """A unit of translatable/localisable markdown content."""

    def __init__(self, source=None):
        super().__init__(source)
        self.locations = []

    def addlocation(self, location):
        self.locations.append(location)

    def getlocations(self):
        return self.locations


class MarkdownFrontmatterUnit(MarkdownUnit):
    @staticmethod
    def isheader():
        return True


class MarkdownFile(base.TranslationStore):
    UnitClass = MarkdownUnit

    def __init__(self, inputfile=None, callback=None, max_line_length=None):
        """
        Construct a new object instance.

        :param inputfile: if specified, the content of this file is read and parsed.
        :param callback: a function which takes a chunk of untranslated content as
          input and returns the corresponding translated content. Defaults to
          a no-op.
        :param max_line_length: if specified, the document is word wrapped to the
          given line length when rendered.
        """
        base.TranslationStore.__init__(self)
        self.filename = getattr(inputfile, "name", None)
        self.callback = callback or self._dummy_callback
        self.max_line_length = max_line_length
        self.filesrc = ""
        if inputfile is not None:
            md_src = inputfile.read()
            inputfile.close()
            self.parse(md_src)

    def parse(self, data):
        """Process the given source string (binary)."""
        lines = data.decode().splitlines(keepends=False)
        front_matter_end = 0
        front_matter = ""
        has_front_matter = False
        for line_no, line in enumerate(lines):
            if not has_front_matter:
                if line and not line.startswith("---"):
                    # No front matter found
                    break
                has_front_matter = True
            elif line.startswith(("---", "...")):
                # End of front matter
                front_matter_end = line_no
                break

        if front_matter_end:
            # Include trailing space in the front matter
            if front_matter_end + 1 < len(lines) and (
                not lines[front_matter_end + 1] or lines[front_matter_end + 1].isspace()
            ):
                front_matter_end += 1
            # Generate header unit to store front matter
            front_matter = "\n".join(chain(lines[: front_matter_end + 1], [""]))
            header = MarkdownFrontmatterUnit(front_matter)
            self.addunit(header)
            lines = lines[front_matter_end + 1 :]

        with TranslatingMarkdownRenderer(
            self._translate_callback,
            block_token.Table,
            max_line_length=self.max_line_length,
        ) as renderer:
            document = block_token.Document(lines)
            self.filesrc = front_matter + renderer.render(document)

    @staticmethod
    def _dummy_callback(text: str) -> str:
        return text

    def _translate_callback(self, text: str, path: Iterable[str]) -> str:
        text = text.strip()
        if not text:
            return ""

        # emit a translation unit. The PO store takes care of the escaping.
        unit = self.addsourceunit(text)
        # Index path to avoid duplicate location on list items.
        unit.addlocation(f"{self.filename or ''}{''.join(path[0])}")

        # return translated text
        return self.callback(text)


class TranslatingMarkdownRenderer(MarkdownRenderer):
    def __init__(self, translate_callback, *extras, max_line_length: int | None = None):
        super().__init__(*extras, max_line_length=max_line_length)
        self.translate_callback = translate_callback
        self.bypass = False
        self.path = []
        self.ignore_translation = False

    def render(self, token: mistletoe.token.Token) -> str:
        try:
            # set the root node here, because the rendering also involves some parsing,
            # and the parsing requires a valid root node.
            mistletoe.token._root_node = token
            return super().render(token)
        finally:
            mistletoe.token._root_node = None

    # rendering of span tokens:
    # override to inject placeholders and translate content

    _leading_ws = re.compile(r"^(\s+)\S")
    _trailing_ws = re.compile(r"\S(\s+)$")

    def render_raw_text(self, token: span_token.RawText) -> Iterable[Fragment]:
        # make separate fragments for leading and trailing space, if applicable
        match = self._leading_ws.search(token.content)
        if match:
            yield Fragment(match.group(1), wordwrap=True)
            token.content = token.content.lstrip()
        match = self._trailing_ws.search(token.content)
        if match:
            yield Fragment(token.content.rstrip(), wordwrap=True)
            yield Fragment(match.group(1), wordwrap=True)
        else:
            yield Fragment(token.content, wordwrap=True)

    def render_auto_link(self, token: span_token.AutoLink) -> Iterable[Fragment]:
        # replace with placeholder, unless in bypass mode
        if self.bypass:
            yield from super().render_auto_link(token)
            return

        yield Fragment(None, placeholder_content=super().render_auto_link(token))

    def render_line_break(self, token: span_token.LineBreak) -> Iterable[Fragment]:
        if self.bypass:
            yield from super().render_line_break(token)
            return

        yield Fragment("\n", wordwrap=token.soft, hard_line_break=not token.soft)

    def render_html_span(self, token: span_token.HTMLSpan) -> Iterable[Fragment]:
        # replace with placeholder, unless in bypass mode
        if self.bypass:
            yield from super().render_html_span(token)
            return

        yield Fragment(None, placeholder_content=super().render_html_span(token))

    def render_link_or_image(
        self, token: span_token.SpanToken, target: str
    ) -> Iterable[Fragment]:
        if self.bypass:
            yield from super().render_link_or_image(token, target)
            return

        yield from self.embed_span(Fragment("["), token.children, Fragment("]"))

        if token.dest_type in {"uri", "angle_uri"}:
            # Markdown link format: "[" description "](" dest_part [" " title] ")"
            dest_part = f"<{target}>" if token.dest_type == "angle_uri" else target
            placeholder = Fragment(None, important=True)
            placeholder.placeholder_content = [
                Fragment("("),
                Fragment(dest_part),
            ]
            if token.title:
                translated_title = self.translate_callback(
                    token.title, [*self.path, "link-title"]
                )
                placeholder.placeholder_content.extend(
                    [
                        Fragment(" ", wordwrap=True),
                        Fragment(token.title_delimiter),
                        Fragment(translated_title, wordwrap=True),
                        Fragment(
                            ")"
                            if token.title_delimiter == "("
                            else token.title_delimiter
                        ),
                    ]
                )
            placeholder.placeholder_content.append(Fragment(")"))
            yield placeholder
        elif token.dest_type == "full":
            # Markdown link format: "[" description "][" label "]"
            translated_label = self.translate_callback(
                token.label, [*self.path, "link-label"]
            )
            placeholder = Fragment(None, important=True)
            placeholder.placeholder_content = [
                Fragment("["),
                Fragment(translated_label, wordwrap=True),
                Fragment("]"),
            ]
            yield placeholder
        elif token.dest_type == "collapsed":
            # Markdown link format: "[" description "][]"
            yield Fragment("[]")
        else:
            # Markdown link format: "[" description "]"
            pass

    def render_link_reference_definition(
        self, token: LinkReferenceDefinition
    ) -> Iterable[Fragment]:
        # note: these tokens will never be encountered in bypass mode.
        # Translate label and title unless we're in an ignore section
        if self.ignore_translation:
            label = token.label
            title = token.title
        else:
            label = self.translate_callback(token.label, [*self.path, "link-label"])
            title = (
                self.translate_callback(token.title, [*self.path, "link-title"])
                if token.title
                else None
            )

        placeholder = Fragment(None)
        placeholder.placeholder_content = [
            Fragment("["),
            Fragment(label, wordwrap=True),
            Fragment("]: ", wordwrap=True),
            Fragment(
                f"<{token.dest}>" if token.dest_type == "angle_uri" else token.dest
            ),
        ]
        if title:
            placeholder.placeholder_content.extend(
                [
                    Fragment(" ", wordwrap=True),
                    Fragment(token.title_delimiter),
                    Fragment(title, wordwrap=True),
                    Fragment(
                        ")" if token.title_delimiter == "(" else token.title_delimiter
                    ),
                ]
            )
        yield placeholder

    # rendering of block tokens:
    # override to keep track of the content path

    def render_heading(
        self, token: block_token.Heading, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(super().render_heading(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def render_setext_heading(
        self, token: block_token.SetextHeading, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(
            super().render_setext_heading(token, max_line_length=max_line_length)
        )
        self.path.pop()
        return content

    def render_quote(
        self, token: block_token.Quote, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(super().render_quote(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def render_paragraph(
        self, token: block_token.Paragraph, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(super().render_paragraph(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def render_html_block(
        self, token: block_token.HtmlBlock, max_line_length: int
    ) -> Iterable[str]:
        # Check if this is a translation control comment
        content = token.content.strip()
        if content == "<!-- translate:off -->":
            self.ignore_translation = True
        elif content == "<!-- translate:on -->":
            self.ignore_translation = False

        # Return the raw HTML block content
        return super().render_html_block(token, max_line_length=max_line_length)

    def render_list_item(
        self, token: block_token.ListItem, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(super().render_list_item(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def render_table(
        self, token: block_token.Table, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(super().render_table(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def render_link_reference_definition_block(
        self, token: LinkReferenceDefinitionBlock, max_line_length: int
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        content = list(
            super().render_link_reference_definition_block(
                token, max_line_length=max_line_length
            )
        )
        self.path.pop()
        return content

    # translation and placeholder functions

    def span_to_lines(
        self, tokens: Iterable[span_token.SpanToken], max_line_length: int
    ) -> Iterable[str]:
        """Renders a sequence of span tokens to markdown, with translation."""
        # If we're in an ignore section, skip translation
        if self.ignore_translation:
            original_bypass = self.bypass
            try:
                self.bypass = True
                fragments = self.make_fragments(tokens)
                # Expand placeholders before rendering
                expanded = list(self.expand_placeholders(fragments))
                return super().fragments_to_lines(
                    expanded, max_line_length=max_line_length
                )
            finally:
                self.bypass = original_bypass

        # turn the span into fragments, which may include placeholders.
        # list-ify the iterator because we may need to traverse it more than once
        fragments = list(self.make_fragments(tokens))
        original_bypass = self.bypass
        try:
            self.bypass = True

            # pre-process placeholders
            merged = self.merge_adjacent_placeholders(fragments)
            leader, content, trailer = self.trim_flanking_placeholders(merged)
            placeholders = self.insert_placeholder_markers(content)

            # render the translatable content (with placeholders) to markdown
            content_md = "\n".join(
                self.fragments_to_lines(content, max_line_length=float("inf"))
            )

            # translate and parse into new fragments. handle hard line breaks.
            if content_md:
                translated_md = self.translate_callback(content_md, self.path)
                translated_md = translated_md.replace("\n", "\\\n").strip(" \t")
                translated_md = self.remove_placeholder_markers(
                    translated_md, placeholders
                )
                translated = self.make_fragments(
                    span_token.tokenize_inner(translated_md)
                )
                fragments = chain(leader, translated, trailer)

            # expand placeholders and render into final markdown.
            # list-ify to let all generators run before exiting the try/finally block
            expanded = list(self.expand_placeholders(fragments))
            return super().fragments_to_lines(expanded, max_line_length=max_line_length)
        finally:
            self.bypass = original_bypass

    @classmethod
    def merge_adjacent_placeholders(
        cls, fragments: Iterable[Fragment]
    ) -> Iterable[Fragment]:
        """Replaces sequences of placeholders and whitespace with larger placeholders."""
        fragments = list(fragments)
        start = 0
        while start < len(fragments):
            if getattr(fragments[start], "placeholder_content", None):
                end = 0
                for j in range(start + 1, len(fragments)):
                    if getattr(fragments[j], "placeholder_content", None):
                        end = j + 1
                    elif fragments[j].text.isspace():
                        pass
                    else:
                        break
                if end:
                    chunk = fragments[start:end]
                    placeholder = Fragment(None, placeholder_content=chunk)
                    placeholder.important = any(
                        getattr(fragment, "important", False) for fragment in chunk
                    )
                    fragments[start:end] = (placeholder,)
            start += 1

        return fragments

    @classmethod
    def trim_flanking_placeholders(
        cls, fragments: Iterable[Fragment]
    ) -> tuple[Iterable[Fragment], Iterable[Fragment], Iterable[Fragment]]:
        """
        Splits leading and trailing placeholders and whitespace, and the main
        content, into separate lists. Placeholders marked as important are kept
        with the main content.
        """
        fragments = list(fragments)

        pos = 0
        while pos < len(fragments):
            if getattr(fragments[pos], "placeholder_content", None):
                if getattr(fragments[pos], "important", False):
                    break
            elif not fragments[pos].text.isspace():
                break
            pos += 1

        t = len(fragments)
        while t - 1 >= pos:
            if getattr(fragments[t - 1], "placeholder_content", None):
                if getattr(fragments[t - 1], "important", False):
                    break
            elif not fragments[t - 1].text.isspace():
                break
            t -= 1

        return fragments[:pos], fragments[pos:t], fragments[t:]

    @classmethod
    def insert_placeholder_markers(
        cls, fragments: Iterable[Fragment]
    ) -> Iterable[Fragment]:
        """
        Sets the text of the (top-level) placeholder fragments to "{n}".
        Returns an ordered list of placeholders.
        """
        placeholders = []
        for fragment in fragments:
            content = getattr(fragment, "placeholder_content", None)
            if content:
                placeholders.append(fragment)
                fragment.text = f"{{{len(placeholders)}}}"

        return placeholders

    def remove_placeholder_markers(
        self, markdown: str, placeholders: Iterable[Fragment]
    ) -> str:
        """Replaces placeholder markers in the given markdown with placeholder content."""
        for index, placeholder in enumerate(placeholders):
            content = self.expand_placeholders(placeholder.placeholder_content)
            content_md = "\n".join(
                self.fragments_to_lines(content, max_line_length=float("inf"))
            )
            markdown = markdown.replace(f"{{{index + 1}}}", content_md)

        return markdown

    def expand_placeholders(self, fragments: Iterable[Fragment]) -> Iterable[Fragment]:
        """Expands placeholder fragments, recursively."""
        for fragment in fragments:
            content = getattr(fragment, "placeholder_content", None)
            if content:
                yield from self.expand_placeholders(content)
            else:
                yield fragment
