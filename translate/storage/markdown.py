#
# Copyright 2023 Anders Kaplan
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

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
from contextlib import contextmanager
from io import StringIO
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
    from collections.abc import Callable, Iterable


_EXPLICIT_HEADING_ID = re.compile(
    r"(?P<title>.*?)(?P<suffix>[ \t]+(?:"
    r"\{/\*\s*#[^\s{}*]+\s*\*/\}|"
    r"\{#[^\s{}]+\}))$"
)


def _split_explicit_heading_id(text: str) -> tuple[str, str]:
    """Split a trailing explicit heading ID from translatable text."""
    match = _EXPLICIT_HEADING_ID.fullmatch(text)
    if match is None:
        return text, ""
    return match.group("title"), match.group("suffix")


class MarkdownUnit(base.TranslationUnit):
    """A unit of translatable/localisable markdown content."""

    def __init__(self, source=None) -> None:
        super().__init__(source)
        self.locations = []

    def addlocation(self, location) -> None:
        self.locations.append(location)

    def getlocations(self):
        return self.locations


class MarkdownFile(base.TranslationStore[MarkdownUnit]):
    UnitClass = MarkdownUnit

    def __init__(
        self,
        inputfile=None,
        callback=None,
        max_line_length=None,
        extract_code_blocks=True,
        extract_frontmatter=True,
        frontmatter_translate_values=False,
        no_placeholders=False,
        lookup_callback=None,
    ) -> None:
        """
        Construct a new object instance.

        :param inputfile: if specified, the content of this file is read and parsed.
        :param callback: a function which takes a chunk of untranslated content as
          input and returns the corresponding translated content. Defaults to
          a no-op.
        :param max_line_length: if specified, the document is word wrapped to the
          given line length when rendered.
        :param extract_code_blocks: if True (default), code blocks are extracted
          for translation. If False, code blocks are left as-is.
        :param extract_frontmatter: if True (default), front matter is extracted
          for translation. If False, it is preserved as-is.
        :param frontmatter_translate_values: if True, front matter is parsed as
          YAML and one translation unit is emitted per scalar string value, using
          the key path as the unit location and docpath (e.g. ``frontmatter.metaTitle``).
          On serialization the YAML structure, keys, quoting style and comments are
          preserved and only the values are replaced by their translations. If
          False (default), ``extract_frontmatter`` governs front matter handling and
          the whole block is treated as a single opaque unit. Requires the optional
          ``ruamel.yaml`` dependency; takes precedence over ``extract_frontmatter``.
        :param no_placeholders: if True, inline elements (links, images, HTML
          spans, autolinks) are rendered verbatim in translation units instead
          of being replaced by {n} placeholder markers. Sub-attribute extraction
          (e.g. link titles as separate units) is suppressed in this mode. If
          False (default), the classic placeholder behavior is used.
        :param lookup_callback: a function which returns a translation for a source
          string, or None when no translation exists. Defaults to adapting callback
          by treating an unchanged result as missing.
        """
        base.TranslationStore.__init__(self)
        self.filename = getattr(inputfile, "name", None)
        self.callback = callback or self._dummy_callback
        self.lookup_callback = (
            self._default_lookup_callback
            if lookup_callback is None
            else lookup_callback
        )
        self.max_line_length = max_line_length
        self.extract_code_blocks = extract_code_blocks
        self.extract_frontmatter = extract_frontmatter
        self.frontmatter_translate_values = frontmatter_translate_values
        self.no_placeholders = no_placeholders
        self.filesrc = ""
        if inputfile is not None:
            md_src = inputfile.read()
            inputfile.close()
            self.parse(md_src)

    def parse(self, data) -> None:
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
            # front_matter_end indexes the closing fence line ("---" or "...").
            close_fence_idx = front_matter_end
            # Include trailing space in the front matter
            if front_matter_end + 1 < len(lines) and (
                not lines[front_matter_end + 1] or lines[front_matter_end + 1].isspace()
            ):
                front_matter_end += 1
            front_matter = "\n".join(chain(lines[: front_matter_end + 1], [""]))
            if self.frontmatter_translate_values:
                # Value-only mode: parse the YAML and emit one unit per scalar
                # value, preserving keys/structure/quoting on serialization.
                front_matter = self._translate_frontmatter_values(
                    open_fence=lines[0],
                    body_lines=lines[1:close_fence_idx],
                    close_fence=lines[close_fence_idx],
                    trailing_lines=lines[close_fence_idx + 1 : front_matter_end + 1],
                )
            elif self.extract_frontmatter:
                # Keep front matter as a normal translation unit.
                unit = self.UnitClass(front_matter)
                if self.filename:
                    unit.addlocation(f"{self.filename}:1")
                unit.setdocpath("frontmatter[1]")
                self.addunit(unit)
                front_matter = self.callback(front_matter)
            lines = lines[front_matter_end + 1 :]

        with TranslatingMarkdownRenderer(
            self._translate_callback,
            block_token.Table,
            max_line_length=self.max_line_length,
            extract_code_blocks=self.extract_code_blocks,
            lookup_callback=self.lookup_callback,
            no_placeholders=self.no_placeholders,
        ) as renderer:
            document = block_token.Document(lines)
            self.filesrc = front_matter + renderer.render(document)

    def _translate_frontmatter_values(
        self,
        open_fence: str,
        body_lines: list[str],
        close_fence: str,
        trailing_lines: list[str],
    ) -> str:
        """
        Parse the YAML front matter, emit one translation unit per scalar string
        value, and re-serialize with keys/structure/quoting/comments preserved.

        :param open_fence: the opening fence line (e.g. ``---``).
        :param body_lines: the YAML body lines between the fences.
        :param close_fence: the closing fence line (e.g. ``---`` or ``...``).
        :param trailing_lines: blank lines that followed the closing fence and
          were considered part of the front matter block.
        :return: the rendered (translated) front matter, terminated by a newline,
          ready to be prepended to the rendered document body.

        Serialization is tuned so that only the translated values change and the
        YAML formatting stays byte-stable on an identity translation:

          * The block indentation is fixed at two-space mappings with a two-space
            sequence offset (``yaml.indent(mapping=2, sequence=4, offset=2)``),
            matching the front matter style of the target files, so block
            sequences keep their source indentation (``  - item`` is not
            flattened to ``- item``).
          * Block scalars (``|`` / ``>``) keep their style, chomping indicator
            and first-line comment: the trailing-newline pattern that drives
            chomping is split off before translation and re-appended afterwards,
            and the comment / fold positions are carried over to the re-wrapped
            node. See ``_translate_frontmatter_child``.
          * Only scalar *string* values are translated. Numbers, booleans, dates
            and ``null`` are left untouched on purpose.
          * Nested maps and lists are walked recursively; list items use a
            ``[i]`` index segment in the location/docpath.
          * If the body fails to parse as YAML, fall back to the opaque-blob
            behavior so a malformed file never raises here.
        """
        # Imported lazily: ruamel.yaml is in the optional ``yaml`` extra, not
        # ``markdown``, so a top-level import would break ``[markdown]``-only
        # installs that never enable this flag.
        # pylint: disable-next=import-outside-toplevel
        from ruamel.yaml import YAML, YAMLError  # ruff:ignore[import-outside-top-level]

        # In the source the last body line is followed by a newline before the
        # closing fence, so terminate the body with one. Without it a trailing
        # block scalar loses its final newline and its chomping indicator drifts
        # (e.g. ``>`` would be emitted as ``>-``).
        body = "\n".join(body_lines) + "\n"
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 2**31  # avoid reflowing/wrapping translated values
        # Match the target front matter style: two-space mapping indentation with
        # block-sequence dashes indented two spaces under their key. ruamel
        # expresses this as a four-space sequence indent with a two-space offset
        # for the dash, which keeps "  - item" intact instead of flattening it.
        yaml.indent(mapping=2, sequence=4, offset=2)

        try:
            data = yaml.load(body) if body.strip() else None
        except YAMLError:
            # Malformed YAML: keep the original block as a single opaque unit so
            # we never lose content or raise during parsing.
            front_matter = "\n".join(
                chain([open_fence], body_lines, [close_fence], trailing_lines, [""])
            )
            unit = self.UnitClass(front_matter)
            if self.filename:
                unit.addlocation(f"{self.filename}:1")
            unit.setdocpath("frontmatter[1]")
            self.addunit(unit)
            return self.callback(front_matter)

        if data is None:
            # Empty or comment-only front matter: nothing to translate. Re-emit
            # the original block verbatim so comments survive and we do not
            # serialize a synthetic ``null`` document.
            return "\n".join(
                chain([open_fence], body_lines, [close_fence], trailing_lines, [""])
            )

        self._walk_frontmatter(data, "frontmatter")

        buffer = StringIO()
        yaml.dump(data, buffer)
        rendered_body = buffer.getvalue()
        if rendered_body.endswith("\n...\n"):
            # When the final value is a kept block scalar (``|+`` / ``>+``), ruamel
            # appends an explicit document-end marker (``...``) so the scalar's
            # trailing blank lines are not lost. Drop the marker and the single
            # terminating newline only; the blank lines stay part of the body and
            # the join below re-adds one newline before the close fence.
            rendered_body = rendered_body[: -len("\n...\n")]
        else:
            # ruamel terminates the dump with a trailing newline; the fence lines
            # and any preserved trailing blank lines are added back explicitly.
            rendered_body = rendered_body.rstrip("\n")
        parts = [open_fence]
        if rendered_body:
            parts.append(rendered_body)
        parts.extend([close_fence, *trailing_lines, ""])
        return "\n".join(parts)

    def _walk_frontmatter(self, node, path: str) -> None:
        """
        Recursively walk a parsed YAML node, translating scalar string values
        in place. ``path`` is the dotted/indexed key path used as the unit
        location and docpath (e.g. ``frontmatter.metaTitle`` or
        ``frontmatter.authors[0]``).
        """
        if isinstance(node, dict):
            for key in list(node.keys()):
                self._translate_frontmatter_child(node, key, f"{path}.{key}")
        elif isinstance(node, list):
            for index in range(len(node)):
                self._translate_frontmatter_child(node, index, f"{path}[{index}]")

    def _translate_frontmatter_child(self, container, key, path: str) -> None:
        """Translate or recurse into a single child of a map/list container."""
        # pylint: disable-next=import-outside-toplevel
        from ruamel.yaml.scalarstring import (  # ruff:ignore[import-outside-top-level]
            FoldedScalarString,
            LiteralScalarString,
            ScalarString,
        )

        value = container[key]
        if isinstance(value, (dict, list)):
            self._walk_frontmatter(value, path)
        elif isinstance(value, str):
            # bool/int/float are not str, so only genuine strings are translated.
            is_block = isinstance(value, (LiteralScalarString, FoldedScalarString))
            if is_block:
                # Block scalars (| and >): the trailing-newline run encodes the
                # chomping indicator (none -> "-" strip, one -> clip, more ->
                # "+" keep). Split it off so the unit holds only the content and
                # the indicator survives an arbitrary translation unchanged.
                content, trailing_newlines = self._split_trailing_newlines(str(value))
            else:
                content = str(value)
                trailing_newlines = ""

            if not content.strip():
                # Empty or blank scalars are preserved verbatim and never emit a
                # unit: an empty source would serialize as a spurious ``msgid ""``
                # and a wrapping callback would corrupt the value.
                return

            unit = self.addsourceunit(content)
            if self.filename:
                unit.addlocation(f"{self.filename}:{path}")
            else:
                unit.addlocation(path)
            unit.setdocpath(path)
            translated = self.callback(content)

            if is_block:
                # Re-wrap in the same block subtype, restore the chomping via the
                # trailing newlines, and carry over the first-line comment and
                # (for folded scalars) the fold positions so an identity
                # translation re-emits byte-for-byte.
                new_value = type(value)(translated + trailing_newlines)
                if hasattr(value, "comment"):
                    new_value.comment = value.comment
                if isinstance(value, FoldedScalarString) and hasattr(value, "fold_pos"):
                    new_value.fold_pos = value.fold_pos
                container[key] = new_value
            elif isinstance(value, ScalarString):
                # Preserve the original quoting style for flow scalars.
                container[key] = type(value)(translated)
            else:
                container[key] = translated

    @staticmethod
    def _split_trailing_newlines(text: str) -> tuple[str, str]:
        """Split ``text`` into its content and its trailing run of newlines."""
        stripped = text.rstrip("\n")
        return stripped, text[len(stripped) :]

    @staticmethod
    def _dummy_callback(text: str) -> str:
        return text

    def _default_lookup_callback(self, text: str) -> str | None:
        """Adapt a translation callback to the lookup callback contract."""
        translation = self.callback(text)
        return translation if translation != text else None

    def _translate_callback(self, text: str, path: list[str], docpath: str = "") -> str:
        text = text.strip()
        if not text:
            return ""

        # emit a translation unit. The PO store takes care of the escaping.
        unit = self.addsourceunit(text)
        # Index path to avoid duplicate location on list items.
        unit.addlocation(f"{self.filename or ''}{''.join(path[0])}")
        if docpath:
            unit.setdocpath(docpath)

        # return translated text
        return self.callback(text)


