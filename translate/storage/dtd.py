#
# Copyright 2002-2013 Zuza Software Foundation
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

r"""
Classes that hold units of .dtd files (:class:`dtdunit`) or entire files
(:class:`dtdfile`).

These are specific .dtd files for localisation used by mozilla.

Specifications
    The following information is provided by Mozilla:

    `Specification <http://www.w3.org/TR/REC-xml/#sec-entexpand>`_

    There is a grammar for entity definitions, which isn't really precise,
    as the spec says.  There's no formal specification for DTD files, it's
    just "whatever makes this work" basically. The whole piece is clearly not
    the strongest point of the xml spec

    XML elements are allowed in entity values. A number of things that are
    allowed will just break the resulting document, Mozilla forbids these
    in their DTD parser.

Dialects
    There are two dialects:

    - Regular DTD
    - Android DTD

    Both dialects are similar, but the Android DTD uses some particular escapes
    that regular DTDs don't have.

Escaping in regular DTD
    In DTD usually there are characters escaped in the entities. In order to
    ease the translation some of those escaped characters are unescaped when
    reading from, or converting, the DTD, and that are escaped again when
    saving, or converting to a DTD.

    In regular DTD the following characters are usually or sometimes escaped:

    - The % character is escaped using &#037; or &#37; or &#x25;
    - The " character is escaped using &quot;
    - The ' character is escaped using &apos; (partial roundtrip)
    - The & character is escaped using &amp;
    - The < character is escaped using &lt; (not yet implemented)
    - The > character is escaped using &gt; (not yet implemented)

    Besides the previous ones there are a lot of escapes for a huge number of
    characters. This escapes usually have the form of &#NUMBER; where NUMBER
    represents the numerical code for the character.

    There are a few particularities in DTD escaping. Some of the escapes are
    not yet implemented since they are not really necessary, or because its
    implementation is too hard.

    A special case is the ' escaping using &apos; which doesn't provide a full
    roundtrip conversion in order to support some special Mozilla DTD files.

    Also the " character is never escaped in the case that the previous
    character is = (the sequence =" is present on the string) in order to avoid
    escaping the " character indicating an attribute assignment, for example in
    a href attribute for an a tag in HTML (anchor tag).

Escaping in Android DTD
    It has the sames escapes as in regular DTD, plus this ones:

    - The ' character is escaped using \&apos; or \' or \u0027
    - The " character is escaped using \&quot;
"""

import re
import warnings
from io import BytesIO

from lxml import etree

from translate.misc import quote
from translate.storage import base

labelsuffixes = (".label", ".title")
"""Label suffixes: entries with this suffix are able to be comibed with accesskeys
found in in entries ending with :attr:`.accesskeysuffixes`"""
accesskeysuffixes = (".accesskey", ".accessKey", ".akey")
"""Accesskey Suffixes: entries with this suffix may be combined with labels
ending in :attr:`.labelsuffixes` into accelerator notation"""


end_entity_re = re.compile(rb"[\"']\s*>")


def quoteforandroid(source):
    """Escapes a line for Android DTD files."""
    # Replace "'" character with the \u0027 escape. Other possible replaces are
    # "\\&apos;" or "\\'".
    source = source.replace("'", "\\u0027")
    source = source.replace('"', "\\&quot;")
    return quotefordtd(source)  # value is an UTF-8 encoded string.


def unquotefromandroid(source):
    """Unquotes a quoted Android DTD definition."""
    value = unquotefromdtd(source)  # value is an UTF-8 encoded string.
    value = value.replace("\\&apos;", "'")
    value = value.replace("\\'", "'")
    value = value.replace("\\u0027", "'")
    return value.replace('\\"', '"')  # This converts \&quot; to ".


_DTD_CODEPOINT2NAME = {
    ord("%"): "#037",  # Always escape % sign as &#037;.
    ord("&"): "amp",
    # ord("<"): "lt",  # Not really so useful.
    # ord(">"): "gt",  # Not really so useful.
}


