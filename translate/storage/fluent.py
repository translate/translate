#
# Copyright 2021 Jack Grigg
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

r"""Manage the Fluent translation format.

It is a monolingual base class derived format with :class:`FluentFile`
and :class:`FluentUnit` providing file and unit level access.
"""

from fluent.syntax import FluentParser, ast, parse, serialize, visitor
from fluent.syntax.serializer import serialize_pattern, serialize_placeable
from fluent.syntax.stream import FluentParserStream
from translate.storage import base


def id_from_source(source):
    # If the caller does not provide a unit ID, we need to generate one
    # ourselves. A valid Fluent identifier has the following EBNF grammar:
    #     Identifier          ::= [a-zA-Z] [a-zA-Z0-9_-]*
    #
    # This means we can't simply use the source string itself as the identifier
    # (as e.g. PO files do). Instead, we hash the source string with a
    # collision-resistant hash function.
    import hashlib

    return "gen-" + hashlib.sha256(source.encode()).hexdigest()


def source_from_entry(entry):
    # Serialized patterns come in two forms:
    # - Single-line patterns, which have a leading space we need to strip (for
    #   consistency with the expectations of what callers will set).
    # - Multiline patterns, which have a leading newline we need to preserve.
    return serialize_pattern(entry.value).lstrip(" ")


class FluentUnit(base.TranslationUnit):
    """A Fluent message."""

    def __init__(self, source=None, entry=None):
        super().__init__(source)
        self._type = None
        self._id = None
        self._errors = {}
        self._attributes = {}
        self._placeables = []
        if source is not None:
            self._type = ast.Message
            self._set_value(source)
            # Default to source string
            self._id = id_from_source(self.source)
        if entry is not None:
            self.parse(entry)

    def _set_value(self, value):
        self.source = value
        # The source and target are equivalent for monolingual units.
        self.target = self.source

    def getid(self):
        return self._id

    def setid(self, value):
        self._id = value

    def adderror(self, errorname, errortext):
        self._errors[errorname] = errortext

    def geterrors(self):
        return self._errors

    def isheader(self):
        return self._type in [
            ast.Comment,
            ast.GroupComment,
            ast.ResourceComment,
        ]

    def getattributes(self):
        return self._attributes

    def getplaceables(self):
        return self._placeables

    def parse(self, entry):
        this = self

        class Parser(visitor.Visitor):
            _found_id = False

            @staticmethod
            def visit_Attribute(node):
                this._attributes[node.id.name] = source_from_entry(node)

            @staticmethod
            def visit_Placeable(node):
                this._placeables.append(serialize_placeable(node))

            @staticmethod
            def visit_Comment(node):
                if this._type not in [ast.Message, ast.Term]:
                    this._type = ast.Comment
                this.addnote(node.content)

            @staticmethod
            def visit_GroupComment(node):
                this._type = ast.GroupComment
                this.addnote(node.content)

            @staticmethod
            def visit_ResourceComment(node):
                this._type = ast.ResourceComment
                this.addnote(node.content)

            def visit_Identifier(self, node):
                if not self._found_id:
                    # Only save the first identifier we encounter (the entry's
                    # value will also contain identifiers if it has selectors).
                    this._id = node.name
                    self._found_id = True

            def visit_Message(self, node):
                this._type = ast.Message
                this._set_value(source_from_entry(node))
                self.generic_visit(node)

            def visit_Term(self, node):
                this._type = ast.Term
                this._set_value(source_from_entry(node))
                self.generic_visit(node)

        Parser().visit(entry)

    def to_entry(self):
        fp = FluentParser(False)

        # Handle standalone comments separately; they don't have any values or
        # attributes, just comment text.
        if self._type in [ast.ResourceComment, ast.GroupComment, ast.Comment]:
            return (self._type)(self.getnotes())

        assert self.source is not None
        value = fp.maybe_get_pattern(FluentParserStream(self.source))

        attributes = [
            ast.Attribute(
                ast.Identifier(id),
                fp.maybe_get_pattern(FluentParserStream(value)),
            )
            for (id, value) in self._attributes.items()
        ]

        comment = None
        if self.getnotes():
            comment = ast.Comment(self.getnotes())

        return (self._type if self._type is not None else ast.Message)(
            ast.Identifier(self.getid()),
            value=value,
            attributes=attributes,
            comment=comment,
        )


class FluentFile(base.TranslationStore):
    """A Fluent file."""

    Name = "Fluent file"
    Mimetypes = []
    Extensions = ["ftl"]
    UnitClass = FluentUnit

    def __init__(self, inputfile=None, **kwargs):
        super().__init__(**kwargs)
        self.filename = getattr(inputfile, "name", "")
        if inputfile is not None:
            fluentsrc = inputfile.read()
            self.parse(fluentsrc)

    def parse(self, fluentsrc):
        resource = parse(fluentsrc.decode("utf-8"))
        for entry in resource.body:
            # Handle this unit separately if it is invalid.
            if isinstance(entry, ast.Junk):
                for annotation in entry.annotations:
                    raise ValueError(
                        f"{annotation.code}: {annotation.message} [offset {annotation.span.start}]"
                    )

            self.addunit(FluentUnit(entry=entry))

    def serialize(self, out):
        body = [unit.to_entry() for unit in self.units]
        out.write(serialize(ast.Resource(body)).encode(self.encoding))
