#
# Copyright 2002-2009 Zuza Software Foundation
# Copyright 2013 F Wolff
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

"""Classes that hold units of Gettext .po files (pounit) or entire
files (pofile).
"""

import copy
import logging
import re
import textwrap
import unicodedata
from typing import List, Tuple

from translate.misc import quote
from translate.misc.multistring import multistring
from translate.storage import pocommon, poparser


logger = logging.getLogger(__name__)


lsep = "\n#: "
"""Separator for #: entries"""

# general functions for quoting / unquoting po strings

po_unescape_map = {"\\r": "\r", "\\t": "\t", '\\"': '"', "\\n": "\n", "\\\\": "\\"}
po_escape_map = {value: key for (key, value) in po_unescape_map.items()}


def splitlines(text):
    """Split lines based on first newline char.

    Can not use univerzal newlines as they match any newline like
    character inside text and that breaks on files with unix newlines
    and LF chars inside comments.

    The code looks for first msgid and looks for newline used after it. This
    should safely cover weird newlines used in comments or filenames, while
    properly parsing po files with any newlines.
    """
    # Strip UTF-8 BOM if present. This file would not be accepted
    # by gettext, but some editors might create it, so better handle it.
    if text[:3] == b"\xEF\xBB\xBF":
        text = text[3:]
    # Find first newline
    newline = b"\n"
    msgid_pos = max(0, text.find(b"\rmsgid ") + 1, text.find(b"\nmsgid ") + 1)
    for i, ch in enumerate(text[msgid_pos:]):
        # Iteration over bytes yields numbers in Python 3
        if ch == 10:
            break
        if ch == 13:
            if text[msgid_pos + i + 1] == 10:
                newline = b"\r\n"
            else:
                newline = b"\r"
            break

    return [x + newline for x in text.split(newline)], newline.decode()


def escapeforpo(line):
    """Escapes a line for po format. assumes no \n occurs in the line.

    :param line: unescaped text
    """
    special_locations = []
    for special_key in po_escape_map:
        special_locations.extend(quote.find_all(line, special_key))
    special_locations = sorted(dict.fromkeys(special_locations).keys())
    escaped_line = []
    last_location = 0
    for location in special_locations:
        escaped_line.append(line[last_location:location])
        escaped_line.append(po_escape_map[line[location : location + 1]])
        last_location = location + 1
    escaped_line.append(line[last_location:])
    return "".join(escaped_line)


def unescapehandler(escape):
    return po_unescape_map.get(escape, escape)


WIDE_CHARS = {"F", "W"}


def cjklen(text: str) -> int:
    """
    Return the real width of an unicode text, the len of any other type.

    Fullwidth and Wide CJK chars are double-width.
    """
    return sum(
        2 if unicodedata.east_asian_width(char) in WIDE_CHARS else 1 for char in text
    )


def cjkslices(text: str, index: int) -> Tuple[str, str]:
    """Return the two slices of a text cut to the index."""
    if cjklen(text) <= index:
        return text, ""
    length = 0
    i = 0
    for i in range(len(text)):
        length += cjklen(text[i])
        if length > index:
            break
    return text[:i], text[i:]