class TranslatingMarkdownRenderer(MarkdownRenderer):
    def __init__(
        self,
        translate_callback: Callable[[str, list[str], str], str],
        *extras,
        max_line_length: int | None = None,
        extract_code_blocks: bool = True,
        lookup_callback: Callable[[str], str | None] | None = None,
        no_placeholders: bool = False,
    ) -> None:
        super().__init__(*extras, max_line_length=max_line_length)
        self.translate_callback = translate_callback
        self.lookup_callback = lookup_callback
        self.bypass = False
        self.no_placeholders = no_placeholders
        self.path = []
        self.ignore_translation = False
        self.extract_code_blocks = extract_code_blocks
        # Docpath tracking: heading hierarchy and sibling counts
        # _heading_stack: list of (level, heading_index) for current heading nesting
        self._heading_stack: list[tuple[int, int]] = []
        # _section_counts: dict mapping element type to count at current section level
        self._section_counts: list[dict[str, int]] = [{}]
        # _container_stack: list of (container_type, index) for nested containers
        self._container_stack: list[tuple[str, int]] = []
        # _current_docpath: the current docpath string for the current block
        self._current_docpath = ""

    @contextmanager
    def _bypass_rendering(self):
        original_bypass = self.bypass
        self.bypass = True
        try:
            yield
        finally:
            self.bypass = original_bypass

    def render(self, token: mistletoe.token.Token) -> str:
        try:
            # set the root node here, because the rendering also involves some parsing,
            # and the parsing requires a valid root node.
            mistletoe.token._root_node = token  # ty:ignore[invalid-assignment]
            return super().render(token)
        finally:
            mistletoe.token._root_node = None

    # rendering of span tokens:
    # override to inject placeholders and translate content

    def _build_docpath(self, element_type: str) -> str:
        """Build the current docpath string for a block element."""
        parts = [f"h{level}[{idx}]" for level, idx in self._heading_stack]
        for container_type, container_idx in self._container_stack:
            parts.append(f"{container_type}[{container_idx}]")
        counts = self._section_counts[-1]
        counts[element_type] = counts.get(element_type, 0) + 1
        parts.append(f"{element_type}[{counts[element_type]}]")
        return "/".join(parts)

    def _enter_heading(self, level: int) -> str:
        """Update heading stack and return docpath for this heading."""
        # Pop headings of equal or greater level
        while self._heading_stack and self._heading_stack[-1][0] >= level:
            self._heading_stack.pop()
            self._section_counts.pop()
        # Count this heading at the current section level
        counts = self._section_counts[-1]
        heading_key = f"h{level}"
        counts[heading_key] = counts.get(heading_key, 0) + 1
        idx = counts[heading_key]
        # Push new section level
        self._heading_stack.append((level, idx))
        self._section_counts.append({})
        # Build path
        parts = [f"h{level}[{i}]" for level, i in self._heading_stack]
        for container_type, container_idx in self._container_stack:
            parts.append(f"{container_type}[{container_idx}]")
        return "/".join(parts)

    def _enter_container(self, container_type: str) -> None:
        """Push a container (list item, blockquote) onto the nesting stack."""
        counts = self._section_counts[-1]
        counts[container_type] = counts.get(container_type, 0) + 1
        self._container_stack.append((container_type, counts[container_type]))
        self._section_counts.append({})

    def _exit_container(self) -> None:
        """Pop a container from the nesting stack."""
        if self._container_stack:
            self._container_stack.pop()
            self._section_counts.pop()

    @classmethod
    def _split_explicit_heading_id_tokens(
        cls, tokens: Iterable[mistletoe.token.Token] | None
    ) -> tuple[list[span_token.SpanToken], str]:
        """Remove an explicit heading ID from the final raw-text token."""
        result: list[span_token.SpanToken] = []
        for token in tokens or ():
            assert isinstance(token, span_token.SpanToken)
            result.append(token)
        if not result or not isinstance(result[-1], span_token.RawText):
            return result, ""

        title, suffix = _split_explicit_heading_id(result[-1].content)
        if not suffix:
            return result, ""
        if title:
            result[-1] = span_token.RawText(title)
        else:
            result.pop()
        return result, suffix

    def _lookup_heading_translation(
        self, source: str, translation: str, suffix: str
    ) -> tuple[str, bool]:
        """Look up current and legacy heading translations without ambiguity."""
        if not suffix:
            return translation, translation != source
        if translation != source:
            translated_title, _translated_suffix = _split_explicit_heading_id(
                translation
            )
            return translated_title, True
        if self.lookup_callback is None:
            return translation, False

        current_translation = self.lookup_callback(source)
        if current_translation is not None:
            current_title, _current_suffix = _split_explicit_heading_id(
                current_translation
            )
            return current_title, True

        legacy_source = source + suffix
        legacy_translation = self.lookup_callback(legacy_source)
        if legacy_translation is None:
            return translation, False

        legacy_title, _legacy_suffix = _split_explicit_heading_id(legacy_translation)
        return legacy_title, True

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

        yield Fragment(None, placeholder_content=list(super().render_auto_link(token)))  # ty:ignore[invalid-argument-type]

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

        yield Fragment(None, placeholder_content=list(super().render_html_span(token)))  # ty:ignore[invalid-argument-type]

    def render_link_or_image(
        self, token: span_token.SpanToken, target: str
    ) -> Iterable[Fragment]:
        if self.bypass:
            yield from super().render_link_or_image(token, target)
            return

        yield from self.embed_span(Fragment("["), token.children, Fragment("]"))  # ty:ignore[invalid-argument-type]

        if token.dest_type in {"uri", "angle_uri"}:  # ty:ignore[unresolved-attribute]
            # Markdown link format: "[" description "](" dest_part [" " title] ")"
            dest_part = f"<{target}>" if token.dest_type == "angle_uri" else target  # ty:ignore[unresolved-attribute]
            placeholder = Fragment(None, important=True)  # ty:ignore[invalid-argument-type]
            placeholder.placeholder_content = [  # ty:ignore[unresolved-attribute]
                Fragment("("),
                Fragment(dest_part),
            ]
            if token.title:  # ty:ignore[unresolved-attribute]
                translated_title = self.translate_callback(
                    token.title,  # ty:ignore[unresolved-attribute]
                    [*self.path, "link-title"],
                    self._current_docpath,
                )
                placeholder.placeholder_content.extend(  # ty:ignore[unresolved-attribute]
                    [
                        Fragment(" ", wordwrap=True),
                        Fragment(token.title_delimiter),  # ty:ignore[unresolved-attribute]
                        Fragment(translated_title, wordwrap=True),
                        Fragment(
                            ")"
                            if token.title_delimiter == "("  # ty:ignore[unresolved-attribute]
                            else token.title_delimiter  # ty:ignore[unresolved-attribute]
                        ),
                    ]
                )
            placeholder.placeholder_content.append(Fragment(")"))  # ty:ignore[unresolved-attribute]
            yield placeholder
        elif token.dest_type == "full":  # ty:ignore[unresolved-attribute]
            # Markdown link format: "[" description "][" label "]"
            translated_label = self.translate_callback(
                token.label,  # ty:ignore[unresolved-attribute]
                [*self.path, "link-label"],
                self._current_docpath,
            )
            placeholder = Fragment(None, important=True)  # ty:ignore[invalid-argument-type]
            placeholder.placeholder_content = [  # ty:ignore[unresolved-attribute]
                Fragment("["),
                Fragment(translated_label, wordwrap=True),
                Fragment("]"),
            ]
            yield placeholder
        elif token.dest_type == "collapsed":  # ty:ignore[unresolved-attribute]
            # Markdown link format: "[" description "][]"
            yield Fragment("[]")
        else:
            # Markdown link format: "[" description "]"
            pass

    def render_link_reference_definition(
        self, token: LinkReferenceDefinition
    ) -> Iterable[Fragment]:
        # note: these tokens will never be encountered in bypass mode.
        # Translate label and title unless we're in an ignore section or
        # no_placeholders mode.  In no_placeholders mode we must not translate
        # the label here — the definition is rendered verbatim (the whole block
        # is treated as non-translatable) so that inline reference links, which
        # are rendered verbatim in bypass mode with the original label, resolve
        # correctly and no label mismatch occurs in the output.
        if self.ignore_translation or self.no_placeholders:
            label = token.label
            title = token.title
        else:
            label = self.translate_callback(
                token.label, [*self.path, "link-label"], self._current_docpath
            )
            title = (
                self.translate_callback(
                    token.title, [*self.path, "link-title"], self._current_docpath
                )
                if token.title
                else None
            )

        placeholder = Fragment(None)  # ty:ignore[invalid-argument-type]
        placeholder.placeholder_content = [  # ty:ignore[unresolved-attribute]
            Fragment("["),
            Fragment(label, wordwrap=True),
            Fragment("]: ", wordwrap=True),
            Fragment(
                f"<{token.dest}>" if token.dest_type == "angle_uri" else token.dest
            ),
        ]
        if title:
            placeholder.placeholder_content.extend(  # ty:ignore[unresolved-attribute]
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
        self, token: block_token.Heading, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._current_docpath = self._enter_heading(token.level)
        title_tokens, suffix = self._split_explicit_heading_id_tokens(token.children)
        if suffix:
            translated = next(
                iter(
                    self.span_to_lines(
                        title_tokens,
                        max_line_length=None,
                        legacy_heading_suffix=suffix,
                    )
                ),
                "",
            )
            heading = "#" * token.level
            if translated:
                heading += " " + translated
            heading += suffix
            if token.closing_sequence:
                heading += " " + token.closing_sequence
            content = [heading]
        else:
            content = list(
                super().render_heading(token, max_line_length=max_line_length)
            )
        self.path.pop()
        return content

    def render_setext_heading(
        self, token: block_token.SetextHeading, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._current_docpath = self._enter_heading(token.level)
        title_tokens, suffix = self._split_explicit_heading_id_tokens(token.children)
        if suffix:
            content = list(
                self.span_to_lines(
                    title_tokens,
                    max_line_length=max_line_length,
                    legacy_heading_suffix=suffix,
                )
            )
            if content:
                content[-1] += suffix
            else:
                content.append(suffix.lstrip())
            content.append(token.underline)
        else:
            content = list(
                super().render_setext_heading(token, max_line_length=max_line_length)
            )
        self.path.pop()
        return content

    def render_quote(
        self, token: block_token.Quote, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._enter_container("blockquote")
        content = list(super().render_quote(token, max_line_length=max_line_length))
        self._exit_container()
        self.path.pop()
        return content

    def render_paragraph(
        self, token: block_token.Paragraph, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._current_docpath = self._build_docpath("p")
        content = list(super().render_paragraph(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def render_html_block(
        self, token: block_token.HtmlBlock, max_line_length: int | None
    ) -> Iterable[str]:
        # Check if this is a translation control comment
        content = token.content.strip()
        if content == "<!-- translate:off -->":
            self.ignore_translation = True
        elif content == "<!-- translate:on -->":
            self.ignore_translation = False

        # Return the raw HTML block content
        return super().render_html_block(token, max_line_length=max_line_length)

    def render_block_code(
        self, token: block_token.BlockCode, max_line_length: int | None
    ) -> Iterable[str]:
        if not self.extract_code_blocks or self.ignore_translation:
            return super().render_block_code(token, max_line_length=max_line_length)

        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._current_docpath = self._build_docpath("code")
        code_content = token.content[:-1]  # strip trailing \n
        translated = self.translate_callback(
            code_content, self.path, self._current_docpath
        )
        lines = translated.split("\n")
        self.path.pop()
        return self.prefix_lines(lines, "    ")

    def render_fenced_code_block(
        self,
        token: block_token.CodeFence,
        max_line_length: int | None,
    ) -> Iterable[str]:
        if not self.extract_code_blocks or self.ignore_translation:
            return super().render_fenced_code_block(
                token,
                max_line_length=max_line_length,
            )

        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._current_docpath = self._build_docpath("code")
        code_content = token.content[:-1]  # strip trailing \n
        translated = self.translate_callback(
            code_content, self.path, self._current_docpath
        )
        indentation = " " * token.indentation
        result = [indentation + token.delimiter + token.info_string]
        result.extend(self.prefix_lines(translated.split("\n"), indentation))
        result.append(indentation + token.delimiter)
        self.path.pop()
        return result

    def render_list_item(
        self, token: block_token.ListItem, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")
        self._enter_container("li")
        content = list(super().render_list_item(token, max_line_length=max_line_length))
        self._exit_container()
        self.path.pop()
        return content

    def render_table(
        self, token: block_token.Table, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._table_docpath = self._build_docpath("table")
        self._table_row_index = 0
        content = list(super().render_table(token, max_line_length=max_line_length))
        self.path.pop()
        return content

    def table_row_to_text(self, row) -> list[str]:
        """Render each table cell with a unique docpath."""
        self._table_row_index += 1
        result = []
        for col_index, col in enumerate(row.children):
            self._current_docpath = (
                f"{self._table_docpath}/r[{self._table_row_index}]/c[{col_index + 1}]"
            )
            result.append(
                next(self.span_to_lines(col.children, max_line_length=None), "")  # ty:ignore[invalid-argument-type]
            )
        return result

    def render_link_reference_definition_block(
        self, token: LinkReferenceDefinitionBlock, max_line_length: int | None
    ) -> Iterable[str]:
        self.path.append(f":{token.line_number}")  # ty:ignore[unresolved-attribute]
        self._current_docpath = self._build_docpath("link-ref-def")
        content = list(
            super().render_link_reference_definition_block(
                token, max_line_length=max_line_length
            )
        )
        self.path.pop()
        return content

    # translation and placeholder functions

    def span_to_lines(
        self,
        tokens: Iterable[span_token.SpanToken],
        max_line_length: int | None,
        legacy_heading_suffix: str = "",
    ) -> Iterable[str]:
        """Renders a sequence of span tokens to markdown, with translation."""
        # If we're in an ignore section, skip translation
        if self.ignore_translation:
            with self._bypass_rendering():
                fragments = self.make_fragments(tokens)
                # Expand placeholders before rendering
                expanded = list(self.expand_placeholders(fragments))
                return super().fragments_to_lines(
                    expanded, max_line_length=max_line_length
                )

        # No-placeholders opt-in mode: render source-side fragments verbatim.
        # bypass=True is set BEFORE make_fragments so render_link_or_image,
        # render_auto_link, and render_html_span fall through to their super()
        # implementations, yielding raw text fragments instead of Fragment(None,
        # placeholder_content=...) placeholders.  This means links/images/HTML
        # appear in full in the translation unit rather than as {n} markers, and
        # no sub-attribute extraction (e.g. link titles as separate units) occurs.
        #
        # render_link_reference_definition does NOT check bypass; it always
        # creates Fragment(None, ...) placeholders with label/title already
        # extracted via translate_callback.  We reuse trim_flanking_placeholders
        # so those placeholders end up in leader/trailer (not in content), which
        # prevents translate_callback from being called a second time for them.
        if self.no_placeholders:
            with self._bypass_rendering():
                fragments = list(self.make_fragments(tokens))
                merged = self.merge_adjacent_placeholders(fragments)
                leader, content, trailer = self.trim_flanking_placeholders(merged)
                content_frags = list(self.expand_placeholders(content))
                content_md = "\n".join(
                    super().fragments_to_lines(
                        content_frags,
                        max_line_length=float("inf"),  # ty:ignore[invalid-argument-type]
                    )
                )
                # normalize hard line break markers to plain \n for translate_callback:
                # \\\n = backslash hard break (e.g. "alpha\\\nbeta")
                # (space){2+}\n = trailing-space hard break (e.g. "alpha  \nbeta")
                content_md = re.sub(r"\\\n| {2,}\n", "\n", content_md)
                if content_md:
                    translated_md = self.translate_callback(
                        content_md, self.path, self._current_docpath
                    )
                    translated_md, _translation_found = (
                        self._lookup_heading_translation(
                            content_md, translated_md, legacy_heading_suffix
                        )
                    )
                    translated_md = translated_md.replace("\n", "\\\n").strip(" \t")
                    translated = list(
                        self.make_fragments(span_token.tokenize_inner(translated_md))
                    )
                    expanded = list(
                        self.expand_placeholders(chain(leader, translated, trailer))
                    )
                else:
                    expanded = list(self.expand_placeholders(chain(leader, trailer)))
                return super().fragments_to_lines(
                    expanded, max_line_length=max_line_length
                )

        # turn the span into fragments, which may include placeholders.
        # list-ify the iterator because we may need to traverse it more than once
        fragments = list(self.make_fragments(tokens))
        with self._bypass_rendering():
            # pre-process placeholders
            merged = self.merge_adjacent_placeholders(fragments)
            leader, content, trailer = self.trim_flanking_placeholders(merged)
            placeholders = self.insert_placeholder_markers(content)

            # render the translatable content (with placeholders) to markdown
            content_md = "\n".join(
                self.fragments_to_lines(content, max_line_length=float("inf"))  # ty:ignore[invalid-argument-type]
            )

            # translate and parse into new fragments. handle hard line breaks.
            if content_md:
                translated_md = self.translate_callback(
                    content_md, self.path, self._current_docpath
                )
                translated_md, translation_found = self._lookup_heading_translation(
                    content_md, translated_md, legacy_heading_suffix
                )
                # If no placeholder-based translation matched, try expanded
                # Markdown links and their legacy heading-ID form.
                if not translation_found and placeholders and self.lookup_callback:
                    expanded_content_md = self.remove_placeholder_markers(
                        content_md, list(placeholders)
                    )
                    expanded_translated_md = self.lookup_callback(expanded_content_md)
                    if expanded_translated_md is None and legacy_heading_suffix:
                        expanded_translated_md = self.lookup_callback(
                            expanded_content_md + legacy_heading_suffix
                        )
                    if expanded_translated_md is not None:
                        if legacy_heading_suffix:
                            expanded_translated_md, _expanded_suffix = (
                                _split_explicit_heading_id(expanded_translated_md)
                            )
                        translated_md = expanded_translated_md
                        # The expanded translation already contains full markdown
                        # syntax (e.g. links), so skip placeholder replacement.
                        use_placeholders = []
                    else:
                        use_placeholders = placeholders
                else:
                    use_placeholders = placeholders
                translated_md = translated_md.replace("\n", "\\\n").strip(" \t")
                translated_md = self.remove_placeholder_markers(
                    translated_md, use_placeholders
                )
                translated = self.make_fragments(
                    span_token.tokenize_inner(translated_md)
                )
                fragments = chain(leader, translated, trailer)

            # expand placeholders and render into final markdown.
            # list-ify to let all generators run before exiting the try/finally block
            expanded = list(self.expand_placeholders(fragments))
            return super().fragments_to_lines(expanded, max_line_length=max_line_length)

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
                    placeholder = Fragment(None, placeholder_content=chunk)  # ty:ignore[invalid-argument-type]
                    placeholder.important = any(  # ty:ignore[unresolved-attribute]
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
            content = self.expand_placeholders(placeholder.placeholder_content)  # ty:ignore[unresolved-attribute]
            content_md = "\n".join(
                self.fragments_to_lines(content, max_line_length=float("inf"))  # ty:ignore[invalid-argument-type]
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
