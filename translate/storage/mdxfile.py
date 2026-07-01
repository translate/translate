#
# Copyright 2024 Zuza Software Foundation
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

"""Conservative MDX storage support built on the Markdown storage."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from translate.storage.markdown import MarkdownFile, MarkdownUnit

if TYPE_CHECKING:
    from collections.abc import Iterator

_COMPONENT_NAME = r"[A-Z][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*"
_ATTRIBUTE_NAME = r"[A-Za-z_:][A-Za-z0-9_.:-]*"
_QUOTED_VALUE = r'(?:"[^"\r\n]*"|\'[^\'\r\n]*\')'
_ATTRIBUTE = rf"\s+{_ATTRIBUTE_NAME}(?:\s*=\s*{_QUOTED_VALUE})?"

_COMPONENT_START = re.compile(rf"^<(?P<name>{_COMPONENT_NAME})(?=[\s/>]|$)")
_COMPONENT_CLOSE = re.compile(rf"^</(?P<name>{_COMPONENT_NAME})\s*>[ \t]*$")
_FRAGMENT_START = re.compile(r"^(?:<>|</>)")
_SIMPLE_TAG = re.compile(
    rf"^<(?P<name>{_COMPONENT_NAME})(?P<attrs>(?:{_ATTRIBUTE})*)"
    rf"\s*(?P<slash>/?)>[ \t]*$"
)
_ATTRIBUTE_TOKEN = re.compile(
    rf"\s+(?P<name>{_ATTRIBUTE_NAME})"
    rf"(?:\s*=\s*(?:\"(?P<double>[^\"\r\n]*)\"|'(?P<single>[^'\r\n]*)'))?"
)
_ESM_START = re.compile(
    r"""^(?:
        import \s+ (?:
            \{|\*|type\s|\"|\'|`
            |[A-Za-z_$][A-Za-z0-9_$]*\s*,\s*(?:\*|\{)
            |[A-Za-z_$][A-Za-z0-9_$]*\s+from\b
        )
        |
        export \s+ (?:default|const|function|class|type|let|var|\{|\*)
    )""",
    re.VERBOSE,
)
_FENCE = re.compile(r"^ {0,3}(?P<delimiter>`{3,}|~{3,})")
_LOWER_HTML_START = re.compile(r"^ {0,3}<(?P<tag>[a-z][A-Za-z0-9-]*)(?:[\s>/]|$)")


class MDXUnit(MarkdownUnit):
    """A unit of translatable/localisable MDX content."""


class MDXFile(MarkdownFile):
    """Parse a deliberately small, structurally isolated MDX subset."""

    UnitClass = MDXUnit

    def __init__(
        self,
        inputfile=None,
        callback=None,
        max_line_length=None,
        extract_code_blocks=True,
        extract_frontmatter=True,
        frontmatter_translate_values=False,
        no_placeholders=False,
    ) -> None:
        """Construct an MDX store with the same options as MarkdownFile."""
        self._mdx_blocks: dict[str, tuple[str, int]] = {}
        self._mdx_block_counter = 0
        self._mdx_block_placeholder_prefix = "MDX_BLOCK"
        self._jsx_attr_counter = 0
        self._jsx_block_counter = 0
        super().__init__(
            inputfile=inputfile,
            callback=callback,
            max_line_length=max_line_length,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
            frontmatter_translate_values=frontmatter_translate_values,
            no_placeholders=no_placeholders,
        )

    def parse(self, data) -> None:
        """Protect MDX syntax, parse Markdown, and restore protected content."""
        self._mdx_blocks = {}
        self._mdx_block_counter = 0
        self._jsx_attr_counter = 0
        self._jsx_block_counter = 0

        text = data.decode() if isinstance(data, bytes) else data
        self._mdx_block_placeholder_prefix = self._choose_placeholder_prefix(text)
        frontmatter_offset = self._frontmatter_body_offset(text.split("\n"))
        super().parse(self._protect_mdx(text).encode())
        self.units.sort(
            key=lambda unit: self._unit_document_line(unit, frontmatter_offset)
        )
        self.filesrc = self._restore_mdx_blocks(self.filesrc)

    def _protect_mdx(self, text: str) -> str:
        """Replace recognized MDX blocks with line-count-preserving comments."""
        lines = text.split("\n")
        frontmatter_lines = self._frontmatter_line_count(lines)
        result = lines[:frontmatter_lines]
        i = frontmatter_lines
        fence: tuple[str, int] | None = None

        while i < len(lines):
            line = lines[i]

            if fence is not None:
                result.append(line)
                if self._is_fence_close(line, fence):
                    fence = None
                i += 1
                continue

            opening_fence = self._fence_open(line)
            if opening_fence is not None:
                fence = opening_fence
                result.append(line)
                i += 1
                continue

            if self._is_indented_code(line):
                result.append(line)
                i += 1
                continue

            if not line.strip():
                result.append(line)
                i += 1
                continue

            if line.strip() == "<!-- translate:off -->":
                end = self._translate_off_end(lines, i)
                result.append(self._opaque_lines(lines, i, end))
                i = end
                continue

            raw_end = self._raw_html_end(lines, i)
            if raw_end is not None:
                result.append(self._opaque_lines(lines, i, raw_end))
                i = raw_end
                continue

            if self._is_esm_start(line):
                end = self._blank_delimited_end(lines, i)
                result.append(self._opaque_lines(lines, i, end))
                i = end
                continue

            component = _COMPONENT_START.match(line)
            if component is not None:
                end, rendered = self._component_block(lines, i, component.group("name"))
                result.append(
                    self._make_placeholder(rendered, source_line_count=end - i)
                )
                i = end
                continue

            if _COMPONENT_CLOSE.fullmatch(
                self._logical_line(line)
            ) or _FRAGMENT_START.match(self._logical_line(line)):
                end = self._extend_to_blank(lines, i + 1)
                result.append(self._opaque_lines(lines, i, end))
                i = end
                continue

            end = self._blank_delimited_end(lines, i)
            if self._chunk_requires_opaque(lines[i:end]):
                result.append(self._opaque_lines(lines, i, end))
            else:
                result.extend(lines[i:end])
            i = end

        return "\n".join(result)

    def _component_block(
        self, lines: list[str], start: int, name: str
    ) -> tuple[int, str]:
        """Return the end and rendering of one column-zero component block."""
        opening = lines[start]
        simple = _SIMPLE_TAG.fullmatch(self._logical_line(opening))
        if simple is not None and simple.group("slash"):
            end = start + 1
            if self._is_block_end(lines, end):
                return end, self._translate_simple_tag(opening, start + 1)
            end = self._extend_to_blank(lines, end)
            return end, "\n".join(lines[start:end])

        first_close = self._first_standalone_close(lines, start + 1, name)
        if (
            simple is not None
            and first_close is not None
            and self._is_block_end(lines, first_close + 1)
        ):
            child_lines = lines[start + 1 : first_close]
            if self._simple_markdown_children(child_lines):
                return first_close + 1, self._render_simple_component(
                    opening,
                    child_lines,
                    lines[first_close],
                    start,
                )

        end = self._opaque_component_end(lines, start, name)
        end = self._extend_to_blank(lines, end)
        return end, "\n".join(lines[start:end])

    def _render_simple_component(
        self,
        opening: str,
        child_lines: list[str],
        closing: str,
        opening_index: int,
    ) -> str:
        """Translate one simple component as an isolated Markdown subdocument."""
        translated_opening = self._translate_simple_tag(opening, opening_index + 1)
        self._jsx_block_counter += 1
        if not child_lines:
            return f"{translated_opening}\n{closing}"

        indent = self._common_child_indent(child_lines)
        dedented_lines = [line[indent:] for line in child_lines]
        child_store = MarkdownFile(
            callback=self.callback,
            max_line_length=self.max_line_length,
            extract_code_blocks=self.extract_code_blocks,
            extract_frontmatter=False,
            no_placeholders=self.no_placeholders,
        )
        child_store.parse("\n".join(dedented_lines).encode())

        self._copy_child_units(child_store, opening_index + 2)
        rendered_children = self._reindent(child_store.filesrc, " " * indent)
        if rendered_children and not rendered_children.endswith("\n"):
            rendered_children += "\n"
        return f"{translated_opening}\n{rendered_children}{closing}"

    def _copy_child_units(self, child_store: MarkdownFile, first_line: int) -> None:
        """Copy isolated Markdown units into this store with absolute locations."""
        path_prefix = f"jsx-block[{self._jsx_block_counter}]"
        for child_unit in child_store.units:
            unit = self.addsourceunit(child_unit.source)
            relative_line = self._unit_source_line(child_unit) or 1
            unit.addlocation(f"{self.filename or ''}:{first_line + relative_line - 1}")
            child_path = child_unit.getdocpath()
            unit.setdocpath(
                f"{path_prefix}/{child_path}" if child_path else path_prefix
            )

    def _translate_simple_tag(self, tag: str, line_number: int) -> str:
        """Translate quoted values in a validated simple component tag."""
        logical_tag = self._logical_line(tag)
        match = _SIMPLE_TAG.fullmatch(logical_tag)
        if match is None:
            return tag

        result: list[str] = []
        pos = 0
        attrs_start, attrs_end = match.span("attrs")
        for attribute in _ATTRIBUTE_TOKEN.finditer(logical_tag, attrs_start, attrs_end):
            value_group = (
                "double" if attribute.group("double") is not None else "single"
            )
            if attribute.group(value_group) is None:
                continue
            value_start, value_end = attribute.span(value_group)
            quote = '"' if value_group == "double" else "'"
            result.append(tag[pos:value_start])
            translated = self._translate_attribute(
                tag[value_start:value_end],
                match.group("name"),
                attribute.group("name"),
                line_number,
            )
            result.append(
                self._escape_attribute(
                    translated,
                    quote,
                    changed=translated != tag[value_start:value_end],
                )
            )
            pos = value_end
        result.append(tag[pos:])
        return "".join(result)

    def _translate_attribute(
        self, value: str, component: str, attribute: str, line_number: int
    ) -> str:
        """Emit one quoted component attribute and return its translation."""
        self._jsx_attr_counter += 1
        if not value.strip():
            return value
        unit = self.addsourceunit(value)
        unit.addlocation(f"{self.filename or ''}:{line_number}")
        unit.setdocpath(f"jsx-attr[{self._jsx_attr_counter}]/{component}.@{attribute}")
        return self.callback(value)

    @staticmethod
    def _escape_attribute(value: str, quote: str, *, changed: bool) -> str:
        """Encode the active delimiter as a JSX-compatible character entity."""
        entity = "&quot;" if quote == '"' else "&apos;"
        value = value.replace(quote, entity)
        if changed:
            value = value.replace("<", "&lt;")
            trailing_backslashes = len(value) - len(value.rstrip("\\"))
            if trailing_backslashes % 2:
                value += "\\"
        return value

    @classmethod
    def _simple_markdown_children(cls, lines: list[str]) -> bool:
        """Accept child Markdown only when it contains no MDX structure."""
        nonblank = [line for line in lines if line.strip()]
        if not nonblank:
            return True
        if any("\t" in line[: len(line) - len(line.lstrip())] for line in nonblank):
            return False
        if cls._common_child_indent(lines) >= 4:
            return False
        if nonblank[0].lstrip().startswith("---"):
            return False
        if any(
            _LOWER_HTML_START.match(line) is not None
            or cls._raw_html_end(lines, index) is not None
            for index, line in enumerate(lines)
        ):
            return False

        for _, line in cls._structural_lines(lines):
            if (
                re.search(
                    r"</?[A-Z][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*",
                    line,
                )
                or "<>" in line
                or "</>" in line
                or "{" in line
                or "}" in line
                or cls._is_esm_start(line.lstrip())
            ):
                return False
        return True

    @staticmethod
    def _common_child_indent(lines: list[str]) -> int:
        """Return the common leading-space indentation of nonblank children."""
        indents = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
        return min(indents, default=0)

    @staticmethod
    def _reindent(text: str, prefix: str) -> str:
        """Restore a component child's structural indentation after rendering."""
        if not prefix:
            return text
        return "".join(
            f"{prefix}{line}" if line.strip() else line
            for line in text.splitlines(keepends=True)
        )

    @classmethod
    def _first_standalone_close(
        cls, lines: list[str], start: int, name: str
    ) -> int | None:
        """Find the first exact, column-zero closing line for a component."""
        for index, line in cls._structural_lines(lines, start):
            closing = _COMPONENT_CLOSE.fullmatch(line)
            if closing is not None and closing.group("name") == name:
                return index
        return None

    @classmethod
    def _opaque_component_end(cls, lines: list[str], start: int, name: str) -> int:
        """Conservatively collect unsupported component syntax as one block."""
        depth = 1
        for index, line in cls._structural_lines(lines, start + 1):
            if cls._is_opaque_same_name_open(line, name):
                depth += 1
                continue
            closing = _COMPONENT_CLOSE.fullmatch(line)
            if closing is not None and closing.group("name") == name:
                depth -= 1
                if depth == 0:
                    return index + 1
        return cls._blank_delimited_end(lines, start)

    @classmethod
    def _structural_lines(
        cls, lines: list[str], start: int = 0
    ) -> Iterator[tuple[int, str]]:
        """Yield logical lines outside fenced code and raw HTML blocks."""
        fence: tuple[str, int] | None = None
        index = start
        while index < len(lines):
            line = lines[index]
            if fence is not None:
                if cls._is_fence_close(line, fence):
                    fence = None
                index += 1
                continue
            fence = cls._fence_open(line)
            if fence is not None:
                index += 1
                continue
            raw_html_end = cls._raw_html_end(lines, index)
            if raw_html_end is not None:
                index = raw_html_end
                continue
            yield index, cls._logical_line(line)
            index += 1

    @staticmethod
    def _is_opaque_same_name_open(line: str, name: str) -> bool:
        """Recognize a complete same-name opening line without parsing its attrs."""
        opening = _COMPONENT_START.match(line)
        if opening is None or opening.group("name") != name:
            return False
        stripped = line.rstrip()
        if not stripped.endswith(">") or stripped.endswith("/>"):
            return False
        closing = re.compile(rf"</\s*{re.escape(name)}\s*>")
        return closing.search(line, opening.end()) is None

    @staticmethod
    def _logical_line(line: str) -> str:
        """Remove the CR from a CRLF line for syntax recognition."""
        return line.removesuffix("\r")

    def _opaque_lines(self, lines: list[str], start: int, end: int) -> str:
        """Create a placeholder for a source line range."""
        return self._make_placeholder(
            "\n".join(lines[start:end]), source_line_count=end - start
        )

    def _make_placeholder(
        self, content: str, source_line_count: int | None = None
    ) -> str:
        """Create a collision-resistant HTML comment placeholder."""
        self._mdx_block_counter += 1
        key = f"<!-- {self._mdx_block_placeholder_prefix}_{self._mdx_block_counter} -->"
        padding_lines = (
            content.count("\n")
            if source_line_count is None
            else max(source_line_count - 1, 0)
        )
        self._mdx_blocks[key] = (content, padding_lines)
        return key + ("\n" * padding_lines)

    def _restore_mdx_blocks(self, text: str) -> str:
        """Restore all opaque and rendered MDX blocks."""
        for key, (content, padding_lines) in self._mdx_blocks.items():
            text = text.replace(key + ("\n" * padding_lines), content)
            text = text.replace(key, content)
        return text

    @staticmethod
    def _choose_placeholder_prefix(text: str) -> str:
        """Choose a placeholder prefix not present in user content."""
        prefix = "MDX_BLOCK"
        counter = 1
        while f"<!-- {prefix}_" in text:
            prefix = f"MDX_BLOCK_{counter}"
            counter += 1
        return prefix

    @staticmethod
    def _frontmatter_line_count(lines: list[str]) -> int:
        """Return the number of leading YAML front matter lines."""
        if not lines or not lines[0].startswith("---"):
            return 0
        for line_number, line in enumerate(lines[1:], start=1):
            if line.startswith(("---", "...")):
                return line_number + 1
        return 0

    @classmethod
    def _frontmatter_body_offset(cls, lines: list[str]) -> int:
        """Return the line offset used by Markdown body unit locations."""
        offset = cls._frontmatter_line_count(lines)
        if offset and offset < len(lines) and not lines[offset].strip():
            offset += 1
        return offset

    @staticmethod
    def _blank_delimited_end(lines: list[str], start: int) -> int:
        """Return the first blank line after a conservative opaque block."""
        end = start + 1
        while end < len(lines) and lines[end].strip():
            end += 1
        return end

    @classmethod
    def _extend_to_blank(cls, lines: list[str], end: int) -> int:
        """Extend a non-isolated construct through its Markdown block."""
        if cls._is_block_end(lines, end):
            return end
        return cls._blank_delimited_end(lines, end)

    @staticmethod
    def _is_block_end(lines: list[str], end: int) -> bool:
        """Return whether a construct ends at EOF or before a blank line."""
        return end >= len(lines) or not lines[end].strip()

    @classmethod
    def _chunk_requires_opaque(cls, lines: list[str]) -> bool:
        """Reject an ordinary Markdown block containing structural MDX."""
        for line in lines:
            logical_line = cls._logical_line(line)
            if (
                _COMPONENT_START.match(logical_line)
                or _COMPONENT_CLOSE.fullmatch(logical_line)
                or _FRAGMENT_START.match(logical_line)
                or cls._is_esm_start(line)
            ):
                return True
            if (
                not cls._is_indented_code(line)
                and not re.match(r"(?:>|[-+*]\s|\d+[.)]\s)", line.lstrip())
                and ("{" in line or "}" in line)
            ):
                return True
        return False

    @staticmethod
    def _is_indented_code(line: str) -> bool:
        """Return whether a line has top-level Markdown code indentation."""
        column = 0
        for character in line:
            if character == " ":
                column += 1
            elif character == "\t":
                column += 4 - (column % 4)
            else:
                break
        return column >= 4

    @staticmethod
    def _translate_off_end(lines: list[str], start: int) -> int:
        """Collect an exact translation-control region through translate:on."""
        for index in range(start + 1, len(lines)):
            if lines[index].strip() == "<!-- translate:on -->":
                return index + 1
        return len(lines)

    @staticmethod
    def _is_esm_start(line: str) -> bool:
        """Recognize a top-level MDX ESM statement without parsing JavaScript."""
        return line == line.lstrip() and _ESM_START.match(line) is not None

    @staticmethod
    def _fence_open(line: str) -> tuple[str, int] | None:
        """Return the character and length of a top-level Markdown fence."""
        match = _FENCE.match(line)
        if match is None:
            return None
        delimiter = match.group("delimiter")
        return delimiter[0], len(delimiter)

    @staticmethod
    def _is_fence_close(line: str, fence: tuple[str, int]) -> bool:
        """Return whether a line closes the active Markdown fence."""
        character, length = fence
        match = re.fullmatch(r" {0,3}(`{3,}|~{3,})\s*", line)
        return bool(
            match and match.group(1)[0] == character and len(match.group(1)) >= length
        )

    @classmethod
    def _raw_html_end(cls, lines: list[str], start: int) -> int | None:
        """Return the end of raw HTML that must remain opaque to JSX scanning."""
        line = lines[start]
        stripped = line.lstrip(" ")
        if len(line) - len(stripped) > 3:
            return None

        if stripped.startswith("<!--"):
            return cls._marker_end(lines, start, "-->")
        if stripped.startswith("<?"):
            return cls._marker_end(lines, start, "?>")
        if stripped.startswith("<![CDATA["):
            return cls._marker_end(lines, start, "]]>")
        if re.match(r"<![A-Za-z]", stripped):
            return cls._marker_end(lines, start, ">")

        match = _LOWER_HTML_START.match(line)
        if match is None:
            return None
        tag = match.group("tag")
        if re.search(rf"</\s*{re.escape(tag)}\s*>", line, re.IGNORECASE):
            return None
        if line.rstrip().endswith("/>"):
            return None
        if tag.lower() in {"pre", "script", "style", "textarea"}:
            return cls._marker_end(lines, start, f"</{tag}>", ignore_case=True)
        return cls._blank_delimited_end(lines, start)

    @staticmethod
    def _marker_end(
        lines: list[str],
        start: int,
        marker: str,
        *,
        ignore_case: bool = False,
    ) -> int:
        """Collect through a literal raw-HTML terminator or end of file."""
        needle = marker.lower() if ignore_case else marker
        for index in range(start, len(lines)):
            haystack = lines[index].lower() if ignore_case else lines[index]
            if needle in haystack:
                return index + 1
        return len(lines)

    @staticmethod
    def _unit_source_line(unit: MarkdownUnit) -> int:
        """Return the numeric source line used for stable unit ordering."""
        for location in unit.getlocations():
            match = re.search(r":(\d+)$", location)
            if match:
                return int(match.group(1))
        return 0

    @classmethod
    def _unit_document_line(cls, unit: MarkdownUnit, frontmatter_offset: int) -> int:
        """Return an absolute source line for document-order sorting."""
        line = cls._unit_source_line(unit)
        docpath = unit.getdocpath() or ""
        if docpath.startswith("frontmatter"):
            return 0
        if docpath.startswith("jsx-"):
            return line
        return line + frontmatter_offset
