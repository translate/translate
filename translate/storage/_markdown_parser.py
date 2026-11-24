"""Capture the source syntax needed to render translated Markdown."""

from __future__ import annotations

import re
from functools import cache
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt, rules_block, rules_inline
from markdown_it.helpers import parseLinkDestination, parseLinkLabel, parseLinkTitle
from markdown_it.parser_block import ParserBlock
from markdown_it.rules_block.table import escapedSplit

if TYPE_CHECKING:
    from markdown_it.parser_block import RuleFuncBlockType
    from markdown_it.parser_inline import RuleFuncInlineType
    from markdown_it.rules_block.state_block import StateBlock
    from markdown_it.rules_inline.state_inline import StateInline


ATX_HEADING = re.compile(
    r"^ {0,3}(?P<marker>#{1,6})(?:[ \t]+(?P<title>(?!#+[ \t]*$)[^ \t].*?))?"
    r"(?:[ \t]+(?P<closing>#+))?[ \t]*$"
)
_LIST_MARKER = re.compile(r" *(?:\d{1,9}[.)]|[-+*])(?P<space>[ \t]*)")
_REFERENCE_LABEL = re.compile(r"^[ \t]*\[((?:\\[\s\S]|[^\\\]])*)\]:")


class _MarkdownParser(MarkdownIt):
    def validateLink(self, url: str) -> bool:
        # Preserve destinations in Markdown. The HTML renderer's URL filter
        # would otherwise classify some existing PO placeholders as plain text.
        return True


class _MarkdownBlockParser(ParserBlock):
    def tokenize(self, state: StateBlock, startLine: int, endLine: int) -> None:
        if state.level >= state.md.options.maxNesting:
            line = state.skipEmptyLines(startLine)
            if line < endLine and state.sCount[line] >= state.blkIndent:
                state.env["nesting_limit_reached"] = True
        if state.tokens and state.tokens[-1].type == "blockquote_open":
            # The toolkit has historically extracted quoted Setext headings as
            # paragraphs. Preserve those source strings and document paths.
            outer_quote = state.env.get("inside_blockquote", False)
            state.env["inside_blockquote"] = True
            try:
                super().tokenize(state, startLine, endLine)
            finally:
                state.env["inside_blockquote"] = outer_quote
        else:
            super().tokenize(state, startLine, endLine)


def _link_target(source: str) -> tuple[str, str, str]:
    """Recover the decoded destination and title with their delimiters."""
    source = source.lstrip(" \t\n")
    result = parseLinkDestination(source, 0, len(source))
    if not result.ok:
        return "", "", ""
    destination = result.str
    if source.startswith("<"):
        destination = f"<{destination}>"
    title_source = source[result.pos :].lstrip(" \t\n")
    title = parseLinkTitle(title_source, 0, len(title_source), None)
    return destination, title_source[:1], title.str if title.ok else ""


def _capture_inline(rule: RuleFuncInlineType, kind: str) -> RuleFuncInlineType:
    def capture(state: StateInline, silent: bool) -> bool:
        start = state.pos
        first = len(state.tokens)
        matched = rule(state, silent)
        if not matched or silent or first == len(state.tokens):
            return matched

        # Pushing a new token can flush pending text first.
        token = state.tokens[first]
        if token.type == "text":
            token = state.tokens[first + 1]
        if token.type != kind:
            return matched

        if kind == "hardbreak":
            if state.src[start] == "\\":
                token.meta["source"] = "\\\n"
            else:
                pos = start
                while pos and state.src[pos - 1] == " ":
                    pos -= 1
                token.meta["source"] = state.src[pos : start + 1]
        elif kind == "code_inline":
            token.meta["source"] = state.src[start : state.pos].replace("\n", " ")
        elif token.markup == "autolink":
            token.meta["source"] = state.src[start : state.pos]
        else:
            is_link = kind == "link_open"
            label_end = parseLinkLabel(state, start if is_link else start + 1, is_link)
            suffix = state.src[label_end + 1 : state.pos]
            if "label" in token.meta:
                token.meta["reference_suffix"] = suffix
            else:
                dest, delimiter, title = _link_target(suffix[1:-1])
                token.meta.update(
                    destination=dest, title_delimiter=delimiter, title=title
                )

        return matched

    return capture