def quotefordtd(source):
    """Quotes and escapes a line for regular DTD files."""
    source = quote.entityencode(source, _DTD_CODEPOINT2NAME)
    if '"' in source:
        source = source.replace("'", "&apos;")  # This seems not to run.
        if '="' not in source:  # Avoid escaping " chars in href attributes.
            source = source.replace('"', "&quot;")
            value = f'"{source}"'  # Quote using double quotes.
        else:
            value = f"'{source}'"  # Quote using single quotes.
    else:
        value = f'"{source}"'  # Quote using double quotes.
    return value


_DTD_NAME2CODEPOINT = {
    "quot": ord('"'),
    "amp": ord("&"),
    # "lt": ord("<"),  # Not really so useful.
    # "gt": ord(">"),  # Not really so useful.
    # FIXME these should probably be handled in a more general way
    "#x0022": ord('"'),
    "#187": ord("»"),
    "#037": ord("%"),
    "#37": ord("%"),
    "#x25": ord("%"),
}


def unquotefromdtd(source):
    """Unquotes a quoted dtd definition."""
    # extract the string, get rid of quoting
    if len(source) == 0:
        source = '""'
    # The quote characters should be the first and last characters in the
    # string. Of course there could also be quote characters within the string.
    quotechar = source[0]
    extracted, _quotefinished = quote.extractwithoutquotes(
        source, quotechar, quotechar, allowreentry=False
    )
    if quotechar == "'":
        extracted = extracted.replace("&apos;", "'")
    return quote.entitydecode(extracted, _DTD_NAME2CODEPOINT)


def removeinvalidamps(name, value):
    """
    Find and remove ampersands that are not part of an entity definition.

    A stray & in a DTD file can break an application's ability to parse the
    file. In Mozilla localisation this is very important and these can break the
    parsing of files used in XUL and thus break interface rendering. Tracking
    down the problem is very difficult, thus by removing potential broken
    ampersand and warning the users we can ensure that the output DTD will
    always be parsable.

    :type name: String
    :param name: Entity name
    :type value: String
    :param value: Entity text value
    :rtype: String
    :return: Entity value without bad ampersands
    """

    def is_valid_entity_name(name):
        """Check that supplied *name* is a valid entity name."""
        return name.replace(".", "").replace("_", "").isalnum() or (
            name[0] == "#" and name[1:].isalnum()
        )

    amppos = 0
    invalid_amps = []
    while amppos >= 0:
        amppos = value.find("&", amppos)
        if amppos != -1:
            amppos += 1
            semipos = value.find(";", amppos)
            if semipos != -1 and is_valid_entity_name(value[amppos:semipos]):
                continue
            invalid_amps.append(amppos - 1)
    if len(invalid_amps) > 0:
        warnings.warn(f"invalid ampersands in dtd entity {name}")
        for adjustment, amppos in enumerate(invalid_amps):
            value = value[: amppos - adjustment] + value[amppos - adjustment + 1 :]
    return value