class PoWrapper(textwrap.TextWrapper):
    """
    Customized TextWrapper

    - custom word separator regexp
    - full width chars accounting, based on https://bugs.python.org/issue24665
    - dropped support for unused features (for example max_lines or drop_whitespace)
    """

    wordsep_re = re.compile(
        r"""
            (
            \s+|                                  # any whitespace
            [a-z0-9A-Z_-]+/|                      # nicely split long URLs
            \w*\\.\w*|                            # any escape should not be split
            n(?=%)|                               # wrap insidide plural equation
            \.(?=\w)|                             # full stop inside word
            [\w\!\'\&\.\,\?=<>%]+\s+|             # space should go with a word
            [^\s\w]*\w+[a-zA-Z]-(?=\w+[a-zA-Z])|  # hyphenated words
            (?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w)    # em-dash
            )
        """,
        re.VERBOSE,
    )

    def __init__(self, width=77):
        super().__init__(
            width=width,
            replace_whitespace=False,
            expand_tabs=False,
            drop_whitespace=False,
            break_long_words=True,
        )

    def _handle_long_word(
        self, reversed_chunks: List[str], cur_line: List[str], cur_len: int, width: int
    ):
        """
        Handle a chunk of text (most likely a word, not whitespace) that
        is too long to fit in any line.
        """
        # Figure out when indent is larger than the specified width, and make
        # sure at least one character is stripped off on every pass
        if width < 1:
            space_left = 1
        else:
            space_left = width - cur_len

        # We're allowed to break long words, then do so: put as much
        # of the next chunk onto the current line as will fit.
        chunk_start, chunk_end = cjkslices(reversed_chunks[-1], space_left)
        cur_line.append(chunk_start)
        reversed_chunks[-1] = chunk_end

    def _wrap_chunks(self, chunks: List[str]) -> List[str]:
        lines = []
        if self.width <= 1:
            raise ValueError("invalid width %r (must be > 1)" % self.width)

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)

            while chunks:
                l = cjklen(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and cjklen(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            if cur_line:
                # Convert current line back to a string and store it in
                # list of all lines (return value).
                lines.append(indent + "".join(cur_line))
        return lines


def quoteforpo(text, wrapper_obj=None):
    """Quotes the given text for a PO file, returning quoted and escaped lines"""
    if text is None:
        return []
    if wrapper_obj is None:
        wrapper_obj = PoWrapper()
    text = escapeforpo(text)
    if wrapper_obj.width == -1:
        return ['"%s"' % text]
    lines = text.split("\\n")
    for i, l in enumerate(lines[:-1]):
        lines[i] = l + "\\n"

    polines = []
    len_lines = len(lines)
    if (
        len_lines > 2
        or (len_lines == 2 and lines[1])
        or len(lines[0]) > wrapper_obj.width - 6
    ):
        polines.append('""')
    for line in lines:
        lns = wrapper_obj.wrap(line)
        for ln in lns:
            polines.append('"%s"' % ln)
    return polines


def unescape(line):
    """Unescape the given line.

    Quotes on either side should already have been removed.
    """
    escape_places = quote.find_all(line, "\\")
    if not escape_places:
        return line

    # filter escaped escapes
    true_escape = False
    true_escape_places = []
    for escape_pos in escape_places:
        if escape_pos - 1 in escape_places:
            true_escape = not true_escape
        else:
            true_escape = True
        if true_escape:
            true_escape_places.append(escape_pos)

    extracted = []
    lastpos = 0
    for pos in true_escape_places:
        # everything leading up to the escape
        extracted.append(line[lastpos:pos])
        # the escaped sequence (consuming 2 characters)
        extracted.append(unescapehandler(line[pos : pos + 2]))
        lastpos = pos + 2

    extracted.append(line[lastpos:])
    return "".join(extracted)


def unquotefrompo(postr):
    return "".join(unescape(line[1:-1]) for line in postr)


def is_null(lst):
    return lst == [] or len(lst) == 1 and lst[0] == '""'


def extractstr(string):
    left = string.find('"')
    right = string.rfind('"')
    if right > -1:
        return string[left : right + 1]
    return string[left:] + '"'


class pounit(pocommon.pounit):
    # othercomments = []      #   # this is another comment
    # automaticcomments = []  #   #. comment extracted from the source code
    # sourcecomments = []     #   #: sourcefile.xxx:35
    # prev_msgctxt = []       #   #| The previous values that msgctxt and msgid held
    # prev_msgid = []         #
    # prev_msgid_plural = []  #
    # typecomments = []       #   #, fuzzy
    # msgidcomments = []      #   _: within msgid
    # msgctxt
    # msgid = []
    # msgstr = []

    # Our homegrown way to indicate what must be copied in a shallow
    # fashion
    __shallow__ = ["_store", "wrapper"]

    def __init__(self, source=None, wrapper=None, **kwargs):
        self.wrapper = wrapper
        self.obsolete = False
        self._initallcomments(blankall=True)
        self.prev_msgctxt = []
        self.prev_msgid = []
        self.prev_msgid_plural = []
        self.msgctxt = []
        self.msgid = []
        self.msgid_pluralcomments = []
        self.msgid_plural = []
        self.msgstr = []
        super().__init__(source)

    @property
    def newline(self):
        if self._store is not None:
            return self._store.newline
        return "\n"

    def _initallcomments(self, blankall=False):
        """Initialises allcomments"""
        if blankall:
            self.othercomments = []
            self.automaticcomments = []
            self.sourcecomments = []
            self.typecomments = []
            self.msgidcomments = []

    def _get_all_comments(self):
        return [
            self.othercomments,
            self.automaticcomments,
            self.sourcecomments,
            self.typecomments,
            self.msgidcomments,
        ]

    allcomments = property(_get_all_comments)

    def _get_source_vars(self, msgid, msgid_plural):
        singular = unquotefrompo(msgid)
        if self.hasplural():
            pluralform = unquotefrompo(msgid_plural)
            return multistring([singular, pluralform])
        return singular

    def quote(self, text):
        return quoteforpo(text, self.wrapper)

    def _set_source_vars(self, source):
        msgid = None
        msgid_plural = None
        if isinstance(source, multistring):
            source = source.strings
        if isinstance(source, list):
            msgid = self.quote(source[0])
            if len(source) > 1:
                msgid_plural = self.quote(source[1])
            else:
                msgid_plural = []
        else:
            msgid = self.quote(source)
            msgid_plural = []
        return msgid, msgid_plural

    @property
    def source(self):
        """Returns the unescaped msgid"""
        return self._get_source_vars(self.msgid, self.msgid_plural)

    @source.setter
    def source(self, source):
        """Sets the msgid to the given (unescaped) value.

        :param source: an unescaped source string.
        """
        self._rich_source = None
        self.msgid, self.msgid_plural = self._set_source_vars(source)

    def _get_prev_source(self):
        """Returns the unescaped msgid"""
        return self._get_source_vars(self.prev_msgid, self.prev_msgid_plural)

    def _set_prev_source(self, source):
        """Sets the msgid to the given (unescaped) value.

        :param source: an unescaped source string.
        """
        self.prev_msgid, self.prev_msgid_plural = self._set_source_vars(source)

    prev_source = property(_get_prev_source, _set_prev_source)

    @property
    def target(self):
        """Returns the unescaped msgstr"""
        if isinstance(self.msgstr, dict):
            return multistring(list(map(unquotefrompo, self.msgstr.values())))
        return unquotefrompo(self.msgstr)

    @target.setter
    def target(self, target):
        """Sets the msgstr to the given (unescaped) value"""
        self._rich_target = None
        if self.hasplural():
            if isinstance(target, multistring):
                target = target.strings
            elif isinstance(target, str):
                target = [target]
        elif isinstance(target, (dict, list)):
            if len(target) == 1:
                target = target[0]
            else:
                raise ValueError(
                    "po msgid element has no plural but msgstr has %d elements (%s)"
                    % (len(target), target)
                )
        templates = self.msgstr
        if isinstance(templates, list):
            templates = {0: templates}
        if isinstance(target, list):
            self.msgstr = {i: self.quote(target[i]) for i in range(len(target))}
        elif isinstance(target, dict):
            self.msgstr = {
                i: self.quote(targetstring) for i, targetstring in target.items()
            }
        else:
            self.msgstr = self.quote(target)

    def getalttrans(self):
        """Return a list of alternate units.

        Previous msgid and current msgstr is combined to form a single
        alternative unit.
        """
        prev_source = self.prev_source
        if prev_source and self.isfuzzy():
            unit = type(self)(prev_source)
            unit.target = self.target
            # Already released versions of Virtaal (0.6.x) only supported XLIFF
            # alternatives, and expect .xmlelement.get().
            # This can be removed soon:
            unit.xmlelement = {}
            return [unit]
        return []

    def getnotes(self, origin=None):
        """Return comments based on origin value.

        :param origin: programmer, developer, source code, translator or None
        """
        if origin is None:
            comments = "".join(
                comment[2:] or self.newline for comment in self.othercomments
            )
            comments += "".join(
                comment[3:] or self.newline for comment in self.automaticcomments
            )
        elif origin == "translator":
            comments = "".join(
                comment[2:] or self.newline for comment in self.othercomments
            )
        elif origin in ["programmer", "developer", "source code"]:
            comments = "".join(
                comment[3:] or self.newline for comment in self.automaticcomments
            )
        else:
            raise ValueError("Comment type not valid")
        # Let's drop the last newline
        return comments[:-1]

    def addnote(self, text, origin=None, position="append"):
        """This is modeled on the XLIFF method.

        See :meth:`translate.storage.xliff.xliffunit.addnote`
        """
        # ignore empty strings and strings without non-space characters
        if not (text and text.strip()):
            return
        commentlist = self.othercomments
        linestart = "#"
        autocomments = False
        if origin in ["programmer", "developer", "source code"]:
            autocomments = True
            commentlist = self.automaticcomments
            linestart = "#."
        newcomments = [
            "".join((linestart, " " if line else "", line, self.newline))
            for line in text.split(self.newline)
        ]
        if position == "append":
            newcomments = commentlist + newcomments
        elif position == "prepend":
            newcomments = newcomments + commentlist

        if autocomments:
            self.automaticcomments = newcomments
        else:
            self.othercomments = newcomments

    def removenotes(self, origin=None):
        """Remove all the translator's notes (other comments)"""
        self.othercomments = []

    def __deepcopy__(self, memo={}):
        # Make an instance to serve as the copy
        new_unit = self.__class__()
        # We'll be testing membership frequently, so make a set from
        # self.__shallow__
        shallow = set(self.__shallow__)
        # Make deep copies of all members which are not in shallow
        for key, value in self.__dict__.items():
            if key not in shallow:
                setattr(new_unit, key, copy.deepcopy(value))
        # Make shallow copies of all members which are in shallow
        for key in set(shallow):
            setattr(new_unit, key, getattr(self, key))
        # Mark memo with ourself, so that we won't get deep copied
        # again
        memo[id(self)] = self
        # Return our copied unit
        return new_unit

    def copy(self):
        return copy.deepcopy(self)

    def _msgidlen(self):
        if self.hasplural():
            return len(unquotefrompo(self.msgid)) + len(
                unquotefrompo(self.msgid_plural)
            )
        return len(unquotefrompo(self.msgid))

    def _msgstrlen(self):
        if isinstance(self.msgstr, dict):
            combinedstr = self.newline.join(
                filter(None, [unquotefrompo(msgstr) for msgstr in self.msgstr.values()])
            )
            return len(combinedstr)
        return len(unquotefrompo(self.msgstr))

    def merge(self, otherpo, overwrite=False, comments=True, authoritative=False):
        """Merges the otherpo (with the same msgid) into this one.

        Overwrite non-blank self.msgstr only if overwrite is True
        merge comments only if comments is True
        """

        def mergelists(list1, list2, split=False):
            # Determine the newline style of list1
            lineend = ""
            if list1 and list1[0]:
                for candidate in ["\n", "\r", "\n\r"]:
                    if list1[0].endswith(candidate):
                        lineend = candidate
                if not lineend:
                    lineend = ""
            else:
                lineend = "\n"

            # Split if directed to do so:
            if split:
                splitlist1 = []
                splitlist2 = []
                prefix = "#"
                for item in list1:
                    splitlist1.extend(item.split()[1:])
                    prefix = item.split()[0]
                for item in list2:
                    splitlist2.extend(item.split()[1:])
                    prefix = item.split()[0]
                list1.extend(
                    [
                        f"{prefix} {item}{lineend}"
                        for item in splitlist2
                        if item not in splitlist1
                    ]
                )
            else:
                # Normal merge, but conform to list1 newline style
                if list1 != list2:
                    for item in list2:
                        if lineend:
                            item = item.rstrip() + lineend
                        # avoid duplicate comment lines (this might cause some problems)
                        if item not in list1 or len(item) < 5:
                            list1.append(item)

        if not isinstance(otherpo, pounit):
            super().merge(otherpo, overwrite, comments)
            return
        if comments:
            mergelists(self.othercomments, otherpo.othercomments)
            mergelists(self.typecomments, otherpo.typecomments)
            if not authoritative:
                # We don't bring across otherpo.automaticcomments as we
                # consider ourself to be the the authority.  Same applies
                # to otherpo.msgidcomments
                mergelists(self.automaticcomments, otherpo.automaticcomments)
                mergelists(self.msgidcomments, otherpo.msgidcomments)
                mergelists(self.sourcecomments, otherpo.sourcecomments, split=True)
        if not self.istranslated() or overwrite:
            # Remove kde-style comments from the translation (if any).
            if self._extract_msgidcomments(otherpo.target):
                otherpo.target = otherpo.target.replace(
                    "_: " + otherpo._extract_msgidcomments() + self.newline, ""
                )
            self.target = otherpo.target
            if (
                self.source != otherpo.source
                or self.getcontext() != otherpo.getcontext()
            ):
                self.markfuzzy()
            else:
                self.markfuzzy(otherpo.isfuzzy())
        elif not otherpo.istranslated():
            if self.source != otherpo.source:
                self.markfuzzy()
        else:
            if self.target != otherpo.target:
                self.markfuzzy()

    def isheader(self):
        # return (self._msgidlen() == 0) and (self._msgstrlen() > 0) and (len(self.msgidcomments) == 0)
        # rewritten here for performance:
        return (
            is_null(self.msgid)
            and not is_null(self.msgstr)
            and self.msgidcomments == []
            and is_null(self.msgctxt)
        )

    def isblank(self):
        if self.isheader() or self.msgidcomments:
            return False
        if (
            (self._msgidlen() == 0)
            and (self._msgstrlen() == 0)
            and (is_null(self.msgctxt))
        ):
            return True
        return False
        # TODO: remove:
        # Before, the equivalent of the following was the final return statement:
        # return len(self.source.strip()) == 0

    def _extracttypecomment(self):
        for tc in self.typecomments:
            for flag in tc.split(","):
                value = flag.strip()
                if not value or value == "#":
                    continue
                yield value

    def hastypecomment(self, typecomment, parsed=None):
        """Check whether the given type comment is present"""
        if not self.typecomments:
            return False
        if not parsed:
            parsed = self._extracttypecomment()
        return typecomment in parsed

    def hasmarkedcomment(self, commentmarker):
        """Check whether the given comment marker is present.

        These should appear as::

                # (commentmarker) ...
        """
        commentmarker = "(%s)" % commentmarker
        for comment in self.othercomments:
            if comment.replace("#", "", 1).strip().startswith(commentmarker):
                return True
        return False

    def settypecomment(self, typecomment, present=True):
        """Alters whether a given typecomment is present"""
        typecomments = list(self._extracttypecomment())
        if self.hastypecomment(typecomment, typecomments) != present:
            if present:
                typecomments.append(typecomment)
            else:
                typecomments.remove(typecomment)
            if typecomments:
                typecomments.sort()
                comments_str = ", ".join(typecomments)
                self.typecomments = [f"#, {comments_str}{self.newline}"]
            else:
                self.typecomments = []

    def isfuzzy(self):
        return self.hastypecomment("fuzzy")

    def markfuzzy(self, present=True):
        if present:
            self.set_state_n(self.STATE[self.S_FUZZY][0])
        elif self.hasplural() and not self._msgstrlen() or is_null(self.msgstr):
            self.set_state_n(self.STATE[self.S_UNTRANSLATED][0])
        else:
            self.set_state_n(self.STATE[self.S_TRANSLATED][0])
        self._domarkfuzzy(present)

    def _domarkfuzzy(self, present=True):
        self.settypecomment("fuzzy", present)

    def infer_state(self):
        if self.obsolete:
            self.makeobsolete()
        else:
            self.markfuzzy(self.hastypecomment("fuzzy"))

    def isobsolete(self):
        return self.obsolete

    def makeobsolete(self):
        """Makes this unit obsolete"""
        super().makeobsolete()
        self.obsolete = True
        self.sourcecomments = []
        self.automaticcomments = []

    def resurrect(self):
        """Makes an obsolete unit normal"""
        super().resurrect()
        self.obsolete = False

    def hasplural(self):
        """returns whether this pounit contains plural strings..."""
        return len(self.msgid_plural) > 0

    def _getmsgpartstr(self, partname, partlines, partcomments=""):
        if isinstance(partlines, dict):
            partkeys = sorted(partlines.keys())
            return "".join(
                self._getmsgpartstr(
                    "%s[%d]" % (partname, partkey), partlines[partkey], partcomments
                )
                for partkey in partkeys
            )
        partstr = [partname, " "]
        partstartline = 0
        if partlines and not partcomments:
            partstr.append(partlines[0])
            partstartline = 1
        elif partcomments:
            if partlines and not unquotefrompo(partlines[:1]):
                # if there is a blank leader line, it must come before the comment
                partstr.extend((partlines[0], self.newline))
                # but if the whole string is blank, leave it in
                if len(partlines) > 1:
                    partstartline += 1
            else:
                # All partcomments should start on a newline
                partstr.append('""\n')
            # combine comments into one if more than one
            if len(partcomments) > 1:
                combinedcomment = []
                for comment in partcomments:
                    comment = unquotefrompo([comment])
                    if comment.startswith("_:"):
                        comment = comment[len("_:") :]
                    if comment.endswith("\\n"):
                        comment = comment[: -len("\\n")]
                    # Before we used to strip. Necessary in some cases?
                    combinedcomment.append(comment)
                partcomments = self.quote("_:%s" % "".join(combinedcomment))
                # Strip heading empty line for multiline string, it was already added above
                if partcomments[0] == '""':
                    partcomments = partcomments[1:]
            # comments first, no blank leader line needed
            partstr.append(quote.rstripeol(self.newline.join(partcomments)))
        else:
            partstr.append('""')
        partstr.append(self.newline)
        # add the rest
        previous = None
        for partline in partlines[partstartline:]:
            # Avoid duplicate empty lines
            if previous == '""' and partline == '""':
                continue
            previous = partline
            partstr.extend((partline, self.newline))
        return "".join(partstr)

    def __str__(self):
        """Convert to a string."""
        return self._getoutput()

    def _getoutput(self):
        """return this po element as a string"""

        def add_prev_msgid_lines(lines, prefix, header, var):
            if var:
                lines.append(f"{prefix} {header} {var[0]}\n")
                lines.extend(f"{prefix} {line}\n" for line in var[1:])

        def add_prev_msgid_info(lines, prefix):
            add_prev_msgid_lines(lines, prefix, "msgctxt", self.prev_msgctxt)
            add_prev_msgid_lines(lines, prefix, "msgid", self.prev_msgid)
            add_prev_msgid_lines(lines, prefix, "msgid_plural", self.prev_msgid_plural)

        lines = []
        lines.extend(self.othercomments)
        if self.isobsolete():
            lines.extend(self.typecomments)
            obsoletelines = []
            add_prev_msgid_info(obsoletelines, prefix="#~|")
            if self.msgctxt:
                obsoletelines.append(self._getmsgpartstr("#~ msgctxt", self.msgctxt))
            obsoletelines.append(
                self._getmsgpartstr("#~ msgid", self.msgid, self.msgidcomments)
            )
            if self.msgid_plural or self.msgid_pluralcomments:
                obsoletelines.append(
                    self._getmsgpartstr(
                        "#~ msgid_plural", self.msgid_plural, self.msgid_pluralcomments
                    )
                )
            obsoletelines.append(self._getmsgpartstr("#~ msgstr", self.msgstr))
            for index, obsoleteline in enumerate(obsoletelines):
                # We need to account for a multiline msgid or msgstr here
                obsoletelines[index] = obsoleteline.replace('\n"', '\n#~ "')
            lines.extend(obsoletelines)
            return "".join(lines)
        # if there's no msgid don't do msgid and string, unless we're the
        # header this will also discard any comments other than plain
        # othercomments...
        if is_null(self.msgid) and not (
            self.isheader() or self.getcontext() or self.sourcecomments
        ):
            return "".join(lines)
        lines.extend(self.automaticcomments)
        lines.extend(self.sourcecomments)
        lines.extend(self.typecomments)
        add_prev_msgid_info(lines, prefix="#|")
        if self.msgctxt:
            lines.append(self._getmsgpartstr("msgctxt", self.msgctxt))
        lines.append(self._getmsgpartstr("msgid", self.msgid, self.msgidcomments))
        if self.msgid_plural or self.msgid_pluralcomments:
            lines.append(
                self._getmsgpartstr(
                    "msgid_plural", self.msgid_plural, self.msgid_pluralcomments
                )
            )
        lines.append(self._getmsgpartstr("msgstr", self.msgstr))
        return "".join(lines)

    def getlocations(self):
        """Get a list of locations from sourcecomments in the PO unit

        rtype: List
        return: A list of the locations with '#: ' stripped

        """
        locations = []
        for sourcecomment in self.sourcecomments:
            locations += quote.rstripeol(sourcecomment)[3:].split()
        for i, loc in enumerate(locations):
            locations[i] = pocommon.unquote_plus(loc)
        return locations

    def addlocation(self, location):
        """Add a location to sourcecomments in the PO unit

        :param location: Text location e.g. 'file.c:23' does not include #:
        :type location: String

        """
        location = pocommon.quote_plus(location)
        self.sourcecomments.append(f"#: {location}{self.newline}")

    def _extract_msgidcomments(self, text=None):
        """Extract KDE style msgid comments from the unit.

        :rtype: String
        :return: Returns the extracted msgidcomments found in this
                 unit's msgid.
        """

        if not text:
            text = unquotefrompo(self.msgidcomments)
        return text.split(self.newline)[0].replace("_: ", "", 1)

    def setmsgidcomment(self, msgidcomment):
        if msgidcomment:
            self.msgidcomments = ['"_: %s\\n"' % msgidcomment]
        else:
            self.msgidcomments = []

    msgidcomment = property(_extract_msgidcomments, setmsgidcomment)

    def getcontext(self):
        """Get the message context."""
        return unquotefrompo(self.msgctxt) + self._extract_msgidcomments()

    def setcontext(self, context):
        self.msgctxt = self.quote(context)

    def getid(self):
        """Returns a unique identifier for this unit."""
        context = self.getcontext()
        # Gettext does not consider the plural to determine duplicates, only
        # the msgid. For generation of .mo files, we might want to use this
        # code to generate the entry for the hash table, but for now, it is
        # commented out for conformance to gettext.
        #        id = '\0'.join(self.source.strings)
        id = self.source
        if self.msgidcomments:
            id = f"_: {context}\n{id}"
        elif context:
            id = f"{context}\04{id}"
        return id


class pofile(pocommon.pofile):
    """A .po file containing various units"""

    UnitClass = pounit

    def __init__(self, inputfile=None, width=None, **kwargs):
        wrapargs = {}
        if width is not None:
            wrapargs = {"width": width}
        self.wrapper = PoWrapper(**wrapargs)
        self.newline = "\n"
        super().__init__(inputfile, **kwargs)

    def create_unit(self):
        return self.UnitClass(wrapper=self.wrapper)

    def parse(self, input):
        """Parses the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if not isinstance(input, bytes):
            input = input.read()
        lines, self.newline = splitlines(input)
        # clear units to get rid of automatically generated headers before parsing
        self.units = []
        poparser.parse_units(poparser.ParseState(iter(lines), self.create_unit), self)

    def removeduplicates(self, duplicatestyle="merge"):
        """Make sure each msgid is unique ; merge comments etc from
        duplicates into original
        """
        # TODO: can we handle consecutive calls to removeduplicates()? What
        # about files already containing msgctxt? - test
        id_dict = {}
        uniqueunits = []
        # TODO: this is using a list as the pos aren't hashable, but this is slow.
        # probably not used frequently enough to worry about it, though.
        markedpos = []

        def addcomment(thepo):
            thepo.msgidcomments.append('"_: %s\\n"' % " ".join(thepo.getlocations()))
            markedpos.append(thepo)

        for thepo in self.units:
            id = thepo.getid()
            if thepo.isheader() and not thepo.getlocations():
                # header msgids shouldn't be merged...
                uniqueunits.append(thepo)
            elif id in id_dict:
                if duplicatestyle == "merge":
                    if id:
                        id_dict[id].merge(thepo)
                    else:
                        addcomment(thepo)
                        uniqueunits.append(thepo)
                elif duplicatestyle == "msgctxt":
                    origpo = id_dict[id]
                    if origpo not in markedpos and id:
                        # if it doesn't have an id, we already added msgctxt
                        origpo.msgctxt.append(
                            '"%s"' % escapeforpo(" ".join(origpo.getlocations()))
                        )
                        markedpos.append(thepo)
                    thepo.msgctxt.append(
                        '"%s"' % escapeforpo(" ".join(thepo.getlocations()))
                    )
                    if not thepo.msgctxt == id_dict[id].msgctxt:
                        uniqueunits.append(thepo)
                    else:
                        logger.warning(
                            "Duplicate unit found with msgctx of '%s' and source '%s'",
                            thepo.msgctxt,
                            thepo.source,
                        )
            else:
                if not id:
                    if duplicatestyle == "merge":
                        addcomment(thepo)
                    else:
                        thepo.msgctxt.append(
                            '"%s"' % escapeforpo(" ".join(thepo.getlocations()))
                        )
                id_dict[id] = thepo
                uniqueunits.append(thepo)
        self.units = uniqueunits

    def serialize(self, out):
        """Write to file"""
        at_start = True
        try:
            for unit in self.units:
                if not at_start:
                    out.write(self.newline.encode())
                else:
                    at_start = False
                out.write(unit._getoutput().encode(self.encoding))
        except UnicodeEncodeError:
            if self.encoding == "utf-8":
                raise
            self.updateheader(add=True, Content_Type="text/plain; charset=UTF-8")
            self.encoding = "utf-8"
            out.seek(0)
            self.serialize(out)

    def unit_iter(self):
        for unit in self.units:
            if not (unit.isheader() or unit.isobsolete()):
                yield unit

    def addunit(self, unit):
        unit.wrapper = self.wrapper
        super().addunit(unit)
