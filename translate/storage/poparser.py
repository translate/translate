#
# Copyright 2002-2007 Zuza Software Foundation
# Copyright 2016 F Wolff
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


"""
From the GNU gettext manual:
     WHITE-SPACE
     #  TRANSLATOR-COMMENTS
     #. AUTOMATIC-COMMENTS
     #| PREVIOUS MSGID                 (Gettext 0.16 - check if this is the correct position - not yet implemented)
     #: REFERENCE...
     #, FLAG...
     #= FLAG...
     msgctxt CONTEXT                   (Gettext 0.15)
     msgid UNTRANSLATED-STRING
     msgstr TRANSLATED-STRING.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable

    from .pypo import pofile, pounit

SINGLE_BYTE_ENCODING = "iso-8859-1"


class PoParseError(ValueError):
    def __init__(self, parse_state: PoParseState, message: str | None = None) -> None:
        self.parse_state = parse_state
        if message is None:
            message = "Syntax error"
        super().__init__(
            f"{message} on line {parse_state.lineno}: {parse_state.next_line!r}"
        )


class PoParseState:
    def __init__(
        self,
        input_lines: list[bytes] | list[str],
        UnitClass: Callable[[], pounit],
        encoding: str = SINGLE_BYTE_ENCODING,
    ) -> None:
        # A single-byte encoding is first defined to be able to read the header
        # without risking UnicodeDecodeErrors. As soon as the header is parsed,
        # the encoding defined in the header is used to reset the parser and
        # re-parse all content (including the header) with the correct encoding.
        self._input_lines = input_lines
        self._input_iterator = iter(input_lines)
        self.next_line: str = ""
        self.last_line: str = ""
        self.lineno: int = 0
        self.eof: bool = False
        self.encoding: str = encoding
        self.read_line()
        self.UnitClass = UnitClass

    def set_encoding(self, encoding: str) -> None:
        """Reset parser state to process file with a different encoding."""
        self.encoding = encoding
        self._input_iterator = iter(self._input_lines)
        self.next_line = ""
        self.last_line = ""
        self.lineno = 0
        self.eof = False
        self.read_line()

    def read_line(self) -> str:
        self.last_line = current = self.next_line
        if self.eof:
            return current
        try:
            next_line = next(self._input_iterator)
            self.lineno += 1
            while next_line.isspace():
                next_line = next(self._input_iterator)
                self.lineno += 1
        except StopIteration:
            self.next_line = ""
            self.eof = True
        else:
            if isinstance(next_line, bytes):
                self.next_line = next_line.decode(self.encoding)
            else:
                self.next_line = next_line
        return current

    def new_input(self, input_lines: list[bytes] | list[str]) -> PoParseState:
        return PoParseState(input_lines, self.UnitClass, self.encoding)


def read_prevmsgid_lines(parse_state: PoParseState) -> list[str]:
    """
    Read all the lines starting with #|.

    These lines contain the previous msgid and msgctxt info. We strip away the
    leading '#| ' and read until we stop seeing #|.
    """
    prevmsgid_lines = []
    next_line = parse_state.next_line
    while next_line.startswith(("#|", "|")):
        content = parse_state.read_line()
        prefix_len = content.index("|") + 1
        while content[prefix_len] == " ":
            prefix_len += 1
        content = content[prefix_len:]
        prevmsgid_lines.append(content)
        next_line = parse_state.next_line
    return prevmsgid_lines


def parse_prev_msgctxt(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(parse_state, "msgctxt", 7, unit.prev_msgctxt)
    return len(unit.prev_msgctxt) > 0


def parse_prev_msgid(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(parse_state, "msgid", 5, unit.prev_msgid)
    return len(unit.prev_msgid) > 0


def parse_prev_msgid_plural(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(parse_state, "msgid_plural", 12, unit.prev_msgid_plural)
    return len(unit.prev_msgid_plural) > 0


def parse_comment(parse_state: PoParseState, unit: pounit) -> str | None:
    next_line = parse_state.next_line.lstrip()
    if next_line and next_line[0] in {"#", "|"}:
        next_char = next_line[1]
        if next_char == ".":
            unit.automaticcomments.append(next_line)
        elif next_line[0] == "|" or next_char == "|":
            parsed = False
            # Read all the lines starting with #|
            prevmsgid_lines = read_prevmsgid_lines(parse_state)
            # Create a parse state object that holds these lines
            ps = parse_state.new_input(prevmsgid_lines)
            # Parse the msgctxt if any
            parsed |= parse_prev_msgctxt(ps, unit)
            # Parse the msgid if any
            parsed |= parse_prev_msgid(ps, unit)
            # Parse the msgid_plural if any
            parsed |= parse_prev_msgid_plural(ps, unit)
            # Fail with error in case nothing was parsed
            if not parsed:
                raise PoParseError(parse_state)
            return parse_state.next_line
        elif next_char == ":":
            unit.sourcecomments.append(next_line)
        elif next_char in {",", "="}:
            # One of these will be workflow flags and one sticky flags in the future,
            # normalize to #, for now
            unit.typecomments.append(f"#,{next_line[2:]}")
        elif next_char == "~":
            # Special case: we refuse to parse obsoletes: they are done
            # elsewhere to ensure we reuse the normal unit parsing code
            return None
        else:
            unit.othercomments.append(next_line)
        return parse_state.read_line()
    return None


def parse_comments(parse_state: PoParseState, unit: pounit) -> bool | None:
    if not parse_comment(parse_state, unit):
        return None
    while parse_comment(parse_state, unit):
        pass
    return True


def read_obsolete_lines(parse_state: PoParseState) -> list[str]:
    """Read all the lines belonging to the current unit if obsolete."""
    obsolete_lines = []
    next_line = parse_state.next_line
    while next_line.startswith("#~"):
        content = parse_state.read_line()[2:].lstrip()
        obsolete_lines.append(content)
        next_line = parse_state.next_line
        if content.startswith("msgstr"):
            # now we saw a msgstr, so we need to become more conservative to
            # avoid parsing into the following unit
            while next_line.startswith(('#~ "', "#~ msgstr")):
                content = parse_state.read_line()[3:]
                obsolete_lines.append(content)
                next_line = parse_state.next_line
            break
    return obsolete_lines


def parse_obsolete(parse_state: PoParseState, unit: pounit) -> pounit | None:
    obsolete_lines = read_obsolete_lines(parse_state)
    if len(obsolete_lines) == 0:
        return None
    parsed_unit = parse_unit(parse_state.new_input(obsolete_lines), unit)
    if parsed_unit is not None:
        parsed_unit.makeobsolete()
    return parsed_unit


def parse_quoted(parse_state: PoParseState, start_pos: int = 0) -> str | None:
    line = parse_state.next_line
    left = line.find('"', start_pos)
    if left == start_pos or line[start_pos:left].isspace():
        right = line.rfind('"')
        if left != right:
            return parse_state.read_line()[left : right + 1]
        raise PoParseError(parse_state, "end-of-line within string")
    return None


def parse_msg_comment(
    parse_state: PoParseState, msg_comment_list: list[str], string: str
) -> str | None:
    parsed_string: str | None = string
    while parsed_string is not None:
        msg_comment_list.append(parsed_string)
        if parsed_string.find("\\n") > -1:
            return parse_quoted(parse_state)
        parsed_string = parse_quoted(parse_state)
    return None


def parse_multiple_quoted(
    parse_state: PoParseState,
    msg_list: list[str],
    msg_comment_list: list[str] | None,
    first_start_pos: int = 0,
) -> None:
    string = parse_quoted(parse_state, first_start_pos)
    while string is not None:
        if msg_comment_list is None or not string.startswith('"_:'):
            msg_list.append(string)
            string = parse_quoted(parse_state)
        else:
            string = parse_msg_comment(parse_state, msg_comment_list, string)


def parse_message(
    parse_state: PoParseState,
    start_of_string: str,
    start_of_string_len: int,
    msg_list: list[str],
    msg_comment_list: list[str] | None = None,
) -> None:
    if parse_state.next_line.startswith(start_of_string):
        parse_multiple_quoted(
            parse_state, msg_list, msg_comment_list, start_of_string_len
        )


def parse_msgctxt(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(parse_state, "msgctxt", 7, unit.msgctxt)
    return len(unit.msgctxt) > 0


def parse_msgid(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(parse_state, "msgid", 5, unit.msgid, unit.msgidcomments)
    return len(unit.msgid) > 0 or len(unit.msgidcomments) > 0


def parse_msgstr(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(parse_state, "msgstr", 6, cast("list[str]", unit.msgstr))
    return len(unit.msgstr) > 0


def parse_msgid_plural(parse_state: PoParseState, unit: pounit) -> bool:
    parse_message(
        parse_state, "msgid_plural", 12, unit.msgid_plural, unit.msgid_pluralcomments
    )
    return len(unit.msgid_plural) > 0 or len(unit.msgid_pluralcomments) > 0


MSGSTR_ARRAY_ENTRY_LEN = len("msgstr[")


def add_to_dict(
    msgstr_dict: dict[int, list[str]],
    line: str,
    right_bracket_pos: int,
    entry: list[str],
) -> None:
    index = int(line[MSGSTR_ARRAY_ENTRY_LEN:right_bracket_pos])
    if index not in msgstr_dict:
        msgstr_dict[index] = []
    msgstr_dict[index].extend(entry)


def get_entry(parse_state: PoParseState, right_bracket_pos: int) -> list[str]:
    entry = []
    parse_message(parse_state, "msgstr[", right_bracket_pos + 1, entry)
    return entry


def parse_msgstr_array_entry(
    parse_state: PoParseState, msgstr_dict: dict[int, list[str]]
) -> bool:
    line = parse_state.next_line
    right_bracket_pos = line.find("]", MSGSTR_ARRAY_ENTRY_LEN)
    if right_bracket_pos >= 0:
        entry = get_entry(parse_state, right_bracket_pos)
        if entry:
            add_to_dict(msgstr_dict, line, right_bracket_pos, entry)
            return True
        return False
    return False


def parse_msgstr_array(parse_state: PoParseState, unit: pounit) -> bool:
    msgstr_dict: dict[int, list[str]] = {}
    result = parse_msgstr_array_entry(parse_state, msgstr_dict)
    if not result:  # We require at least one result
        return False
    while parse_msgstr_array_entry(parse_state, msgstr_dict):
        pass
    unit.msgstr = msgstr_dict
    return True


def parse_plural(parse_state: PoParseState, unit: pounit) -> bool:
    return bool(
        parse_msgid_plural(parse_state, unit) and parse_msgstr_array(parse_state, unit)
    )


def parse_msg_entries(parse_state: PoParseState, unit: pounit) -> bool:
    parse_msgctxt(parse_state, unit)
    return bool(
        parse_msgid(parse_state, unit)
        and (parse_msgstr(parse_state, unit) or parse_plural(parse_state, unit))
    )


def parse_unit(parse_state: PoParseState, unit: pounit | None = None) -> pounit | None:
    unit = unit or parse_state.UnitClass()
    # Store the line number where this unit starts
    # Use the current line number since we're at the start of parsing
    start_line = parse_state.lineno
    parsed_comments = parse_comments(parse_state, unit)
    obsolete_unit = parse_obsolete(parse_state, unit)
    if obsolete_unit is not None:
        # Set line number for obsolete units
        if hasattr(obsolete_unit, "_line_number"):
            obsolete_unit._line_number = start_line
        return obsolete_unit
    parsed_msg_entries = parse_msg_entries(parse_state, unit)
    if parsed_comments or parsed_msg_entries:
        # Set line number for regular units
        if hasattr(unit, "_line_number"):
            unit._line_number = start_line
        return unit
    return None


def get_header_charset(unit: pounit) -> str:
    if (
        isinstance(unit.msgstr, list)
        and unit.msgstr
        and isinstance(unit.msgstr[0], str)
    ):
        # Allow optional whitespace after '=' to match 'charset= koi8-r'
        charset_match = re.search(r"charset=\s*([^\s\\n]+)", "".join(unit.msgstr))
        if charset_match and (charset := charset_match.group(1)) != "CHARSET":
            return charset
    # fallback to utf-8
    return "utf-8"


def parse_header(parse_state: PoParseState, store: pofile) -> pounit | None:
    first_unit = parse_unit(parse_state)
    if first_unit is None:
        return None
    charset = get_header_charset(first_unit)

    if parse_state.encoding == charset:
        return first_unit

    # Configure store
    store._encoding = charset
    # Configure parser
    parse_state.set_encoding(charset)

    # Parse header with the new encoding
    return parse_unit(parse_state)


def parse_units(parse_state: PoParseState, store: pofile) -> None:
    unit = parse_header(parse_state, store)
    while unit:
        unit.infer_state()
        store.addunit(unit)
        unit = parse_unit(parse_state)
    if not parse_state.eof:
        raise PoParseError(parse_state)