class dtdunit(base.TranslationUnit):
    """An entity definition from a DTD file (and any associated comments)."""

    def __init__(self, source="", android=False):
        """Construct the dtdunit, prepare it for parsing."""
        self.android = android

        super().__init__(source)
        self.comments = []
        self.unparsedlines = []
        self.incomment = False
        self.inentity = False
        self.entity = "FakeEntityOnlyForInitialisationAndTesting"
        self.source = source
        self.space_pre_entity = " "
        self.space_pre_definition = " "
        self.closing = ">"

    # Note that source and target are equivalent for monolingual units
    @property
    def source(self):
        """Gets the unquoted source string."""
        if self.android:
            return unquotefromandroid(self.definition)
        return unquotefromdtd(self.definition)

    @source.setter
    def source(self, source):
        """Sets the definition to the quoted value of source."""
        if self.android:
            self.definition = quoteforandroid(source)
        else:
            self.definition = quotefordtd(source)
        self._rich_source = None

    @property
    def target(self):
        """Gets the unquoted target string."""
        if self.android:
            return unquotefromandroid(self.definition)
        return unquotefromdtd(self.definition)

    @target.setter
    def target(self, target):
        """Sets the definition to the quoted value of target."""
        if target is None:
            target = ""
        if self.android:
            self.definition = quoteforandroid(target)
        else:
            self.definition = quotefordtd(target)
        self._rich_target = None

    def getid(self):
        return self.entity

    def setid(self, new_id):
        self.entity = new_id

    def getlocations(self):
        """Return the entity as location (identifier)."""
        assert quote.rstripeol(self.entity) == self.entity
        return [self.entity]

    def addlocation(self, location):
        """Set the entity to the given "location"."""
        self.entity = location

    def isblank(self):
        """Returns whether this dtdunit doesn't actually have an entity definition."""
        # for dtds, we currently return a blank string if there is no .entity (==location in other files)
        # TODO: this needs to work better with base class expectations
        return self.entity is None

    def istranslatable(self):
        return getattr(self, "entityparameter", None) != "SYSTEM" and not self.isblank()

    def __str__(self):
        """Convert to a string."""
        return self.getoutput()

    def getoutput(self):
        """Convert the dtd entity back to string form."""
        lines = []
        lines.extend([comment for commenttype, comment in self.comments])
        lines.extend(self.unparsedlines)
        if self.isblank():
            result = "".join(lines)
            return f"{result.rstrip()}\n"
        # for f in self._locfilenotes: yield f
        # for ge in self._locgroupends: yield ge
        # for gs in self._locgroupstarts: yield gs
        # for n in self._locnotes: yield n
        if len(self.entity) > 0:
            if getattr(self, "entitytype", None) == "external":
                entityline = f"<!ENTITY % {self.entity} {self.entityparameter} {self.definition}{self.closing}"
            else:
                entityline = f"<!ENTITY{self.space_pre_entity}{self.entity}{self.space_pre_definition}{self.definition}{self.closing}"
            if getattr(self, "hashprefix", None):
                entityline = f"{self.hashprefix} {entityline}"
            lines.append(f"{entityline}\n")
        return "".join(lines)


