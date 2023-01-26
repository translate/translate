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

import re
import textwrap

from fluent.syntax import FluentSerializer, ast, parse, serialize, visitor

from translate.storage import base


class FluentUnit(base.TranslationUnit):
    """Represents a single fluent Message, Term, a ResourceComment, a
    GroupComment or a stand-alone Comment.
    """

    def __init__(
        self,
        source=None,
        unit_id=None,
        comment="",
        fluent_type="Message",
        placeholders=None,
    ):
        """
        :param source: The serialized fluent value, or None.
        :type source: str or None
        :param unit_id: An optional id to set (see :meth:`~FluentUnit.setid`),
            otherwise an id is generated from the given `source`.
        :type unit_id: str or None
        :param str comment: An optional comment for the unit.
        :param str fluent_type: The fluent type this unit corresponds to.
        :param placeholders: An optional list of sub-strings of the source that
            should be highlighted as placeholders. A translation of this unit
            would be expected to contain the same sub-strings.
        :type placeholders: list[str] or None
        """
        if fluent_type not in (
            "Message",
            "Term",
            "ResourceComment",
            "GroupComment",
            "DetachedComment",
        ):
            raise ValueError(f'Unknown value "{fluent_type}" for fluent_type')
        super().__init__(source)
        self._fluent_type = fluent_type
        self._is_comment = fluent_type.endswith("Comment")
        self.placeholders = placeholders or []
        self.target = source
        if unit_id is None and fluent_type == "Message" and source:
            unit_id = self._id_from_source(source)
        self.setid(unit_id)
        self.addnote(comment)

    @staticmethod
    def _id_from_source(source):
        # If the caller does not provide a unit ID, we need to generate one
        # ourselves.
        # The set of valid ids is restricted, so we cannot use the source string
        # as the identifier (as e.g. PO files do). Instead, we hash the source
        # string with a collision-resistant hash function.
        # By default, we choose an id that indicates that this represents a
        # fluent Message.
        import hashlib

        return "gen-" + hashlib.sha256(source.encode()).hexdigest()

    def getid(self):
        return self._id

    # From fluent EBNF.
    _FLUENT_ID_PATTERN = r"[a-zA-Z][a-zA-Z0-9_-]*"
    _FLUENT_ID_REGEXES = {
        "Message": _FLUENT_ID_PATTERN,
        "Term": r"-" + _FLUENT_ID_PATTERN,
    }

    def setid(self, value):
        """Set the id of the unit.
        A valid fluent identifier is [a-zA-Z][a-zA-Z0-9_-]*
        For a FluentUnit that represents a fluent Message, the id must be a
        valid fluent identifier.
        For a fluent Term, the id must be a valid fluent identifier prefixed by
        a "-".
        For a fluent Comment, GroupComment or ResourceComment, the id is unused.
        """
        regex = self._FLUENT_ID_REGEXES.get(self._fluent_type, "")
        if not re.fullmatch(regex, value or ""):
            raise ValueError(
                f"Invalid id for a {self._fluent_type} FluentUnit: {value}"
            )
        self._id = value or None

    def isheader(self):
        return self._is_comment

    @property
    def fluent_type(self):
        """The fluent type this unit corresponds to."""
        return self._fluent_type

    def getplaceables(self):
        """Still called in Weblate. Returns :attr:`~FluentUnit.placeholders`."""
        return self.placeholders

    @classmethod
    def new_from_entry(cls, fluent_entry, comment=None):
        """Create a new unit corresponding to the given fluent AST entry.

        :param fluent_entry: A fluent Entry to convert.
        :type fluent_entry: Entry
        :param comment: A comment to set on the unit. For fluent Comments the
            comment is taken from the object instead.
        :type comment: str or None

        :return: A new FluentUnit.
        :rtype: FluentUnit
        """
        if isinstance(fluent_entry, ast.ResourceComment):
            return cls(comment=fluent_entry.content, fluent_type="ResourceComment")
        if isinstance(fluent_entry, ast.GroupComment):
            return cls(comment=fluent_entry.content, fluent_type="GroupComment")
        if isinstance(fluent_entry, ast.Comment):
            return cls(comment=fluent_entry.content, fluent_type="DetachedComment")
        if isinstance(fluent_entry, ast.Term):
            return cls._create_from_fluent_pattern(
                fluent_entry, "Term", f"-{fluent_entry.id.name}", comment
            )
        if isinstance(fluent_entry, ast.Message):
            return cls._create_from_fluent_pattern(
                fluent_entry, "Message", fluent_entry.id.name, comment
            )
        raise ValueError(f"Unhandled fluent type: {fluent_entry.__class__.__name__}")

    @classmethod
    def _create_from_fluent_pattern(cls, fluent_entry, fluent_type, unit_id, comment):
        """Create a new unit from a fluent entry that has a Pattern value."""
        lines = []
        source = cls._fluent_pattern_to_source(fluent_entry.value)
        if source:
            lines.append(source)
        for attr in fluent_entry.attributes:
            attr_source = cls._fluent_pattern_to_source(attr.value)
            source = f".{attr.id.name} ="
            if "\n" in attr_source:
                # Multi-line Attributes placed on newline.
                source += "\n"
            else:
                source += " "
            source += attr_source
            lines.append(source)
        return cls(
            source="\n".join(lines),
            unit_id=unit_id,
            comment=comment,
            fluent_type=fluent_type,
            placeholders=cls._fluent_pattern_placeholders(fluent_entry, fluent_type),
        )

    @staticmethod
    def _fluent_pattern_to_source(pattern):
        """Convert the fluent Pattern into a source string."""
        if not pattern:
            return None

        if not pattern.elements:
            raise ValueError("Unexpected fluent Pattern without any elements")

        first_element = pattern.elements[0]
        if isinstance(first_element, ast.TextElement):
            # Replace the special characters "*", "[" and "." with a
            # StringLiteral if they appear at the start of a line.
            # NOTE: These are specified in the fluent EBNF's "indented_char".
            # Normally, these characters cannot appear at the start of a line
            # for a value because they are part of the syntax, so they must be
            # escaped. However, as an exception, these characters may appear at
            # the very start of a Pattern, on the same line as the "=" sign.
            # For example:
            #     m = .start
            # or
            #     m = *start
            #         another line
            #
            # We want to escape these special characters for two reasons:
            #   1. For consistency with other lines not being able to start with
            #      such a character in multiline values. There is no "=" sign in
            #      the derived source to indicate the exception.
            #   2. To make re-serialization easier. In particular, when we
            #      serialize the FluentUnit's source, we place the source on a
            #      newline for consistent behaviour.
            first_char = first_element.value[0]
            if first_char in ("[", ".", "*"):
                # Replace with literals.
                # NOTE: An empty TextElement is ok for the FluentSerializer.
                first_element.value = first_element.value[1:]
                pattern.elements.insert(0, ast.Placeable(ast.StringLiteral(first_char)))

        # Create a fluent Message with the given pattern and serialize it.
        # We use serialize_entry which is part of python-fluent's public API.
        source = FluentSerializer().serialize_entry(
            ast.Message(ast.Identifier("i"), value=pattern)
        )

        # Strip away the id part: "i =". For single-line values, a space is also
        # added. For multi-line values, a newline is added.
        # NOTE: Since we escaped any leading special character, the newline is
        # expected to always be added for multiline values.
        source = re.sub(r"^i =( |\n)", "", source, count=1)
        # Strip away the trailing newline that the serializer adds.
        source = re.sub(r"\n$", "", source, count=1)

        # Remove the common indent.
        # NOTE: textwrap.dedent also collapses blank lines.
        return textwrap.dedent(source)

    @staticmethod
    def _fluent_pattern_placeholders(fluent_entry, fluent_type):
        """Get the placeholders expected for the given fluent entry."""
        ref_visitor = _ReferenceVisitor(fluent_type)
        ref_visitor.visit(fluent_entry.value)
        # NOTE: For Terms, we do not look through references in the Attributes.
        # Only Term's have their Attributes appear in their source, and Term
        # Attributes tend to be locale-specific, which we don't want to
        # influence the placeholders.
        # FIXME: For Messages, we expect Attributes to contain the same
        # references in translations, but the placeholders have no way to
        # distinguish between whether the placeholder is found in the same
        # attribute or not. So we do not include them.
        return list(ref_visitor.placeholders)

    def to_entry(self):
        """Convert the unit into a corresponding fluent AST Entry.

        :return: A new fluent AST Entry, if one was created.
        :rtype: Entry or None
        :raises ValueError: if the unit source contains an error.
        """
        fluent_id = self.getid()
        if fluent_id:
            # Remove the leading "-" for Terms.
            fluent_id = re.sub(r"^-", "", fluent_id, count=1)
        if self.fluent_type == "ResourceComment":
            # Create a comment, even if empty. Especially since empty
            # GroupComments are meant to end a previous GroupComment's
            # scope.
            return ast.ResourceComment(content=(self.getnotes() or ""))
        if self.fluent_type == "GroupComment":
            return ast.GroupComment(content=(self.getnotes() or ""))
        if self.fluent_type == "DetachedComment":
            return ast.Comment(content=(self.getnotes() or ""))
        if self.fluent_type in ("Term", "Message"):
            return self._source_to_fluent_entry()
        raise ValueError(f"Unhandled fluent_type: {self.fluent_type}")

    def _source_to_fluent_entry(self):
        """Convert a FluentUnit's source to a fluent Term or Message."""
        entry = self._try_source_to_fluent_entry()
        if isinstance(entry, str):
            raise ValueError(
                f'Error in source of FluentUnit "{self.getid()}":\n{entry}'
            )
        return entry

    def _try_source_to_fluent_entry(self):
        """Convert a FluentUnit's source to a generic fluent Entry. Returns a
        string with an error message if this fails.
        """
        source = self.source
        if source is None or not source.strip():
            return None

        # Create a fluent Message by prefixing the source with "unit-id = \n"
        # and parsing it. After each newline we also indent so that it is
        # considered part of the same entry.
        source_lines = [(f"{self.getid()} =", "")]
        for line in source.split("\n"):
            source_lines.append((" ", line))
        source = "\n".join([added + orig for (added, orig) in source_lines])

        # We use parse which is part of python-fluent's public API.
        # The other advantage is that the entry will return Junk with an error
        # description if there are syntax errors.
        # NOTE: We cannot reliably use FluentParser.parse_entry because it does
        # not parse the entire input, but only up until the entry ends. So if a
        # source contains syntax to start another entry it will not throw an
        # error. For example, a line that starts with "*" will end an entry.
        res = parse(source)

        # First look for junk.
        for entry in res.body:
            if isinstance(entry, ast.Junk):
                error_message = []
                for annotation in entry.annotations:
                    # Convert the fluent error position into a line number and
                    # offset of the unit's source.
                    offset = annotation.span.start
                    line = 0
                    for added, orig in source_lines:
                        if not orig:
                            # Entire line was added, so we want to skip this
                            # line. If we are within this line, then the offset
                            # will be set to "0" for the next loop.
                            line_len = len(added) + 1
                            offset = max(0, offset - line_len)
                            continue
                        added_len = len(added)
                        # Plus one for the newline/end-of-line.
                        line_len = added_len + len(orig) + 1
                        if offset < line_len:
                            # On this line.
                            offset = max(0, offset - added_len)
                            break
                        offset -= line_len
                        line += 1
                    error_message.append(
                        f"{annotation.code}: {annotation.message} "
                        f"[line {line + 1}, column {offset + 1}]"
                    )
                return "\n".join(error_message)
        if len(res.body) != 1:
            # This is unexpected since if the user tried to insert extra
            # Entries, they would have likely given us Junk above since we
            # indented *all* lines, which would prevent starting a new entry.
            return "Unexpectedly found {len(res.body)} fluent Entries"
        entry = res.body[0]
        if self.fluent_type == "Term" and not isinstance(entry, ast.Term):
            # Also unexpected since we started with "-tmp =", which starts a new
            # Term.
            return (
                f"Unexpectedly found a fluent {entry.__class__.name__} "
                "Entry rather than a Term"
            )
        if self.fluent_type != "Term" and not isinstance(entry, ast.Message):
            # Also unexpected since we started with "tmp =", which starts a new
            # Message.
            return (
                f"Unexpectedly found a fluent {entry.__class__.name__} "
                "Entry rather than a Message"
            )

        return entry


