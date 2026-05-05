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

"""
Module for parsing MDX files for translation.

MDX is Markdown with JSX support. This module extends the Markdown parser to
handle MDX-specific syntax:

- import/export statements are preserved as-is (not translated)
- JSX block-level components are preserved as-is (not translated)
- Standalone JSX expression blocks on their own line ({expr}) are preserved
- Regular Markdown content between JSX blocks is extracted for translation
- Inline {expr} inside a paragraph is kept as-is (part of the translation unit)

See: https://mdxjs.com/docs/what-is-mdx/
"""

from __future__ import annotations

import re

from translate.storage.markdown import MarkdownFile, MarkdownUnit


class MDXUnit(MarkdownUnit):
    """A unit of translatable/localisable MDX content."""


class MDXFile(MarkdownFile):
    """Parser for MDX files (Markdown with JSX)."""

    UnitClass = MDXUnit

    def __init__(
        self,
        inputfile=None,
        callback=None,
        max_line_length=None,
        extract_code_blocks=True,
        extract_frontmatter=True,
        no_placeholders=False,
    ) -> None:
        """
        Construct a new MDXFile instance.

        Parameters are the same as MarkdownFile. JSX components and
        import/export statements are automatically preserved without
        translation.
        """
        # Storage for MDX blocks that are replaced with placeholders
        self._mdx_blocks: dict[str, tuple[str, int]] = {}
        self._mdx_block_counter = 0
        super().__init__(
            inputfile=inputfile,
            callback=callback,
            max_line_length=max_line_length,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
            no_placeholders=no_placeholders,
        )

    def parse(self, data) -> None:
        """Pre-process MDX content, then delegate to the Markdown parser."""
        # Reset placeholder state so repeated parse() calls don't accumulate
        # stale entries from a previous pass.
        self._mdx_blocks = {}
        self._mdx_block_counter = 0
        text = data.decode() if isinstance(data, bytes) else data
        text = self._protect_mdx_blocks(text)
        super().parse(text.encode())
        # Restore MDX blocks in the rendered output
        self.filesrc = self._restore_mdx_blocks(self.filesrc)

    def _make_placeholder(self, content: str) -> str:
        """
        Create an HTML comment placeholder for an MDX block.

        HTML comments are used because they are preserved verbatim by the
        Markdown parser and are not extracted as translation units.

        The placeholder pads to the same number of lines as the original block
        so that extracted PO ``#: file:line`` locations remain accurate.
        Indentation is *not* embedded in the placeholder because the Markdown
        renderer may alter leading whitespace; it is instead recovered from the
        stored *content* when ``_restore_mdx_blocks`` runs.
        """
        self._mdx_block_counter += 1
        key = f"<!-- MDX_BLOCK_{self._mdx_block_counter} -->"
        n_lines = content.count("\n")
        self._mdx_blocks[key] = (content, n_lines)
        # Pad to the same number of lines as the original block so that
        # downstream line-number references (PO locations) stay accurate.
        return key + ("\n" * n_lines)

    def _protect_mdx_blocks(self, text: str) -> str:
        """
        Replace MDX-specific blocks with HTML comment placeholders.

        This allows the standard Markdown parser to handle the rest of the
        content without being confused by JSX syntax.

        Lines inside fenced code blocks (``` or ~~~) are never protected so
        that JSX-like examples inside code samples are left intact.
        """
        lines = text.split("\n")
        result = []
        i = 0
        in_code_fence = False
        code_fence_char = ""
        code_fence_len = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Track fenced code blocks so we never protect content inside them.
            if not in_code_fence:
                fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
                if fence_match:
                    in_code_fence = True
                    code_fence_char = fence_match.group(1)[0]
                    code_fence_len = len(fence_match.group(1))
                    result.append(line)
                    i += 1
                    continue
            else:
                # Closing fence: same character, length >= opening length,
                # nothing after except optional whitespace (CommonMark §4.5).
                close_match = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
                if (
                    close_match
                    and close_match.group(1)[0] == code_fence_char
                    and len(close_match.group(1)) >= code_fence_len
                ):
                    in_code_fence = False
                    code_fence_char = ""
                    code_fence_len = 0
                result.append(line)
                i += 1
                continue

            # Import/export statements (may span multiple lines with parens/braces).
            # Require a recognisable MDX import/export form to avoid treating
            # normal paragraphs that begin with the word "import" or "export" as
            # code blocks.
            #
            # Recognised import forms:
            #   import { ... } from '...'
            #   import * as x from '...'
            #   import type ...
            #   import DefaultExport from '...'  (identifier immediately followed
            #     by "from" somewhere on the line)
            #   import '...' (side-effect-only)
            #
            # Recognised export forms:
            #   export default ...
            #   export const/function/class/type/let/var ...
            #   export { ... }
            #   export * from '...'
            if re.match(
                r"""^(?:
                    import \s+ (?:\{|\*|type\s|\"|\'|`|[A-Za-z_$][A-Za-z0-9_$]*\s+from\b)
                    |
                    export \s+ (?:default|const|function|class|type|let|var|\{|\*)
                )""",
                stripped,
                re.VERBOSE,
            ):
                block_lines = [line]
                # Collect continuation lines until the statement is complete.
                # The cap guards against a malformed file with a never-closing
                # brace consuming the entire rest of the file.  On hitting the
                # cap we emit the collected lines as ordinary Markdown (fail
                # open) rather than silently dropping all subsequent content.
                MAX_IMPORT_LINES = 200
                while (
                    i + 1 < len(lines)
                    and len(block_lines) < MAX_IMPORT_LINES
                    and self._is_continuation("\n".join(block_lines))
                ):
                    i += 1
                    block_lines.append(lines[i])
                if self._is_continuation("\n".join(block_lines)):
                    # Still open at cap — treat as regular Markdown.
                    result.extend(block_lines)
                    i += 1
                    continue
                result.append(self._make_placeholder("\n".join(block_lines)))
                i += 1
                continue

            # JSX block-level component (starts with <UpperCase)
            if re.match(r"^[ \t]*<[A-Z]", line) or re.match(r"^[ \t]*</[A-Z]", line):
                block_lines = [line]
                # Self-closing tag on one line
                if re.search(r"/>\s*$", stripped):
                    result.append(self._make_placeholder("\n".join(block_lines)))
                    i += 1
                    continue
                # Opening tag - find corresponding closing tag
                tag_match = re.match(r"^[ \t]*<([A-Z][A-Za-z0-9_.]*)", line)
                if tag_match:
                    tag_name = tag_match.group(1)
                    # Check if opening tag closes on same line with >
                    # then look for </TagName>
                    depth = 1
                    # Check if this line itself has content after the opening tag
                    # that includes the closing tag
                    close_pattern = re.compile(rf"</\s*{re.escape(tag_name)}\s*>")
                    open_pattern = re.compile(rf"<{re.escape(tag_name)}(?:\s|>)")
                    selfclose_pattern = re.compile(
                        rf"<{re.escape(tag_name)}(?:\s[^>]*)?\s*/>"
                    )
                    # Count opens/closes on first line
                    first_line_closes = len(close_pattern.findall(stripped))
                    first_line_opens = len(open_pattern.findall(stripped)) - len(
                        selfclose_pattern.findall(stripped)
                    )
                    depth = first_line_opens - first_line_closes
                    if depth <= 0:
                        # Entire component on one line
                        result.append(self._make_placeholder("\n".join(block_lines)))
                        i += 1
                        continue
                    # Multi-line component: collect lines until the matching
                    # closing tag is found. If we reach EOF without closing
                    # (malformed MDX), fall back to emitting the first line
                    # as a placeholder and re-processing the rest, so that
                    # content after the unclosed tag is not silently dropped.
                    while i + 1 < len(lines) and depth > 0:
                        i += 1
                        block_lines.append(lines[i])
                        current = lines[i]
                        depth += len(open_pattern.findall(current)) - len(
                            selfclose_pattern.findall(current)
                        )
                        depth -= len(close_pattern.findall(current))
                    if depth > 0:
                        # Unclosed tag: protect only the opening line and
                        # re-process the remaining lines normally.
                        result.append(self._make_placeholder(block_lines[0]))
                        lines = block_lines[1:] + lines[i + 1 :]
                        i = 0
                        continue
                    result.append(self._make_placeholder("\n".join(block_lines)))
                    i += 1
                    continue
                # Closing tag alone - just protect it
                result.append(self._make_placeholder("\n".join(block_lines)))
                i += 1
                continue

            # JSX expression blocks (lines that are just {expression})
            if re.match(r"^[ \t]*\{", stripped) and not re.match(
                r"^[ \t]*\{[{%]", stripped
            ):
                # Check if it's a standalone JSX expression block
                brace_count = stripped.count("{") - stripped.count("}")
                if brace_count == 0 and stripped.endswith("}"):
                    result.append(self._make_placeholder(line))
                    i += 1
                    continue
                if brace_count > 0:
                    # Multi-line expression: collect lines until braces balance.
                    # Cap guards against a never-closing brace in malformed MDX
                    # consuming the entire file.  Fail open on hitting the cap.
                    block_lines = [line]
                    MAX_EXPR_LINES = 200
                    while (
                        i + 1 < len(lines)
                        and brace_count > 0
                        and len(block_lines) < MAX_EXPR_LINES
                    ):
                        i += 1
                        block_lines.append(lines[i])
                        brace_count += lines[i].count("{") - lines[i].count("}")
                    if brace_count > 0:
                        # Still unclosed at cap — treat as regular Markdown.
                        result.extend(block_lines)
                        i += 1
                        continue
                    result.append(self._make_placeholder("\n".join(block_lines)))
                    i += 1
                    continue

            result.append(line)
            i += 1

        return "\n".join(result)

    def _restore_mdx_blocks(self, text: str) -> str:
        r"""
        Restore MDX blocks from their placeholders.

        Each placeholder was emitted as ``key + "\n" * n_lines`` so that the
        block occupied the same number of lines as the original content.  On
        restoration, both the key and the padding newlines are replaced with
        the original content to avoid doubling blank lines.
        """
        for key, (content, n_lines) in self._mdx_blocks.items():
            text = text.replace(key + ("\n" * n_lines), content)
            # Fallback: replace any remaining bare key (e.g. if the Markdown
            # renderer stripped trailing whitespace/newlines).
            text = text.replace(key, content)
        return text

    @staticmethod
    def _is_continuation(text: str) -> bool:
        """
        Check if a multi-line import/export is incomplete.

        Note: brace and parenthesis counts are naive — characters inside string
        literals are not excluded. Import paths containing unbalanced brace or
        paren characters (e.g. ``import x from './path/{section'``) may
        incorrectly trigger continuation. This is an accepted limitation of
        regex-based parsing.
        """
        # Unclosed braces
        if text.count("{") > text.count("}"):
            return True
        # Unclosed parentheses
        if text.count("(") > text.count(")"):
            return True
        # Line ends with a comma (continuation)
        return text.rstrip().endswith(",")