class dtdfile(base.TranslationStore):
    """A .dtd file made up of dtdunits."""

    UnitClass = dtdunit

    def __init__(self, inputfile=None, android=False):
        """Construct a dtdfile, optionally reading in from inputfile."""
        super().__init__()
        self.filename = getattr(inputfile, "name", "")
        self.android = android
        if inputfile is not None:
            dtdsrc = inputfile.read()
            self.parse(dtdsrc)

    def _determine_comment_type(self, comment: str) -> str:
        """Determine the type of a DTD comment."""
        if comment.find("LOCALIZATION NOTE") != -1:
            pos = quote.findend(comment, "LOCALIZATION NOTE")
            while pos < len(comment) and comment[pos] == " ":
                pos += 1
            if comment.find("FILE", pos) == pos:
                return "locfile"
            if comment.find("BEGIN", pos) == pos:
                return "locgroupstart"
            if comment.find("END", pos) == pos:
                return "locgroupend"
            return "locnote"
        return "comment"

    def _store_comment(self, unit: dtdunit, commenttype: str, comment: str) -> None:
        """Store a comment in the appropriate list on the unit."""
        commentpair = (commenttype, comment)
        comment_targets = {
            "locfile": unit._locfilenotes,
            "locgroupstart": unit._locgroupstarts,
            "locgroupend": unit._locgroupends,
            "locnote": unit._locnotes,
            "comment": unit.comments,
        }
        comment_targets.get(commenttype, unit.comments).append(commentpair)

    def _parse_entity_name(self, line: str) -> tuple[str, str, str, str, int]:
        """
        Parse entity name from line and return entity info.

        Returns:
            tuple: (entity_name, entitytype, space_pre_entity, space_pre_definition, position)

        """
        e = 0
        while e < len(line) and line[e].isspace():
            e += 1
        space_pre_entity = " " * e
        entity_name = ""
        entitytype = "internal"

        if e < len(line) and line[e] == "%":
            entitytype = "external"
            e += 1
            while e < len(line) and line[e].isspace():
                e += 1

        while e < len(line) and not line[e].isspace():
            entity_name += line[e]
            e += 1
        s = e

        while e < len(line) and line[e].isspace():
            e += 1
        space_pre_definition = " " * (e - s)

        return entity_name, entitytype, space_pre_entity, space_pre_definition, e

    def _extract_entity_definition(
        self, line: str, entityhelp: tuple[int, str], instring: bool
    ) -> tuple[str, bool]:
        """
        Extract entity definition from line.

        Returns:
            tuple: (definition_part, still_in_string) or raises ValueError

        """
        e = entityhelp[0]
        quote_char = entityhelp[1]

        if quote_char == "'":
            return quote.extract(
                line[e:], "'", "'", startinstring=instring, allowreentry=False
            )
        if quote_char == '"':
            return quote.extract(
                line[e:], '"', '"', startinstring=instring, allowreentry=False
            )
        raise ValueError(f"Unexpected quote character... {quote_char!r}")

    def parse(self, dtdsrc):
        """Read the source code of a dtd file in and include them as dtdunits in self.units."""
        if not dtdsrc:
            return

        # Decode the source
        source = dtdsrc.decode(self.encoding)
        lines = source.split("\n")

        # When splitting by "\n", a trailing newline creates an empty string at the end.
        # For example: "text\n" → ["text", ""]
        # We remove this empty element to avoid creating an unwanted blank unit.
        # Intentional blank lines (e.g., "text\n\n") still work correctly:
        # "text\n\n" → ["text", "", ""] → ["text", ""] (one blank line preserved)
        if lines and not lines[-1]:
            lines = lines[:-1]

        # Parse state
        line_idx = 0

        while line_idx < len(lines):
            # Create a new unit
            newdtd = dtdunit(android=self.android)

            # Initialize unit state
            newdtd.comments = []
            newdtd._locfilenotes = newdtd.comments
            newdtd._locgroupstarts = newdtd.comments
            newdtd._locgroupends = newdtd.comments
            newdtd._locnotes = newdtd.comments
            newdtd.entity = None
            newdtd.definition = ""
            newdtd.unparsedlines = []

            # Parsing state variables
            incomment = False
            continuecomment = False
            inentity = False
            commenttype = "comment"
            entitypart = None
            entitytype = "internal"
            entityhelp = None
            instring = False
            space_pre_entity = ""
            space_pre_definition = ""

            has_content = False  # Track if this unit has any content
            malformed = False  # Track if this unit is malformed

            # Parse lines until we have a complete unit or find the start of the next one
            while line_idx < len(lines):
                line = lines[line_idx] + "\n"

                if not incomment:
                    if line.find("<!--") != -1:
                        incomment = True
                        continuecomment = False
                        has_content = True
                        # Work out the type of comment
                        comment, _dummy = quote.extract(line, "<!--", "-->", None, 0)
                        commenttype = self._determine_comment_type(comment)
                    elif not inentity and re.search(r"%[^;%]+;", line):
                        # Entity reference line
                        newdtd.comments.append(("comment", line))
                        has_content = True
                        line = ""
                        line_idx += 1
                        continue

                if incomment:
                    # Parse comment
                    (comment, incomment) = quote.extract(
                        line, "<!--", "-->", None, continuecomment
                    )
                    continuecomment = incomment
                    # Strip the comment out of what will be parsed
                    line = line.replace(comment, "", 1)
                    # Add an end of line if this is the end of the comment
                    if not incomment:
                        if line.isspace():
                            comment += line
                            line = ""
                        else:
                            comment += "\n"
                    # Store the comment
                    self._store_comment(newdtd, commenttype, comment)

                if not inentity and not incomment:
                    entitypos = line.find("<!ENTITY")
                    if entitypos != -1:
                        inentity = True
                        has_content = True
                        beforeentity = line[:entitypos].strip()
                        if beforeentity.startswith("#"):
                            newdtd.hashprefix = beforeentity
                        entitypart = "start"
                    else:
                        # Add to unparsed lines
                        newdtd.unparsedlines.append(line)
                        if not line.isspace():
                            has_content = True

                if inentity:
                    if entitypart == "start":
                        # The entity definition
                        e = quote.findend(line, "<!ENTITY")
                        line = line[e:]
                        entitypart = "name"

                    if entitypart == "name":
                        (
                            entity_name,
                            entitytype,
                            space_pre_entity,
                            space_pre_definition,
                            e,
                        ) = self._parse_entity_name(line)

                        newdtd.entity = entity_name
                        assert quote.rstripeol(entity_name) == entity_name
                        if newdtd.entity:
                            newdtd.entitytype = entitytype
                            if entitytype == "external":
                                entitypart = "parameter"
                                newdtd.entityparameter = ""
                            else:
                                entitypart = "definition"
                            # Remember the start position and the quote character
                            if e == len(line):
                                entityhelp = None
                                e = 0
                                line_idx += 1
                                continue
                            if entitypart == "definition":
                                entityhelp = (e, line[e])
                                instring = False

                    if entitypart == "parameter":
                        while e < len(line) and line[e].isspace():
                            e += 1
                        paramstart = e
                        while e < len(line) and line[e].isalnum():
                            e += 1
                        newdtd.entityparameter += line[paramstart:e]
                        while e < len(line) and line[e].isspace():
                            e += 1
                        line = line[e:]
                        e = 0
                        if not line:
                            line_idx += 1
                            continue
                        if line[0] in {'"', "'"}:
                            entitypart = "definition"
                            entityhelp = (e, line[e])
                            instring = False

                    if entitypart == "definition":
                        if entityhelp is None:
                            e = 0
                            while e < len(line) and line[e].isspace():
                                e += 1
                            if e == len(line):
                                line_idx += 1
                                continue
                            entityhelp = (e, line[e])
                            instring = False
                        # Extract the definition part
                        e = entityhelp[0]
                        try:
                            defpart, instring = self._extract_entity_definition(
                                line, entityhelp, instring
                            )
                        except ValueError as exc:
                            # Handle malformed entities gracefully
                            warnings.warn(str(exc))
                            # Mark as malformed and skip to next line
                            malformed = True
                            line_idx += 1
                            break
                        # For any following lines, start at the beginning of the line
                        entityhelp = (0, entityhelp[1])
                        newdtd.definition += defpart
                        if not instring:
                            closing = line[e + len(defpart) :].rstrip("\n\r")
                            inentity = False
                            # Entity is complete
                            newdtd.space_pre_entity = space_pre_entity
                            newdtd.space_pre_definition = space_pre_definition
                            newdtd.closing = closing
                            line_idx += 1
                            break

                line_idx += 1

                # If we have no entity and no comment in progress and no content, skip this unit
                if (
                    not inentity
                    and not incomment
                    and not has_content
                    and line_idx < len(lines)
                ):
                    break

            # Add the unit if it's not blank or has unparsed lines or has comments,
            # but skip malformed entities
            if not malformed and (
                not newdtd.isblank() or newdtd.unparsedlines or newdtd.comments
            ):
                self.units.append(newdtd)

    def serialize(self, out):
        """Write content to file."""
        content = b""
        for dtd in self.units:
            unit_str = str(dtd).encode(self.encoding)
            out.write(unit_str)
            content += unit_str
        if not self._valid_store(content):
            warnings.warn(f"DTD file '{self.filename}' does not validate")
            out.truncate(0)

    def _valid_store(self, content):
        """
        Validate the store to determine if it is valid.

        This uses ElementTree to parse the DTD

        :return: If the store passes validation
        :rtype: Boolean
        """
        # Android files are invalid DTDs
        if not self.android:
            # #expand is a Mozilla hack and are removed as they are not valid in DTDs
            input_ = content.replace(rb"#expand", b"")
            try:
                etree.DTD(BytesIO(input_))
            except etree.DTDParseError as e:
                warnings.warn(f"DTD parse error: {e.error_log}")
                return False
        return True