class _ReferenceVisitor(visitor.Visitor):
    """Private class used to extract the reference ids contained within a
    Pattern.
    """

    # NOTE: This class is used to extract *expected* placeholder strings. I.e. a
    # translation of this unit would *also* be expected to include this
    # placeholder text.
    #
    # We extract the MessageReferences, TermReferences and
    # VariableReferences because we would normally expect them to appear in a
    # translation.
    #
    # In contrast, other fluent Expressions are not wanted:
    #   + StringLiteral and NumberLiteral are able to represent literal
    #     characters, which wouldn't necessarily be present in a
    #     translation.
    #   + FunctionReference is for function calls, normally to format a
    #     number or date, which may not be needed in a translation.
    #   + SelectExpression is for branching logic. Whilst sometimes this
    #     would be expected in a translation (e.g. based on the plural
    #     category of a variable) it isn't always necessary (e.g. one locale
    #     branches based on whether a Term starts with a vowel or not).

    def __init__(self, fluent_type):
        self.fluent_type = fluent_type
        self.placeholders = set()

    def visit_MessageReference(self, node):
        # If a MessageReference appears in a value, we expect that to also
        # appear in a translation's value as well.
        # TODO: Are there reasonable cases where one locale would use one of
        # these references, but another would not?
        # NOTE: MessageReferences cannot be used as a SelectorExpression's
        # selector, nor do they accept callable arguments. Therefore, we only
        # expect them to appear in the form "{ message-id }".
        placeholder = "{ " + node.id.name
        if node.attribute:
            placeholder += "." + node.attribute.name
        placeholder += " }"
        self.placeholders.add(placeholder)
        # NOTE: We do not call Visitor.generic_visit because there is no child
        # to descend into for this type.

    def visit_TermReference(self, node):
        if node.attribute:
            # A TermReference with an attribute should only appear in a
            # SelectExpression as the selector. We only expect this to be a
            # locale-specific selector (e.g. based on some language property of
            # the Term) so we do not add it to our placeholders.
            return
        # Otherwise, we expect a TermReference to also appear in a translation's
        # value as well.
        # NOTE: TermReferences cannot be used as a SelectorExpression's
        # selector.
        # TODO: TermReferences can accept callable arguments. Normally these
        # arguments are locale-specific (e.g. passing in some grammatical
        # context). So it can either appear as "{ -term-id }" or something like
        # "{ -term-id(arg1: "val", arg2: "val") }".
        # Technically, something like "{ -term-id({ message-id }) }", or more
        # complex Expressions are allowed for positional arguments, but these
        # would have no use, so we only match the regex with named arguments.
        self.placeholders.add("{ -" + node.id.name + " }")

    def visit_VariableReference(self, node):
        if self.fluent_type == "Term":
            # Variables for terms are normally locale-specific (like some
            # grammatical context), so we do not include these.
            return
        # TODO: VaraibleReferences can appear as Function arguments or as
        # SelectExpression selectors, but they are not wrapped in "{" and "}"
        # in these cases.
        self.placeholders.add("{ $" + node.id.name + " }")

    def visit_SelectExpression(self, node):
        # We only want to visit the variants, rather than the select expression.
        for variant in node.variants:
            self.generic_visit(variant)


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
            self.parse(inputfile.read())

    def parse(self, fluentsrc):
        resource = parse(fluentsrc.decode("utf-8"))
        for entry in resource.body:
            # Handle this unit separately if it is invalid.
            if isinstance(entry, ast.Junk):
                raise self._fluent_junk_to_error(entry)

        resource_comments = []
        for entry in resource.body:
            if isinstance(entry, ast.ResourceComment):
                # We add another line to the comments, even if it is blank.
                resource_comments.append(entry.content)

        resource_comments = "\n".join(resource_comments)
        comment_prefix = resource_comments
        for entry in resource.body:
            if isinstance(entry, ast.BaseComment):
                self.addunit(FluentUnit.new_from_entry(entry))
                if isinstance(entry, ast.GroupComment):
                    # A GroupComment replaces the previous GroupComment.
                    comment_prefix = self._combine_comments(resource_comments, entry)
            elif isinstance(entry, (ast.Term, ast.Message)):
                self.addunit(
                    FluentUnit.new_from_entry(
                        entry,
                        self._combine_comments(comment_prefix, entry.comment),
                    )
                )
            else:
                raise ValueError(
                    f"Unhandled fluent Entry type: {entry.__class__.__name__}"
                )

    @staticmethod
    def _fluent_junk_to_error(junk):
        """Convert the given fluent Junk object into a ValueError."""
        error_message = [
            "Parsing error for fluent source: "
            + junk.content.strip()[0:64].replace("\n", "\\n")
            + "[...]"
        ]
        for annotation in junk.annotations:
            error_message.append(
                f"{annotation.code}: {annotation.message} [offset {annotation.span.start}]"
            )
        return ValueError("\n".join(error_message))

    @staticmethod
    def _combine_comments(*comments):
        """Combine the given string or fluent BaseComment objects into a single
        string.
        """
        comment_text = []
        for part in comments:
            if isinstance(part, ast.BaseComment):
                comment_text.append(part.content)
            else:
                comment_text.append(part)
        return "\n".join(text for text in comment_text if text)

    def serialize(self, out):
        prefix_comments = []
        for unit in self.units:
            if unit.fluent_type == "ResourceComment":
                prefix_comments.append(unit.getnotes() or "")
        prev_group_comment = ""

        body = []
        for unit in self.units:
            entry = unit.to_entry()
            if not entry:
                continue
            if unit.fluent_type == "GroupComment":
                group_comment = entry.content
                if group_comment != prev_group_comment:
                    if not prev_group_comment:
                        prefix_comments.append(group_comment)
                    elif not group_comment:
                        prefix_comments = prefix_comments[:-1]
                    else:
                        prefix_comments[-1] = group_comment
                    prev_group_comment = group_comment
            elif unit.fluent_type in ("Term", "Message"):
                comment = self._strip_prefix_from_comment(unit, prefix_comments)
                if comment:
                    entry.comment = ast.Comment(comment)
            body.append(entry)

        serialized = serialize(ast.Resource(body))
        # The Fluent parser may insert a blank line "    \n" in a multiline
        # value that has a gap. We tidy those up here.
        serialized = re.sub(r"\n +\n", "\n\n", serialized)
        out.write(serialized.encode(self.encoding))

    @staticmethod
    def _strip_prefix_from_comment(unit, prefix_comments):
        """Try to remove each prefix in `prefix_comments` in turn from the start
        of `unit`'s comment.
        """
        unit_comment = unit.getnotes() or ""
        for prefix in prefix_comments:
            if unit_comment == prefix:
                return ""
            # Remove the prefix as a block.
            # NOTE: removeprefix only available in python 3.9+.
            block = prefix + "\n"
            if unit_comment.startswith(block):
                unit_comment = unit_comment[len(block) :]
        return unit_comment