def _capture_block(rule: RuleFuncBlockType) -> RuleFuncBlockType:
    def capture(state: StateBlock, start: int, end: int, silent: bool) -> bool:
        if rule is rules_block.lheading and state.env.get("inside_blockquote"):
            return False
        first = len(state.tokens)
        matched = rule(state, start, end, silent)
        if not matched or silent or first == len(state.tokens):
            return matched

        token = state.tokens[first]
        assert token.map is not None
        if token.type == "definition":
            source = state.getLines(start, token.map[1], state.blkIndent, False)
            match = _REFERENCE_LABEL.match(source)
            assert match is not None
            dest, delimiter, title = _link_target(source[match.end() :])
            token.meta.update(
                label=match[1], destination=dest, title_delimiter=delimiter, title=title
            )
        elif token.type == "heading_open":
            last = token.map[1] - 1
            source = state.getLines(last, last + 1, state.blkIndent, False)
            token.meta["source"] = source.rstrip()
        elif token.type == "hr":
            token.meta["source"] = state.getLines(
                start, start + 1, state.blkIndent, False
            )
        elif token.type == "fence":
            token.meta["indent"] = max(0, state.sCount[start] - state.blkIndent)

        return matched

    return capture


def _capture_list(state: StateBlock, start: int, end: int, silent: bool) -> bool:
    first = len(state.tokens)
    if not rules_block.list_block(state, start, end, silent):
        return False
    if silent:
        return True

    token = state.tokens[first]
    items = [
        item
        for item in state.tokens[first + 1 :]
        if item.type == "list_item_open" and item.level == token.level + 1
    ]
    for item in items:
        assert item.map is not None
        line = item.map[0]
        source = state.getLines(line, line + 1, state.blkIndent, False)
        match = _LIST_MARKER.match(source)
        if match is not None:
            marker_end = match.start("space")
            prefix = match[0].expandtabs(4)
            if len(prefix) - marker_end > 4 or not source[match.end() :]:
                prefix = prefix[:marker_end] + " "
            item.meta["prefix"] = prefix

        # The parser can include separator lines in the preceding item's map.
        # Leave them for the list (or the outer block) to render.
        while item.map[1] > line + 1 and state.isEmpty(item.map[1] - 1):
            item.map[1] -= 1

    assert token.map is not None
    assert items[-1].map is not None
    token.map[1] = items[-1].map[1]
    return True


def _capture_table(state: StateBlock, start: int, end: int, silent: bool) -> bool:
    first = len(state.tokens)
    if not rules_block.table(state, start, end, silent):
        return False
    if silent:
        return True

    row = None
    columns = 0
    for token in state.tokens[first:]:
        if token.type == "tr_open":
            row = token
            columns = 0
        elif token.type == "td_open":
            columns += 1
        elif token.type == "tr_close" and columns:
            assert row is not None
            assert row.map is not None
            line = row.map[0]
            source = state.getLines(line, line + 1, state.blkIndent, False)
            cells = escapedSplit(source.strip())
            if cells and not cells[0]:
                cells.pop(0)
            if cells and not cells[-1]:
                cells.pop()
            # The GFM tokenizer drops surplus cells. The toolkit has always
            # extracted them and expanded the output table to fit.
            if len(cells) > columns:
                row.meta["extra_cells"] = cells[columns:]
    return True


def _table_end(state: StateBlock, start: int, _end: int, silent: bool) -> bool:
    """A line without a pipe starts a new block after a table."""
    return (
        silent
        and state.parentType == "table"
        and "|" not in state.src[state.bMarks[start] : state.eMarks[start]]
    )


@cache
def markdown_parser(*, block_only: bool = False) -> MarkdownIt:
    parser = _MarkdownParser(
        "commonmark",
        {
            "inline_definitions": True,
            "store_labels": True,
            "strikethrough_single_tilde": False,
        },
    )
    parser.block = _MarkdownBlockParser()
    parser.enable(["table", "strikethrough"]).disable("text_join")
    if block_only:
        # Collect every reference definition before parsing any inline spans.
        parser.disable("inline")
    for name, rule, kind in (
        ("link", rules_inline.link, "link_open"),
        ("image", rules_inline.image, "image"),
        ("autolink", rules_inline.autolink, "link_open"),
        ("backticks", rules_inline.backtick, "code_inline"),
        ("escape", rules_inline.escape, "hardbreak"),
        ("newline", rules_inline.newline, "hardbreak"),
    ):
        parser.inline.ruler.at(name, _capture_inline(rule, kind))
    for name, rule, alt in (
        ("reference", rules_block.reference, []),
        ("lheading", rules_block.lheading, []),
        ("heading", rules_block.heading, ["paragraph", "reference", "blockquote"]),
        ("hr", rules_block.hr, ["paragraph", "reference", "blockquote", "list"]),
        ("fence", rules_block.fence, ["paragraph", "reference", "blockquote", "list"]),
    ):
        parser.block.ruler.at(name, _capture_block(rule), {"alt": alt})
    parser.block.ruler.at(
        "list", _capture_list, {"alt": ["paragraph", "reference", "blockquote"]}
    )
    parser.block.ruler.at("table", _capture_table, {"alt": ["paragraph", "reference"]})
    parser.block.ruler.before("table", "table_end", _table_end, {"alt": ["blockquote"]})
    return parser
