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
from dataclasses import dataclass
from io import StringIO
from itertools import chain
from typing import TYPE_CHECKING

from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode

from translate.storage import base
from translate.storage._markdown_parser import ATX_HEADING, markdown_parser
from translate.storage.yaml_limits import (
    DEFAULT_MAX_YAML_NODES,
    DEFAULT_MAX_YAML_UNITS,
    YAMLTraversalBudget,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from markdown_it.utils import EnvType


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
        max_yaml_nodes: int | None = DEFAULT_MAX_YAML_NODES,
        max_yaml_units: int | None = DEFAULT_MAX_YAML_UNITS,
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
        :param max_yaml_nodes: maximum visits while extracting YAML front matter
            values, including repeated visits through aliases; None disables it.
        :param max_yaml_units: maximum units extracted from YAML front matter;
            None disables it.
        """
        base.TranslationStore.__init__(self)
        self.filename = getattr(inputfile, "name", None)
        self.callback = callback or self._dummy_callback
        self._last_translation: tuple[str, str] | None = None
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
        self._yaml_budget = YAMLTraversalBudget(max_yaml_nodes, max_yaml_units)
        self.filesrc = ""
        if inputfile is not None:
            md_src = inputfile.read()
            inputfile.close()
            self.parse(md_src)

    def parse(self, data) -> None:
        """Process the given source string (binary)."""
        self._yaml_budget.reset()
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

        renderer = TranslatingMarkdownRenderer(
            self._translate_callback,
            max_line_length=self.max_line_length,
            extract_code_blocks=self.extract_code_blocks,
            lookup_callback=self.lookup_callback,
            no_placeholders=self.no_placeholders,
        )
        self.filesrc = front_matter + renderer.render(lines)

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
            chomping is split off before translation and re-appended afterwards.
            Fold positions are retained only when the content is unchanged. See
            ``_translate_frontmatter_child``.
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
        with self._yaml_budget.visit(node):
            if isinstance(node, dict):
                for key in list(node.keys()):
                    self._translate_frontmatter_child(node, key, f"{path}.{key}")
            elif isinstance(node, list):
                for index in range(len(node)):
                    self._translate_frontmatter_child(node, index, f"{path}[{index}]")

    def _translate_frontmatter_child(self, container, key, path: str) -> None:
        """Translate or recurse into a single child of a map/list container."""
        value = container[key]
        if isinstance(value, (dict, list)):
            self._walk_frontmatter(value, path)
        else:
            with self._yaml_budget.visit(value):
                if isinstance(value, str):
                    self._translate_frontmatter_scalar(container, key, path, value)

    def _translate_frontmatter_scalar(
        self, container, key, path: str, value: str
    ) -> None:
        """Extract and translate one YAML front matter scalar."""
        # pylint: disable-next=import-outside-toplevel
        from ruamel.yaml.scalarstring import (  # ruff:ignore[import-outside-top-level]
            FoldedScalarString,
            LiteralScalarString,
            ScalarString,
        )

        is_block = isinstance(value, (LiteralScalarString, FoldedScalarString))
        if is_block:
            # Block scalars carry trailing newlines that encode their style.
            content, trailing_newlines = self._split_trailing_newlines(str(value))
        else:
            content = str(value)
            trailing_newlines = ""

        if not content.strip():
            return

        self._yaml_budget.count_unit()
        unit = self.addsourceunit(content)
        if self.filename:
            unit.addlocation(f"{self.filename}:{path}")
        else:
            unit.addlocation(path)
        unit.setdocpath(path)
        translated = self.callback(content)

        if is_block:
            new_value = type(value)(translated + trailing_newlines)
            if hasattr(value, "comment"):
                new_value.comment = value.comment
            if (
                translated == content
                and isinstance(value, FoldedScalarString)
                and isinstance(new_value, FoldedScalarString)
                and hasattr(value, "fold_pos")
            ):
                new_value.fold_pos = value.fold_pos
            container[key] = new_value
        elif isinstance(value, ScalarString):
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
        if self._last_translation is not None and self._last_translation[0] == text:
            translation = self._last_translation[1]
        else:
            translation = self.callback(text)
        return translation if translation != text else None

    def _translate_callback(self, text: str, path: list[str], docpath: str = "") -> str:
        text = text.strip()
        if not text:
            return ""

        # emit a translation unit. The PO store takes care of the escaping.
        unit = self.addsourceunit(text)
        # Index path to avoid duplicate location on list items.
        unit.addlocation(f"{self.filename or ''}{path[0]}")
        if docpath:
            unit.setdocpath(docpath)

        # return translated text
        translation = self.callback(text)
        self._last_translation = text, translation
        return translation


@dataclass(slots=True)
class Fragment:
    text: str
    wordwrap: bool = False
    hard_line_break: bool = False
    placeholder_content: list[Fragment] | None = None
    important: bool = False
    html_soft_break: bool = False


class TranslatingMarkdownRenderer:
    """Render parsed Markdown back to Markdown while translating its content."""

    def __init__(
        self,
        translate_callback: Callable[[str, list[str], str], str],
        *,
        max_line_length: int | None = None,
        extract_code_blocks: bool = True,
        lookup_callback: Callable[[str], str | None] | None = None,
        no_placeholders: bool = False,
    ) -> None:
        self.translate_callback = translate_callback
        self.lookup_callback = lookup_callback
        self.max_line_length = max_line_length
        self.bypass = False
        self.no_placeholders = no_placeholders
        self.path: list[str] = []
        self.ignore_translation = False
        self.extract_code_blocks = extract_code_blocks
        self._heading_stack: list[tuple[int, int]] = []
        self._section_counts: list[dict[str, int]] = [{}]
        self._container_stack: list[tuple[str, int]] = []
        self._current_docpath = ""
        self._env: EnvType = {}
        self._lines: list[str] = []

    @contextmanager
    def _bypass_rendering(self):
        original_bypass = self.bypass
        self.bypass = True
        try:
            yield
        finally:
            self.bypass = original_bypass

    def render(self, lines: list[str]) -> str:
        self._lines = lines
        source = "".join(f"{line}\n" for line in lines)
        self._env.clear()
        nodes = markdown_parser(block_only=True).parse(source, self._env)
        if self._env.get("nesting_limit_reached"):
            return source
        return "".join(
            f"{line}\n"
            for line in self.render_blocks(
                SyntaxTreeNode(nodes), 0, len(lines), self.max_line_length
            )
        )

    def _parse_inline(
        self, text: str, *, normalized: bool = False
    ) -> list[SyntaxTreeNode]:
        parser = markdown_parser(block_only=normalized)
        if normalized:
            # The block pass already normalized source text. Targets supplied
            # by translation callbacks still go through the full inline API.
            tokens = parser.inline.parse(text, parser, self._env, [])
        else:
            tokens = parser.parseInline(text, self._env)[0].children or []
        return SyntaxTreeNode(tokens).children

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

    @staticmethod
    def _split_explicit_heading_id_tokens(
        nodes: list[SyntaxTreeNode],
    ) -> tuple[list[SyntaxTreeNode], str]:
        """Remove an explicit heading ID from the final text node."""
        if not nodes or nodes[-1].type != "text":
            return nodes, ""
        title, suffix = _split_explicit_heading_id(nodes[-1].content)
        if not suffix:
            return nodes, ""
        if title:
            node = SyntaxTreeNode(
                [Token("text", "", 0, content=title)], create_root=False
            )
            return [*nodes[:-1], node], suffix
        return nodes[:-1], suffix

    def _lookup_heading_translation(
        self, source: str, translation: str, suffix: str
    ) -> tuple[str, bool]:
        """Look up current and legacy heading translations without ambiguity."""
        if not suffix:
            # An identity target is still a successful lookup. Only use the
            # secondary lookup to check presence: the primary callback may have
            # selected a different occurrence of a duplicated source.
            return translation, translation != source or (
                self.lookup_callback is not None
                and self.lookup_callback(source) is not None
            )
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

    def make_fragments(self, nodes: list[SyntaxTreeNode]) -> Iterable[Fragment]:
        for index, node in enumerate(nodes):
            if node.type == "softbreak" and (
                (index and nodes[index - 1].type == "html_inline")
                or (index + 1 < len(nodes) and nodes[index + 1].type == "html_inline")
            ):
                yield Fragment("\n", wordwrap=True, html_soft_break=True)
            else:
                yield from self.render_inline(node)

    def render_inline(self, node: SyntaxTreeNode) -> Iterable[Fragment]:
        match node.type:
            case "text":
                yield from self.render_text(node.content)
            case "text_special":
                if node.info == "escape":
                    yield Fragment(node.markup)
                else:
                    yield from self.render_text(node.content)
            case "strong" | "em" | "s":
                yield Fragment(node.markup)
                yield from self.make_fragments(node.children)
                yield Fragment(node.markup)
            case "code_inline":
                yield Fragment(node.meta["source"])
            case "softbreak":
                yield Fragment("\n", wordwrap=True)
            case "hardbreak":
                marker = node.meta["source"] if self.bypass else "\n"
                yield Fragment(marker, hard_line_break=True)
            case "html_inline":
                yield self.protect_inline(node.content)
            case "link" if node.markup == "autolink":
                yield self.protect_inline(node.meta["source"])
            case "link" | "image":
                yield from self.render_link_or_image(node)

    @staticmethod
    def render_text(text: str) -> Iterable[Fragment]:
        # Isolate whitespace so flanking placeholders can be trimmed.
        content = text.strip()
        if not content:
            if text:
                yield Fragment(text, wordwrap=True)
            return
        if (leading := len(text) - len(text.lstrip())) > 0:
            yield Fragment(text[:leading], wordwrap=True)
        yield Fragment(content, wordwrap=True)
        if (trailing := len(text.rstrip())) < len(text):
            yield Fragment(text[trailing:], wordwrap=True)

    def protect_inline(self, text: str) -> Fragment:
        fragment = Fragment(text)
        if self.bypass or self.no_placeholders:
            return fragment
        return Fragment("", placeholder_content=[fragment])

    def render_link_or_image(self, node: SyntaxTreeNode) -> Iterable[Fragment]:
        yield Fragment("![" if node.type == "image" else "[")
        yield from self.make_fragments(node.children)
        yield Fragment("]")

        if "reference_suffix" in node.meta:
            suffix = node.meta["reference_suffix"]
            if suffix and suffix != "[]":
                label = self.translate_subattribute(suffix[1:-1], "link-label")
                fragments = [
                    Fragment("["),
                    Fragment(label, wordwrap=True),
                    Fragment("]"),
                ]
            else:
                if suffix:
                    yield Fragment(suffix)
                return
        else:
            fragments = [Fragment("("), Fragment(node.meta["destination"])]
            fragments.extend(self.title_fragments(node))
            fragments.append(Fragment(")"))

        if self.bypass or self.no_placeholders:
            yield from fragments
        else:
            yield Fragment("", placeholder_content=fragments, important=True)

    def translate_subattribute(self, text: str, kind: str) -> str:
        if self.bypass or self.ignore_translation or self.no_placeholders:
            return text
        return self.translate_callback(text, [*self.path, kind], self._current_docpath)

    def title_fragments(self, node: SyntaxTreeNode) -> Iterable[Fragment]:
        if title := node.meta["title"]:
            delimiter = node.meta["title_delimiter"] or '"'
            yield Fragment(" ", wordwrap=True)
            yield Fragment(delimiter)
            yield Fragment(
                self.translate_subattribute(title, "link-title"), wordwrap=True
            )
            yield Fragment(")" if delimiter == "(" else delimiter)

    def render_definition(
        self, node: SyntaxTreeNode, max_line_length: int | None
    ) -> Iterable[str]:
        label = self.translate_subattribute(node.meta["label"], "link-label")
        yield from self.fragments_to_lines(
            chain(
                (
                    Fragment("["),
                    Fragment(label, wordwrap=True),
                    Fragment("]: ", wordwrap=True),
                    Fragment(node.meta["destination"]),
                ),
                self.title_fragments(node),
            ),
            max_line_length,
        )

    def render_blocks(
        self, parent: SyntaxTreeNode, start: int, end: int, max_line_length: int | None
    ) -> Iterable[str]:
        definition_start = None
        list_gap = None
        for node in parent.children:
            assert node.map is not None
            node_start, node_end = node.map
            is_list = node.type in {"ordered_list", "bullet_list"}
            gap = node_start - start
            if list_gap is not None and (not is_list or list_gap == 0):
                gap = min(gap, list_gap)
            for _ in range(gap):
                yield ""
            if node.type == "definition":
                if definition_start is None or node_start != start:
                    definition_start = node_start
                    self._current_docpath = self._build_docpath("link-ref-def")
                yield from self.render_with_location(
                    definition_start, self.render_definition(node, max_line_length)
                )
            elif is_list:
                definition_start = None
                yield from self.render_blocks(
                    node, node_start, node_end, max_line_length
                )
            else:
                definition_start = None
                yield from self.render_with_location(
                    node_start, self.render_block(node, max_line_length)
                )
            start = node_end
            # Retain a single separator after a list. Empty final items absorb
            # following blank lines, as in the existing Markdown output.
            list_gap = int(bool(node[-1].children)) if is_list else None
        gap = end - start
        if list_gap is not None:
            gap = min(gap, list_gap)
        for _ in range(gap):
            yield ""

    def render_with_location(self, line: int, lines: Iterable[str]) -> Iterable[str]:
        self.path.append(f":{line + 1}")
        try:
            yield from lines
        finally:
            self.path.pop()

    def render_block(
        self, node: SyntaxTreeNode, max_line_length: int | None
    ) -> Iterable[str]:
        assert node.map is not None
        start, end = node.map
        match node.type:
            case "paragraph":
                self._current_docpath = self._build_docpath("p")
                yield from self.span_to_lines(node[0].content, max_line_length)
            case "heading":
                yield from self.render_heading(node, max_line_length)
            case "html_block":
                content = node.content.strip()
                if content == "<!-- translate:off -->":
                    self.ignore_translation = True
                elif content == "<!-- translate:on -->":
                    self.ignore_translation = False
                yield from node.content.removesuffix("\n").split("\n")
            case "code_block" | "fence":
                yield from self.render_code(node)
            case "hr":
                yield node.meta["source"]
            case "blockquote":
                yield from self.render_container(
                    node, "blockquote", "> ", "> ", max_line_length
                )
            case "list_item":
                prefix = node.meta.get("prefix", f"{node.info}{node.markup} ")
                yield from self.render_container(
                    node, "li", prefix, " " * len(prefix), max_line_length
                )
            case "table":
                yield from self.render_table(node)
            case _:
                yield from self._lines[start:end]

    def render_container(
        self,
        node: SyntaxTreeNode,
        kind: str,
        prefix: str,
        continuation: str,
        max_line_length: int | None,
    ) -> Iterable[str]:
        assert node.map is not None
        start, end = node.map
        self._enter_container(kind)
        try:
            width = max_line_length - len(continuation) if max_line_length else None
            if kind == "li" and not node.children:
                yield prefix
                return
            lines = self.render_blocks(node, start, end, width)
            yield from self.prefix_lines(lines, prefix, continuation)
        finally:
            self._exit_container()

    def render_heading(
        self, node: SyntaxTreeNode, max_line_length: int | None
    ) -> Iterable[str]:
        self._current_docpath = self._enter_heading(int(node.tag[1:]))
        inline_source = node[0].content
        title, suffix = self._split_explicit_heading_id_tokens(
            self._parse_inline(inline_source, normalized=True)
        )
        source = node.meta["source"]
        if node.markup.startswith("#"):
            text = next(
                iter(self.span_to_lines(inline_source, None, suffix, tokens=title)), ""
            )
            heading = node.markup + (f" {text}" if text else "") + suffix
            match = ATX_HEADING.fullmatch(source)
            if match is not None and match["closing"]:
                heading += f" {match['closing']}"
            yield heading
        else:
            lines = list(
                self.span_to_lines(inline_source, max_line_length, suffix, tokens=title)
            )
            if lines:
                lines[-1] += suffix
            elif suffix:
                lines.append(suffix.lstrip())
            yield from lines
            yield source

    def render_code(self, node: SyntaxTreeNode) -> Iterable[str]:
        content = node.content.removesuffix("\n")
        if self.extract_code_blocks and not self.ignore_translation:
            self._current_docpath = self._build_docpath("code")
            content = self.translate_callback(content, self.path, self._current_docpath)
        if node.type == "code_block":
            yield from self.prefix_lines(content.split("\n"), "    ", "    ")
        else:
            indent = " " * node.meta["indent"]
            fence = indent + node.markup
            yield fence + node.info
            yield from self.prefix_lines(content.split("\n"), indent, indent)
            yield fence

    def render_table(self, node: SyntaxTreeNode) -> Iterable[str]:
        docpath = self._build_docpath("table")
        rows = [row for group in node.children for row in group.children]
        styles = [cell.attrGet("style") for cell in rows[0].children]
        alignment = {"text-align:center": "^", "text-align:right": ">"}
        align = [alignment.get(style, "<") for style in styles]
        widths = [3] * len(styles)
        cells = []
        for row_index, row in enumerate(rows, 1):
            cell_text = []
            sources = chain(
                (cell[0].content for cell in row.children),
                (text.strip() for text in row.meta.get("extra_cells", ())),
            )
            for column_index, source in enumerate(sources, 1):
                self._current_docpath = f"{docpath}/r[{row_index}]/c[{column_index}]"
                lines = self.span_to_lines(source, None)
                text = next(iter(lines), "").replace("|", r"\|")
                cell_text.append(text)
                if column_index > len(widths):
                    align.append("<")
                    widths.append(3)
                widths[column_index - 1] = max(widths[column_index - 1], len(text))
            cells.append(cell_text)

        separator = [
            (":" if style == "^" else "-")
            + "-" * (width - 2)
            + (":" if style in "^>" else "-")
            for width, style in zip(widths, align, strict=True)
        ]
        for index, row_cells in enumerate(cells):
            padded = row_cells + [""] * (len(widths) - len(row_cells))
            yield (
                "| "
                + " | ".join(
                    f"{text:{style}{width}}"
                    for text, width, style in zip(padded, widths, align, strict=True)
                )
                + " |"
            )
            if index == 0:
                yield "| " + " | ".join(separator) + " |"

    @staticmethod
    def prefix_lines(lines: Iterable[str], first: str, following: str) -> Iterable[str]:
        for index, line in enumerate(lines):
            prefixed = (first if index == 0 else following) + line
            yield "" if prefixed.isspace() else prefixed

    @classmethod
    def fragments_to_lines(
        cls,
        fragments: Iterable[Fragment],
        max_line_length: float | None,
        *,
        legacy_html_breaks: bool = False,
    ) -> Iterable[str]:
        if not max_line_length:
            lines = "".join(fragment.text for fragment in fragments).split("\n")
            yield from lines[:-1]
            if lines[-1]:
                yield lines[-1]
            return

        line = ""
        for word in cls.make_words(fragments, legacy_html_breaks=legacy_html_breaks):
            if word == "\n":
                yield line
                line = ""
            elif not line:
                line = word
            elif len(line) + 1 + len(word) <= max_line_length:
                line += f" {word}"
            else:
                yield line
                line = word
        if line:
            yield line

    _whitespace = re.compile(r"\s+")

    @classmethod
    def make_words(
        cls, fragments: Iterable[Fragment], *, legacy_html_breaks: bool = False
    ) -> Iterable[str]:
        word = ""
        for fragment in fragments:
            if fragment.hard_line_break or (
                legacy_html_breaks and fragment.html_soft_break
            ):
                yield word + fragment.text[:-1]
                yield "\n"
                word = ""
            elif fragment.wordwrap:
                first, *rest = cls._whitespace.split(fragment.text)
                word += first
                for part in rest:
                    if word:
                        yield word
                    word = part
            else:
                word += fragment.text
        if word:
            yield word

    def span_to_lines(
        self,
        source: str,
        max_line_length: int | None,
        legacy_heading_suffix: str = "",
        *,
        tokens: list[SyntaxTreeNode] | None = None,
    ) -> Iterable[str]:
        """Render an inline Markdown span, with translation."""
        if tokens is None:
            tokens = self._parse_inline(source, normalized=True)
        # If we're in an ignore section, skip translation
        if self.ignore_translation:
            with self._bypass_rendering():
                fragments = self.make_fragments(tokens)
                # Expand placeholders before rendering
                expanded = list(self.expand_placeholders(fragments))
                return self.fragments_to_lines(
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
                self.fragments_to_lines(content, max_line_length=float("inf"))
            )

            # translate and parse into new fragments. handle hard line breaks.
            if content_md:
                translated_md = self.translate_callback(
                    content_md, self.path, self._current_docpath
                )
                translated_md, translation_found = self._lookup_heading_translation(
                    content_md, translated_md, legacy_heading_suffix
                )
                use_placeholders = placeholders
                if not translation_found and (placeholders or "\n" in source):
                    fallback = self._lookup_span_fallback(
                        content_md,
                        content,
                        placeholders,
                        legacy_heading_suffix,
                        # The unmerged fragments include breaks inside placeholders.
                        try_legacy_breaks="\n" in source
                        and any(fragment.html_soft_break for fragment in fragments),
                    )
                    if fallback is not None:
                        translated_md, use_placeholders = fallback
                translated_md = translated_md.replace("\n", "\\\n").strip(" \t")
                translated_md = self.remove_placeholder_markers(
                    translated_md, use_placeholders
                )
                # Reuse the source tokens when normalization, translation and
                # placeholder restoration reproduce the exact same span.
                if translated_md != source or legacy_heading_suffix:
                    tokens = self._parse_inline(translated_md)
                translated = self.make_fragments(tokens)
                fragments = chain(leader, translated, trailer)

            # expand placeholders and render into final markdown.
            # list-ify to let all generators run before exiting the try/finally block
            expanded = list(self.expand_placeholders(fragments))
            return self.fragments_to_lines(expanded, max_line_length=max_line_length)

    def _lookup_span_fallback(
        self,
        source: str,
        fragments: Iterable[Fragment],
        placeholders: list[Fragment],
        heading_suffix: str,
        *,
        try_legacy_breaks: bool,
    ) -> tuple[str, list[Fragment]] | None:
        """Check expanded keys and keys that used hard breaks beside HTML."""
        if self.lookup_callback is None:
            return None

        checked = {source, source + heading_suffix}
        for legacy in (False, True) if try_legacy_breaks else (False,):
            key = source
            candidates: list[tuple[str, list[Fragment]]] = []
            if legacy:
                key = "\n".join(
                    self.fragments_to_lines(
                        fragments, float("inf"), legacy_html_breaks=True
                    )
                )
                candidates.append((key, placeholders))
            if placeholders:
                expanded = self.remove_placeholder_markers(
                    key, placeholders, legacy_html_breaks=legacy
                )
                candidates.append((expanded, []))

            for key, target_placeholders in candidates:
                for candidate in (key, key + heading_suffix):
                    if candidate in checked:
                        continue
                    checked.add(candidate)
                    target = self.lookup_callback(candidate)
                    if target is None:
                        continue
                    if heading_suffix:
                        target, _suffix = _split_explicit_heading_id(target)
                    if legacy and target == key:
                        # A legacy identity target follows the corrected source
                        # wrapping. Edited targets keep their explicit newlines.
                        return source, placeholders
                    return target, target_placeholders
        return None

    @classmethod
    def merge_adjacent_placeholders(
        cls, fragments: Iterable[Fragment]
    ) -> Iterable[Fragment]:
        """Replaces sequences of placeholders and whitespace with larger placeholders."""
        fragments = list(fragments)
        start = 0
        while start < len(fragments):
            if fragments[start].placeholder_content:
                end = 0
                for j in range(start + 1, len(fragments)):
                    if fragments[j].placeholder_content:
                        end = j + 1
                    elif fragments[j].text.isspace():
                        pass
                    else:
                        break
                if end:
                    chunk = fragments[start:end]
                    placeholder = Fragment("", placeholder_content=chunk)
                    placeholder.important = any(
                        fragment.important for fragment in chunk
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
            if fragments[pos].placeholder_content:
                if fragments[pos].important:
                    break
            elif not fragments[pos].text.isspace():
                break
            pos += 1

        t = len(fragments)
        while t - 1 >= pos:
            if fragments[t - 1].placeholder_content:
                if fragments[t - 1].important:
                    break
            elif not fragments[t - 1].text.isspace():
                break
            t -= 1

        return fragments[:pos], fragments[pos:t], fragments[t:]

    @classmethod
    def insert_placeholder_markers(
        cls, fragments: Iterable[Fragment]
    ) -> list[Fragment]:
        """
        Sets the text of the (top-level) placeholder fragments to "{n}".
        Returns an ordered list of placeholders.
        """
        placeholders = []
        for fragment in fragments:
            content = fragment.placeholder_content
            if content:
                placeholders.append(fragment)
                fragment.text = f"{{{len(placeholders)}}}"

        return placeholders

    def remove_placeholder_markers(
        self,
        markdown: str,
        placeholders: Iterable[Fragment],
        *,
        legacy_html_breaks: bool = False,
    ) -> str:
        """Replaces placeholder markers in the given markdown with placeholder content."""
        for index, placeholder in enumerate(placeholders):
            content = self.expand_placeholders(placeholder.placeholder_content or [])
            content_md = "\n".join(
                self.fragments_to_lines(
                    content, float("inf"), legacy_html_breaks=legacy_html_breaks
                )
            )
            markdown = markdown.replace(f"{{{index + 1}}}", content_md)

        return markdown

    def expand_placeholders(self, fragments: Iterable[Fragment]) -> Iterable[Fragment]:
        """Expands placeholder fragments, recursively."""
        for fragment in fragments:
            content = fragment.placeholder_content
            if content:
                yield from self.expand_placeholders(content)
            else:
                yield fragment
