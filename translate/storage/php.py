#
# Copyright 2004-2008 Zuza Software Foundation
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
Classes that hold units of PHP localisation files :class:`phpunit` or
entire files :class:`phpfile`. These files are used in translating many
PHP based applications.

Only PHP files written with these conventions are supported:

.. code-block:: php

   <?php
   $lang['item'] = "vale";  # Array of values
   $some_entity = "value";  # Named variables
   define("ENTITY", "value");
   $lang = array(
      'item1' => 'value1'    ,   #Supports space before comma
      'item2' => 'value2',
   );
   $lang = array(    # Nested arrays
      'item1' => 'value1',
      'item2' => array(
         'key' => 'value'    ,   #Supports space before comma
         'key2' => 'value2',
      ),
   );

Nested arrays without key for nested array are not supported:

.. code-block:: php

   <?php
   $lang = array(array('key' => 'value'));

The working of PHP strings and specifically the escaping conventions which
differ between single quote (') and double quote (") characters are
implemented as outlined in the PHP documentation for the
`String type <https://www.php.net/language.types.string>`_.
"""

import re
import string

from phply.phpast import (
    Array,
    ArrayElement,
    ArrayOffset,
    Assignment,
    BinaryOp,
    FunctionCall,
    InlineHTML,
    Node,
    Return,
    Variable,
)
from phply.phplex import FilteredLexer, full_lexer
from phply.phpparse import make_parser

from translate.misc.multistring import multistring
from translate.storage import base


def _skip_php_spaces(name: str, pos: int) -> int:
    """Skip whitespace and inert comments between PHP tokens."""
    while pos < len(name):
        if name[pos] in " \t\r\n":
            pos += 1
        elif name.startswith("/*", pos):
            end = name.find("*/", pos + 2)
            if end < 0:
                return -1
            pos = end + 2
        elif name.startswith("#[", pos):
            return -1
        elif name.startswith("//", pos) or name[pos] == "#":
            while pos < len(name) and name[pos] not in "\r\n":
                if name.startswith("?>", pos):
                    return -1
                pos += 1
            if pos == len(name):
                return -1
        else:
            break
    return pos


def _scan_php_unicode_escape(name: str, pos: int) -> int:
    """Return the end of a valid double-quoted Unicode escape, or -1."""
    pos += 3  # Skip \u{.
    start = pos
    codepoint = 0
    while pos < len(name) and name[pos] in string.hexdigits:
        codepoint = codepoint * 16 + int(name[pos], 16)
        if codepoint > 0x10FFFF:
            return -1
        pos += 1
    if (
        pos == start
        or pos >= len(name)
        or name[pos] != "}"
        or 0xD800 <= codepoint <= 0xDFFF
    ):
        return -1
    return pos + 1


def _is_php_variable_start(char: str) -> bool:
    return char == "_" or "A" <= char <= "Z" or "a" <= char <= "z" or ord(char) >= 128


def _is_php_variable_continue(char: str) -> bool:
    return _is_php_variable_start(char) or "0" <= char <= "9"


def _starts_php_interpolation(name: str, pos: int) -> bool:
    if pos + 1 >= len(name):
        return False
    next_char = name[pos + 1]
    return next_char == "{" or _is_php_variable_start(next_char)


def _starts_php_string(name: str, pos: int) -> bool:
    return pos < len(name) and (
        name[pos] in {"'", '"'}
        or (name[pos] in "bB" and pos + 1 < len(name) and name[pos + 1] in {"'", '"'})
    )


def _scan_php_string(name: str, pos: int) -> int:
    """Return the end of a safe PHP source literal, or -1."""
    if name[pos] in "bB":
        pos += 1
    quotechar = name[pos]
    pos += 1
    while pos < len(name):
        char = name[pos]
        if (ord(char) < 32 and char not in "\t\n\r") or ord(char) == 127:
            return -1
        if quotechar == '"' and (
            name.startswith("{$", pos)
            or (char == "\\" and name.startswith("{$", pos + 1))
        ):
            return -1
        if char == "\\":
            if pos + 1 >= len(name):
                return -1
            if quotechar == '"' and name.startswith(r"\u{", pos):
                pos = _scan_php_unicode_escape(name, pos)
                if pos < 0:
                    return -1
                continue
            escaped = name[pos + 1]
            if ord(escaped) < 32 or ord(escaped) == 127:
                return -1
            pos += 2
        elif char == quotechar:
            return pos + 1
        elif quotechar == '"' and char == "$" and _starts_php_interpolation(name, pos):
            return -1
        else:
            pos += 1
    return -1


def _scan_php_integer(name: str, pos: int) -> int:
    if pos < len(name) and name[pos] == "-":
        pos += 1
    if pos >= len(name) or not "0" <= name[pos] <= "9":
        return -1
    if name[pos] == "0":
        return pos + 1
    while pos < len(name) and "0" <= name[pos] <= "9":
        pos += 1
    return pos


def _scan_php_number(name: str, pos: int) -> int:
    """Scan an inert PHP numeric literal used as an array index."""
    if pos < len(name) and name[pos] in "+-":
        pos += 1
    if pos >= len(name):
        return -1
    if name[pos] == "0" and pos + 1 < len(name):
        prefix = name[pos + 1]
        digits = {
            "x": string.hexdigits,
            "X": string.hexdigits,
            "b": "01",
            "B": "01",
            "o": string.octdigits,
            "O": string.octdigits,
        }.get(prefix)
        if digits is not None:
            pos += 2
            start = pos
            while pos < len(name) and name[pos] in digits:
                pos += 1
            return pos if pos > start else -1

    start = pos
    while pos < len(name) and "0" <= name[pos] <= "9":
        pos += 1
    integer_end = pos
    fractional = pos < len(name) and name[pos] == "."
    if fractional:
        pos += 1
        while pos < len(name) and "0" <= name[pos] <= "9":
            pos += 1
    if pos == start or (pos == start + 1 and fractional):
        return -1
    exponent = pos < len(name) and name[pos] in "eE"
    if exponent:
        pos += 1
        if pos < len(name) and name[pos] in "+-":
            pos += 1
        exponent_start = pos
        while pos < len(name) and "0" <= name[pos] <= "9":
            pos += 1
        if pos == exponent_start:
            return -1
    if (
        not fractional
        and not exponent
        and integer_end - start > 1
        and name[start] == "0"
        and any(char not in string.octdigits for char in name[start + 1 : integer_end])
    ):
        return -1
    return pos


def _scan_php_index_atom(name: str, pos: int) -> int:
    for literal in ("true", "false", "null"):
        if name[pos : pos + len(literal)].lower() == literal:
            return pos + len(literal)
    return _scan_php_number(name, pos)


def _valid_php_leaf(name: str, start: int, end: int) -> bool:
    """Check a decoded final key; the serializer escapes its apostrophes."""
    if end - start < 2 or name[start] not in {"'", '"'} or name[end - 1] != name[start]:
        return False
    quotechar = name[start]
    pos = start + 1
    while pos < end - 1:
        char = name[pos]
        if (
            (ord(char) < 32 and char not in "\t\n\r")
            or ord(char) == 127
            or (quotechar == '"' and name.startswith("{$", pos))
        ):
            return False
        if char == "\\":
            if quotechar == '"' or pos + 1 >= end - 1:
                return False
            escaped = name[pos + 1]
            if escaped in {"'", "\\"} or ord(escaped) < 32 or ord(escaped) == 127:
                return False
            pos += 2
        elif quotechar == '"' and char == "$" and _starts_php_interpolation(name, pos):
            return False
        else:
            pos += 1
    return True


def _valid_php_index(name: str, start: int, end: int, *, leaf: bool) -> bool:
    if leaf and name.startswith("[]", start) and start + 2 == end:
        return True
    if start >= end:
        return False
    if name[start] in {"'", '"'}:
        return (
            _valid_php_leaf(name, start, end)
            if leaf
            else _scan_php_string(name, start) == end
        )
    return _scan_php_index_atom(name, start) == end


def _scan_php_scalar(name: str, pos: int) -> int:
    """Scan an approved scalar with optional balanced parentheses, iteratively."""
    depth = 0
    pos = _skip_php_spaces(name, pos)
    while 0 <= pos < len(name) and name[pos] == "(":
        depth += 1
        pos = _skip_php_spaces(name, pos + 1)
    if pos < 0 or pos >= len(name):
        return -1
    end = (
        _scan_php_string(name, pos)
        if _starts_php_string(name, pos)
        else _scan_php_index_atom(name, pos)
    )
    while depth and end >= 0:
        end = _skip_php_spaces(name, end)
        if end < 0 or end >= len(name) or name[end] != ")":
            return -1
        end += 1
        depth -= 1
    return end


def _scan_php_offset(name: str, pos: int) -> int:
    pos = _skip_php_spaces(name, pos + 1)
    if pos < 0:
        return -1
    if pos < len(name) and name[pos] == "]":
        return pos + 1
    if pos >= len(name):
        return -1
    end = _scan_php_scalar(name, pos)
    if end < 0:
        return -1
    end = _skip_php_spaces(name, end)
    return end + 1 if 0 <= end < len(name) and name[end] == "]" else -1


def _split_php_name(name: str) -> list[str] | None:
    """Split member boundaries without treating quoted arrows as separators."""
    pos = 0
    quotechar = ""
    bracket_depth = 0
    while pos < len(name):
        char = name[pos]
        if quotechar:
            if char == "\\":
                pos += 2
                continue
            if char == quotechar:
                quotechar = ""
        elif name.startswith(("/*", "//", "#"), pos):
            end = _skip_php_spaces(name, pos)
            if end < 0:
                return None
            if end != pos:
                pos = end
                continue
        elif char in {"'", '"'}:
            quotechar = char
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif bracket_depth == 0 and name.startswith("->", pos):
            break
        pos += 1
    if pos >= len(name):
        return [name]

    parts = [name[:pos]]
    pos += 2
    while pos < len(name):
        start = pos
        end = (
            _scan_php_string(name, pos)
            if name[pos] in {"'", '"'}
            else _scan_php_index_atom(name, pos)
        )
        if end >= 0:
            member_end = end + 2 if name.startswith("[]", end) else end
            if name.startswith("->", member_end):
                parts.append(name[start:member_end])
                pos = member_end + 2
                continue
        if _valid_php_index(name, start, len(name), leaf=True):
            parts.append(name[start:])
            return parts
        return None
    return None


def _valid_php_members(name: str, pos: int, *, required: bool) -> bool:
    parts = _split_php_name(name[pos:])
    if parts is None or parts[0] not in {"", "[]"}:
        return False
    if len(parts) == 1:
        return not required and not parts[0]
    for member in parts[1:-1]:
        if not _valid_php_index(member, 0, len(member.removesuffix("[]")), leaf=False):
            return False
    leaf = parts[-1]
    return _valid_php_index(leaf, 0, len(leaf), leaf=True)


def _validate_php_name(name: str, *, laravel: bool = False) -> None:
    """Accept only inert PHP key expressions using a bounded-time scan."""
    if name != name.rstrip():
        raise ValueError("PHP key cannot be represented exactly")
    if name.startswith("return"):
        valid = _valid_php_members(name, 6, required=True)
    elif laravel:
        valid = False
    elif name.startswith("define("):
        pos = _skip_php_spaces(name, 7)
        end = (
            _scan_php_string(name, pos)
            if pos >= 0 and _starts_php_string(name, pos)
            else -1
        )
        valid = end >= 0 and _skip_php_spaces(name, end) == len(name)
    elif name.startswith("$") and len(name) > 1:
        pos = 1
        char = name[pos]
        valid = _is_php_variable_start(char)
        if valid:
            pos += 1
            while pos < len(name) and _is_php_variable_continue(name[pos]):
                pos += 1
            while True:
                offset = _skip_php_spaces(name, pos)
                if offset < 0:
                    valid = False
                    break
                if offset >= len(name) or name[offset] != "[":
                    pos = offset
                    break
                pos = _scan_php_offset(name, offset)
                if pos < 0:
                    valid = False
                    break
            if valid:
                valid = _valid_php_members(name, pos, required=False)
    else:
        valid = False
    if not valid:
        raise ValueError("PHP key cannot be represented safely")


def wrap_production(func):
    """Decorator for production functions to store lexer positions."""

    def prod(n) -> None:
        func(n)
        if isinstance(n[0], Node):
            startpos = min(getattr(i, "lexpos", 0) for i in n.slice[1:])
            endpos = max(getattr(i, "endlexpos", 0) for i in n.slice[1:])
            n[0].lexpositions = startpos, endpos
        elif isinstance(n[0], list) and n[0] and isinstance(n[0][-1], ArrayElement):
            startpos = min(getattr(i, "lexpos", 0) for i in n.slice[1:])
            endpos = max(getattr(i, "endlexpos", 0) for i in n.slice[1:])
            n[0][-1].lexpositions = startpos, endpos

    return prod


class PHPLexer(FilteredLexer):
    def __init__(self) -> None:
        super().__init__(full_lexer.clone())
        self.tokens = []
        self.pos = 0
        self.codepos = 0

    def next_lexer_token(self):
        token = self.lexer.token()
        if token is not None:
            self.tokens.append(token)
        return token

    def extract_comments(self, end):
        """
        Extract comments related to given parser positions.

        Must be called sequentially for consequent statements.
        """
        comments = []
        # Process all tokens to end of statement
        while self.tokens[self.pos].lexpos < end:
            if self.tokens[self.pos].type in {"COMMENT", "DOC_COMMENT"}:
                comments.append(self.tokens[self.pos].value.strip())
            self.pos += 1
        # Skip end of statement
        self.pos += 1
        # Proceed comments till newline
        length = len(self.tokens)
        while self.pos < length and self.tokens[self.pos].type in {
            "COMMENT",
            "WHITESPACE",
        }:
            token_type = self.tokens[self.pos].type
            token_value = self.tokens[self.pos].value
            self.pos += 1
            if token_type == "WHITESPACE":  # ruff:ignore[hardcoded-password-string]
                if "\n" in token_value:
                    break
                continue
            comments.append(token_value.strip())
            if "\n" in token_value:
                break
        return comments

    def extract_name(self, terminator, start, end):
        """Extract current value name."""
        result = ""
        pos = self.pos
        while self.tokens[pos].lexpos < start:
            pos += 1
        while self.tokens[pos].lexpos < end and self.tokens[pos].type != terminator:
            result += self.tokens[pos].value
            pos += 1
        self.codepos = pos
        return result.rstrip()

    def extract_quote(self) -> str:
        """Extract quote style."""
        pos = max(self.pos, self.codepos)
        while self.tokens[pos].type not in {
            "QUOTE",
            "CONSTANT_ENCAPSED_STRING",
            "START_NOWDOC",
        }:
            pos += 1
        if self.tokens[pos].type == "QUOTE":
            return '"'
        return "'"

    def extract_array(self) -> str:
        pos = max(self.pos, self.codepos)
        while self.tokens[pos].type not in {"ARRAY", "LBRACKET"}:
            pos += 1
        self.codepos = pos
        if self.tokens[pos].type == "ARRAY":
            return ""
        return "[]"


def phpencode(text, quotechar="'"):
    """
    Convert Python string to PHP escaping.

    The encoding is implemented for
    `'single quote' <https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
    and `"double quote" <https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
    syntax.

    heredoc and nowdoc are not implemented and it is not certain whether this
    would ever be needed for PHP localisation needs.
    """
    if not text:
        return text
    if quotechar == '"':
        # \n may be converted to \\n but we don't.  This allows us to preserve
        # pretty layout that might have appeared in muliline entries we might
        # lose some "blah\nblah" layouts but that's probably not the most
        # frequent use case. See bug 588
        escapes = [
            ("\\", "\\\\"),
            ("\r", "\\r"),
            ("\t", "\\t"),
            ("\v", "\\v"),
            ("\f", "\\f"),
            ("\\\\$", "\\$"),
            ('"', '\\"'),
            ("\\\\", "\\"),
        ]
        for a, b in escapes:
            text = text.replace(a, b)
        return text
    return text.replace(f"{quotechar}", f"\\{quotechar}")


def phpdecode(text, quotechar="'"):
    """Convert PHP escaped string to a Python string."""
    escape_encoding = "unicode_escape"

    def decode_octal_hex(match):
        r"""Decode Octal \NNN and Hex values."""
        if "octal" in match.groupdict():
            return match.groupdict()["octal"].encode("latin-1").decode(escape_encoding)
        if "hex" in match.groupdict():
            return match.groupdict()["hex"].encode("latin-1").decode(escape_encoding)
        return match.group

    if not text:
        return text
    if quotechar == '"':
        # We do not escape \$ as it is used by variables and we can't
        # roundtrip that item.
        escapes = [
            ('\\"', '"'),
            ("\\\\", "\\"),
            ("\\n", "\n"),
            ("\\r", "\r"),
            ("\\t", "\t"),
            ("\\v", "\v"),
            ("\\f", "\f"),
        ]
        for a, b in escapes:
            text = text.replace(a, b)
        text = re.sub(r"(?P<octal>\\[0-7]{1,3})", decode_octal_hex, text)
        return re.sub(r"(?P<hex>\\x[0-9A-Fa-f]{1,2})", decode_octal_hex, text)
    return text.replace("\\'", "'").replace("\\\\", "\\")


class phpunit(base.TranslationUnit):
    """A unit of a PHP file: a name, a value, and any comments associated."""

    def __init__(self, source="") -> None:
        """Construct a blank phpunit."""
        self.escape_type = "'"
        super().__init__(source)
        self.name = "$TTK_PLACEHOLDER"
        self.value = ""
        self.translation = ""
        self._comments = []
        self.source = source

    @property
    def source(self):
        return self.value

    @source.setter
    def source(self, source) -> None:
        """Set the source AND the target to be equal."""
        self._invalidate_store_indexes()
        self._rich_source = None
        self.value = source

    @property
    def target(self):
        return self.translation

    @target.setter
    def target(self, target) -> None:
        self._rich_target = None
        self.translation = target

    def __str__(self) -> str:
        """Convert to a string."""
        return self.getoutput()

    def get_raw_value(self):
        return self.translation or self.value

    def getoutput(self, indent="", name=None, *, _has_members: bool | None = None):
        """Convert the unit back into formatted lines for a php file."""
        has_members = (
            len(_split_php_name(self.name) or []) > 1
            if _has_members is None
            else _has_members
        )
        if has_members and name == "[]":
            fmt = "{1}{2}{1},\n"
        elif has_members:
            fmt = "{0} => {1}{2}{1},\n"
            if name is not None and name[0] == name[-1] and name[0] in {"'", '"'}:
                name = name[0] + phpencode(name[1:-1], name[0]) + name[0]
        elif self.name.startswith("define"):
            fmt = "{0}, {1}{2}{1});\n"
        else:
            fmt = "{0} = {1}{2}{1};\n"
        out = fmt.format(
            name or self.name,
            self.escape_type,
            phpencode(self.get_raw_value(), self.escape_type),
        )
        joiner = f"\n{indent}"
        return indent + joiner.join([*self._comments, out])

    def addlocation(self, location) -> None:
        self.name = location

    def getlocations(self):
        return [self.name]

    def addnote(self, text, origin=None, position="append") -> None:
        if origin in {"programmer", "developer", "source code", None}:
            if position == "append":
                self._comments.append(text)
            else:
                self._comments = [text]
        else:
            super().addnote(text, origin=origin, position=position)

    def getnotes(self, origin=None):
        if origin in {"programmer", "developer", "source code", None}:
            return "\n".join(self._comments)
        return super().getnotes(origin)

    def removenotes(self, origin=None) -> None:
        self._comments = []

    def isblank(self) -> bool:
        """Return whether this is a blank element, containing only comments."""
        return not (self.name or self.value)

    def getid(self):
        return self.name

    def validate_id(self, value: str) -> None:
        """Validate PHP source syntax; offsets retain PHP's own key coercion."""
        super().validate_id(value)
        _validate_php_name(value)
        self._validate_id_encoding(value)

    def _validate_id_encoding(self, value: str) -> None:
        """Check the encoding used to write this unit's name verbatim."""
        encoding = (
            self._store.encoding
            if self._store is not None
            else phpfile.default_encoding
        )
        try:
            value.encode(encoding)
        except UnicodeEncodeError as error:
            raise ValueError(
                "PHP key cannot be represented in file encoding"
            ) from error

    def setid(self, value) -> None:
        # Sanitize name to produce valid syntax
        if not isinstance(value, str):
            raise TypeError("PHP key must be a string")
        name = (
            value
            if value.startswith(("$", "define(", "return"))
            else f"${value.replace(' ', '_')}"
        )
        self.validate_id(name)
        self._invalidate_store_indexes()
        self.name = name


class phpfile(base.TranslationStore):
    """This class represents a PHP file, made up of phpunits."""

    UnitClass = phpunit

    def __init__(self, inputfile=None, **kwargs) -> None:
        """Construct a phpfile, optionally reading in from inputfile."""
        super().__init__(**kwargs)
        self.filename = getattr(inputfile, "name", "")
        if inputfile is not None:
            phpsrc = inputfile.read()
            inputfile.close()
            self.parse(phpsrc)

    def serialize(self, out) -> None:
        """Convert the units back to lines."""
        array_units: dict[str, list[phpunit]] = {}
        unit_parts: dict[int, list[str]] = {}
        array_parts: dict[str, tuple[str, int]] = {}
        for unit in self.units:
            name_parts = _split_php_name(unit.name) or unit.name.split("->")
            unit_parts[id(unit)] = name_parts
            array_name = name_parts[0]
            for depth, name_part in enumerate(name_parts[1:], start=1):
                array_units.setdefault(array_name, []).append(unit)
                array_parts.setdefault(array_name, (name_parts[depth - 1], depth))
                array_name = f"{array_name}->{name_part}"

        def write(text) -> None:
            out.write(text.encode(self.encoding))

        def handle_array(arrname, handled, indent=0) -> None:
            if arrname in handled:
                return
            children = set()
            # Default to classic array
            init = "array("
            close = ")"
            name, prefix_depth = array_parts[arrname]
            nested = prefix_depth > 1
            # Handle [] style array
            if name.endswith("[]"):
                init = "["
                close = "]"
                name = name[:-2]
            # Handle return, assignment or sub array
            if nested:
                separator = " =>"
            elif name == "return":
                separator = ""
            else:
                separator = " ="
            # Write array start
            write(f"{' ' * indent}{name}{separator} {init}\n")
            indent += 4
            prefix = f"{arrname}->"
            for item in array_units[arrname]:
                child_parts = unit_parts[id(item)][prefix_depth:]
                if len(child_parts) > 1:
                    handle_array(prefix + child_parts[0], children, indent)
                else:
                    write(
                        item.getoutput(" " * indent, child_parts[0], _has_members=True)
                    )
            # Write array end
            write(f"{' ' * (indent - 4)}{close}{',' if nested else ';'}\n")
            handled.add(arrname)

        write("<?php\n")

        # List of handled arrays
        handled = set()
        for unit in self.units:
            name_parts = unit_parts[id(unit)]
            if len(name_parts) > 1:
                handle_array(name_parts[0], handled)
            else:
                write(unit.getoutput(_has_members=False))

    def create_and_add_unit(self, name, value, escape_type, comments) -> None:
        newunit = self.UnitClass()
        newunit.escape_type = escape_type
        newunit.addlocation(name)
        newunit.source = value
        for comment in comments:
            newunit.addnote(comment, "developer")
        self.addunit(newunit)

    def parse(self, phpsrc) -> None:  # ty:ignore[invalid-method-override]
        """Read the source of a PHP file in and include them as units."""

        def handle_array(prefix, nodes, lexer) -> None:
            prefix += lexer.extract_array()
            for item in nodes:
                assert isinstance(item, ArrayElement)
                if item.key is None:
                    name = []
                else:
                    # To update lexer current position
                    lexer.extract_name("DOUBLE_ARROW", *item.lexpositions)
                    if isinstance(item.key, BinaryOp):
                        name = f"'{concatenate(item.key)}'"
                    elif isinstance(item.key, (int, float)):
                        name = f"{item.key}"
                    else:
                        name = f"'{item.key}'"
                if prefix:
                    name = f"{prefix}->{name}"
                if isinstance(item.value, Array):
                    handle_array(name, item.value.nodes, lexer)
                elif isinstance(item.value, str):
                    self.create_and_add_unit(
                        name,
                        item.value,
                        lexer.extract_quote(),
                        lexer.extract_comments(item.lexpositions[1]),
                    )

        def concatenate(item):
            if isinstance(item, str):
                return item
            if isinstance(item, Variable):
                return item.name
            assert isinstance(item, BinaryOp)
            return concatenate(item.left) + concatenate(item.right)

        parser = make_parser()
        for item in parser.productions:
            item.callable = wrap_production(item.callable)
        lexer = PHPLexer()
        tree = parser.parse(phpsrc.decode(self.encoding), lexer=lexer, tracking=True)
        # Handle text without PHP start
        if len(tree) == 1 and isinstance(tree[0], InlineHTML):
            self.parse(b"<?php\n" + phpsrc)
            return
        for item in tree:
            if isinstance(item, FunctionCall):
                if item.name == "define":
                    self.create_and_add_unit(
                        lexer.extract_name("COMMA", *item.lexpositions),
                        item.params[1].node,
                        lexer.extract_quote(),
                        lexer.extract_comments(item.lexpositions[1]),
                    )
            elif isinstance(item, Assignment):
                if isinstance(item.node, (ArrayOffset, Variable)):
                    name = lexer.extract_name("EQUALS", *item.lexpositions)
                    if isinstance(item.expr, Array):
                        handle_array(name, item.expr.nodes, lexer)
                    elif isinstance(item.expr, str):
                        self.create_and_add_unit(
                            name,
                            item.expr,
                            lexer.extract_quote(),
                            lexer.extract_comments(item.lexpositions[1]),
                        )
                    elif isinstance(item.expr, BinaryOp) and item.expr.op == ".":
                        self.create_and_add_unit(
                            name,
                            concatenate(item.expr),
                            lexer.extract_quote(),
                            lexer.extract_comments(item.lexpositions[1]),
                        )
            elif isinstance(item, Return) and isinstance(item.node, Array):
                # Adjustextractor position
                lexer.extract_name("RETURN", *item.lexpositions)
                handle_array("return", item.node.nodes, lexer)


class LaravelPHPUnit(phpunit):
    def get_raw_value(self):
        result = self.translation or self.value
        if isinstance(result, multistring):
            return "|".join(result.strings)
        return result

    @staticmethod
    def _id_from_name(name: str) -> str:
        # Strip return[]-> or return-> prefix for Laravel files
        if name.startswith("return[]->"):
            name = name[10:]  # Remove "return[]->"
        elif name.startswith("return->"):
            name = name[8:]  # Remove "return->"

        # Strip surrounding quotes if present
        if len(name) >= 2 and name[0] == name[-1] and name[0] in {"'", '"'}:
            return name[1:-1]
        return name

    def getid(self) -> str:
        """Return the key without the Laravel return prefix."""
        return self._id_from_name(self.name)

    def getlocations(self):
        """Return locations without the Laravel return prefix."""
        return [self.getid()]

    def _name_for_id(self, value: str) -> str:
        # If value already has a return prefix, use it as is
        if value.startswith(("return[]->", "return->")):
            return value

        # Determine the array syntax to use based on existing structure
        if self.name.startswith("return[]->"):
            # Preserve short array syntax
            prefix = "return[]->"
        elif self.name.startswith("return->"):
            # Preserve array() syntax
            prefix = "return->"
        else:
            # For newly created units or units without a return prefix,
            # check if the store has a detected array prefix
            prefix = self._get_array_prefix_from_store()

        # Add quotes if not already present and value is not numeric
        # Handle empty string, quoted values, and numeric values correctly
        if value and value[0] not in {"'", '"'}:
            # Check if it's a valid integer (handles negative numbers too)
            if not self._is_numeric_key(value):
                value = f"'{value}'"
        elif not value:
            # Empty string should be quoted
            value = "''"

        return f"{prefix}{value}"

    def _validated_name(self, value: str, *, exact: bool) -> str:
        base.TranslationUnit.validate_id(self, value)
        name = self._name_for_id(value)
        _validate_php_name(name, laravel=True)
        self._validate_id_encoding(name)
        if exact and self._id_from_name(name) != value:
            raise ValueError("PHP key cannot be represented exactly")
        return name

    def validate_id(self, value: str) -> None:
        self._validated_name(value, exact=True)

    def setid(self, value) -> None:
        """Set the key, preserving the Laravel return array structure."""
        if not isinstance(value, str):
            value = str(value)
        name = self._validated_name(value, exact=False)
        self._invalidate_store_indexes()
        self.name = name

    def _get_array_prefix_from_store(self):
        """Get the array prefix from store, or return default."""
        if (
            hasattr(self, "_store")
            and self._store
            and hasattr(self._store, "_array_prefix")
            and self._store._array_prefix
        ):
            return self._store._array_prefix
        # Default to array() syntax for new files
        return "return->"

    @staticmethod
    def _is_numeric_key(value: str) -> bool:
        """Check for a decimal PHP key without converting a large integer."""
        if _scan_php_integer(value, 0) != len(value):
            return False
        digits = value.removeprefix("-")
        limit = (
            "9223372036854775808" if value.startswith("-") else "9223372036854775807"
        )
        return len(digits) < len(limit) or (
            len(digits) == len(limit) and digits <= limit
        )


class LaravelPHPFile(phpfile):
    UnitClass = LaravelPHPUnit

    def __init__(self, inputfile=None, **kwargs) -> None:
        """Construct a LaravelPHPFile, optionally reading in from inputfile."""
        # Store the array syntax prefix detected during parsing
        self._array_prefix = None
        super().__init__(inputfile, **kwargs)

    def create_and_add_unit(self, name, value, escape_type, comments) -> None:
        # Detect and store array prefix from the first unit
        if self._array_prefix is None and name.startswith("return"):
            if name.startswith("return[]->"):
                self._array_prefix = "return[]->"
            elif name.startswith("return->"):
                self._array_prefix = "return->"

        if "|" in value:
            value = multistring(value.split("|"))
        super().create_and_add_unit(name, value, escape_type, comments)
