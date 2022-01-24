#
# Copyright 2007,2009 Zuza Software Foundation
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

"""Class that manages .ini files for translation

.. note::: A simple summary of what is permissible follows.

# a comment
; a comment

[Section]
a = a string
b : a string
"""

import re
from io import StringIO

from translate.storage import base


try:
    from iniparse import INIConfig
except ImportError:
    raise ImportError("Missing iniparse library.")


dialects = {}


def register_dialect(dialect):
    """Decorator that registers the dialect."""
    dialects[dialect.name] = dialect
    return dialect


class Dialect:
    """Base class for differentiating dialect options and functions"""

    name = None


@register_dialect
class DialectDefault(Dialect):
    name = "default"

    @staticmethod
    def unescape(text):
        return text

    @staticmethod
    def escape(text):
        return text


@register_dialect
class DialectInno(DialectDefault):
    name = "inno"

    def unescape(self, text):
        return text.replace("%n", "\n").replace("%t", "\t")

    def escape(self, text):
        return text.replace("\t", "%t").replace("\n", "%n")


class iniunit(base.TranslationUnit):
    """A INI file entry"""

    def __init__(self, source=None, **kwargs):
        self.location = ""
        if source:
            self.source = source
        super().__init__(source)

    def addlocation(self, location):
        self.location = location

    def getlocations(self):
        return [self.location]


class inifile(base.TranslationStore):
    """An INI file"""

    UnitClass = iniunit

    def __init__(self, inputfile=None, dialect="default", **kwargs):
        """construct an INI file, optionally reading in from inputfile."""
        self._dialect = dialects.get(
            dialect, DialectDefault
        )()  # fail correctly/use getattr/
        super().__init__(**kwargs)
        self.filename = ""
        self._inifile = None
        if inputfile is not None:
            self.parse(inputfile)

    def serialize(self, out):
        _outinifile = self._inifile
        for unit in self.units:
            for location in unit.getlocations():
                match = re.match("\\[(?P<section>.+)\\](?P<entry>.+)", location)
                value = self._dialect.escape(unit.target)
                _outinifile[match.groupdict()["section"]][
                    match.groupdict()["entry"]
                ] = value
        if _outinifile:
            out.write(str(_outinifile).encode("utf-8"))

    def parse(self, input):
        """Parse the given file or file source string."""
        if hasattr(input, "name"):
            self.filename = input.name
        elif not getattr(self, "filename", ""):
            self.filename = ""
        if hasattr(input, "read"):
            inisrc = input.read()
            input.close()
            input = inisrc

        if isinstance(input, bytes):
            input = StringIO(input.decode("utf-8"))
            self._inifile = INIConfig(input, optionxformvalue=None)
        else:
            self._inifile = INIConfig(open(input), optionxformvalue=None)

        for section in self._inifile:
            for entry in self._inifile[section]:
                source = self._dialect.unescape(self._inifile[section][entry])
                newunit = self.addsourceunit(source)
                newunit.addlocation(f"[{section}]{entry}")
