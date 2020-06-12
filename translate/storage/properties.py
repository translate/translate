#
# Copyright 2004-2014 Zuza Software Foundation
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

r"""Classes that hold units of .properties, and similar, files that are used in
translating Java, Mozilla, MacOS and other software.

The :class:`propfile` class is a monolingual class with :class:`propunit`
providing unit level access.

The .properties store has become a general key value pair class with
:class:`Dialect` providing the ability to change the behaviour of the
parsing and handling of the various dialects.

Currently we support:

- Java .properties
- Mozilla .properties
- Adobe Flex files
- MacOS X .strings files
- Skype .lang files

The following provides references and descriptions of the various
dialects supported:

Java
    Java .properties are supported completely except for the ability to drop
    pairs that are not translated.

    The following `.properties file description
    <http://docs.oracle.com/javase/7/docs/api/java/util/Properties.html#load(java.io.Reader)>`_
    gives a good references to the .properties specification.

    Properties file may also hold Java `MessageFormat
    <http://docs.oracle.com/javase/7/docs/api/java/text/MessageFormat.html>`_
    messages.  No special handling is provided in this storage class for
    MessageFormat, but this may be implemented in future.

    All delimiter types, comments, line continuations and spaces handling in
    delimeters are supported.

Mozilla
    Mozilla files use '=' as a delimiter, are UTF-8 encoded and thus don't
    need \\u escaping.  Any \\U values will be converted to correct Unicode
    characters.

Strings
    Mac OS X strings files are implemented using
    `these <https://developer.apple.com/library/mac/#documentation/MacOSX/Conceptual/BPInternational/Articles/StringsFiles.html>`_
    `two <https://developer.apple.com/library/mac/#documentation/Cocoa/Conceptual/LoadingResources/Strings/Strings.html>`_
    articles as references.

Flex
    Adobe Flex files seem to be normal .properties files but in UTF-8 just like
    Mozilla files. This
    `page <http://livedocs.adobe.com/flex/3/html/help.html?content=l10n_3.html>`_
    provides the information used to implement the dialect.

Skype
    Skype .lang files seem to be UTF-16 encoded .properties files.

A simple summary of what is permissible follows.

Comments supported:

.. code-block:: properties

   # a comment
   // a comment (only at the beginning of a line)

   # The following are # escaped to render in docs
   # ! is standard but not widely supported
   #! a comment
   # /* is non-standard but used on some implementations
   #/* a comment (not across multiple lines) */


Name and Value pairs:

.. code-block:: properties

   # Delimiters
   key = value
   key : value
   # Whitespace delimiter
   # key[sp]value

   # Space in key and around value
   \ key\ = \ value

   # Note that the b and c are escaped for reST rendering
   b = a string with escape sequences \\t \\n \\r \\\\ \\" \\' \\ (space) \u0123
   c = a string with a continuation line \\
       continuation line

   # Special cases
   # key with no value
   //key (escaped; doesn't render in docs)
   # value no key (extractable in prop2po but not mergeable in po2prop)
   =value

   # .strings specific
   "key" = "value";

"""

import collections
import re
from codecs import iterencode

from translate.lang import data
from translate.misc import quote
from translate.misc.multistring import multistring
from translate.storage import base


labelsuffixes = (".label", ".title")
"""Label suffixes: entries with this suffix are able to be comibed with accesskeys
found in in entries ending with :attr:`.accesskeysuffixes`"""
accesskeysuffixes = (".accesskey", ".accessKey", ".akey")
"""Accesskey Suffixes: entries with this suffix may be combined with labels
ending in :attr:`.labelsuffixes` into accelerator notation"""


# the rstripeols convert dos <-> unix nicely as well
# output will be appropriate for the platform

eol = "\n"


def is_line_continuation(line):
    """Determine whether *line* has a line continuation marker.

    .properties files can be terminated with a backslash (\\) indicating
    that the 'value' continues on the next line.  Continuation is only
    valid if there are an odd number of backslashses (an even number
    would result in a set of N/2 slashes not an escape)

    :param line: A properties line
    :type line: str
    :return: Does *line* end with a line continuation
    :rtype: Boolean
    """
    pos = -1
    count = 0
    if len(line) == 0:
        return False
    # Count the slashes from the end of the line. Ensure we don't
    # go into infinite loop.
    while len(line) >= -pos and line[pos:][0] == "\\":
        pos -= 1
        count += 1
    return (count % 2) == 1  # Odd is a line continuation, even is not


def is_comment_one_line(line):
    """Determine whether a *line* is a one-line comment.

    :param line: A properties line
    :type line: unicode
    :return: True if line is a one-line comment
    :rtype: bool
    """
    stripped = line.strip()
    line_starters = ('#', '!', '//', ';')
    for starter in line_starters:
        if stripped.startswith(starter):
            return True
    if stripped.startswith('/*') and stripped.endswith('*/'):
        return True
    return False


def is_comment_start(line):
    """Determine whether a *line* starts a new multi-line comment.

    :param line: A properties line
    :type line: unicode
    :return: True if line starts a new multi-line comment
    :rtype: bool
    """
    stripped = line.strip()
    return stripped.startswith('/*') and not stripped.endswith('*/')


def is_comment_end(line):
    """Determine whether a *line* ends a new multi-line comment.

    :param line: A properties line
    :type line: unicode
    :return: True if line ends a new multi-line comment
    :rtype: bool
    """
    stripped = line.strip()
    return not stripped.startswith('/*') and stripped.endswith('*/')


def _key_strip(key):
    """Cleanup whitespace found around a key

    :param key: A properties key
    :type key: str
    :return: Key without any unneeded whitespace
    :rtype: str
    """
    newkey = key.rstrip()
    # If string now ends in \ we put back the whitespace that was escaped
    if newkey[-1:] == "\\":
        newkey += key[len(newkey):len(newkey)+1]
    return newkey.lstrip()


dialects = {}
default_dialect = "java"


def register_dialect(dialect):
    """Decorator that registers the dialect."""
    dialects[dialect.name] = dialect
    return dialect


def get_dialect(dialect=default_dialect):
    return dialects.get(dialect)


class Dialect:
    """Settings for the various behaviours in key=value files."""

    name = None
    default_encoding = 'iso-8859-1'
    delimiters = None
    pair_terminator = ""
    key_wrap_char = ""
    value_wrap_char = ""
    drop_comments = []

    @classmethod
    def encode(cls, string, encoding=None):
        """Encode the string"""
        # FIXME: dialects are a bad idea, not possible for subclasses
        # to override key methods
        if encoding not in ("utf-8", "utf-16"):
            return quote.javapropertiesencode(string or "")
        return quote.java_utf8_properties_encode(string or "")

    @staticmethod
    def decode(string):
        return quote.propertiesdecode(string)

    @classmethod
    def find_delimiter(cls, line):
        """Find the type and position of the delimiter in a property line.

        Property files can be delimited by "=", ":" or whitespace (space for now).
        We find the position of each delimiter, then find the one that appears
        first.

        :param line: A properties line
        :type line: str
        :param delimiters: valid delimiters
        :type delimiters: list
        :return: delimiter character and offset within *line*
        :rtype: Tuple (delimiter char, Offset Integer)
        """
        delimiter_dict = {}
        for delimiter in cls.delimiters:
            delimiter_dict[delimiter] = -1
        delimiters = delimiter_dict
        # Find the position of each delimiter type
        for delimiter, pos in delimiters.items():
            start_pos = len(line) - len(line.lstrip())  # Skip initial whitespace
            if cls.key_wrap_char != '' and line[start_pos] == cls.key_wrap_char:
                # Skip the key if it is delimited by some char
                start_pos += 1
                while (line[start_pos] != cls.key_wrap_char or line[start_pos-1] == "\\"):
                    start_pos += 1
            pos = line.find(delimiter, start_pos)
            while pos != -1:
                if delimiters[delimiter] == -1 and line[pos-1] != "\\":
                    delimiters[delimiter] = pos
                    break
                pos = line.find(delimiter, pos + 1)
        # Find the first delimiter
        mindelimiter = None
        minpos = -1
        for delimiter, pos in delimiters.items():
            if pos == -1 or delimiter == " ":
                continue
            if minpos == -1 or pos < minpos:
                minpos = pos
                mindelimiter = delimiter
        if mindelimiter is None and delimiters.get(" ", -1) != -1:
            # Use space delimiter if we found nothing else
            return (" ", delimiters[" "])
        if (mindelimiter is not None and
            " " in delimiters and
            delimiters[" "] < delimiters[mindelimiter]):
            # If space delimiter occurs earlier than ":" or "=" then it is the
            # delimiter only if there are non-whitespace characters between it and
            # the other detected delimiter.
            if len(line[delimiters[" "]:delimiters[mindelimiter]].strip()) > 0:
                return (" ", delimiters[" "])
        return (mindelimiter, minpos)

    @classmethod
    def key_strip(cls, key):
        """Strip unneeded characters from the key"""
        return _key_strip(key)

    @classmethod
    def value_strip(cls, value):
        """Strip unneeded characters from the value"""
        return value.lstrip()

    @classmethod
    def is_line_continuation(cls, line):
        return is_line_continuation(line)

    @classmethod
    def strip_line_continuation(cls, value):
        return value[:-1]

    @classmethod
    def get_key_cldr_name(cls, key):
        return (key, "other")

    @classmethod
    def get_cldr_names_order(cls):
        return ["other"]


@register_dialect
class DialectJava(Dialect):
    name = "java"
    default_encoding = "iso-8859-1"
    delimiters = ["=", ":", " "]


@register_dialect
class DialectJavaUtf8(DialectJava):
    name = "java-utf8"
    default_encoding = "utf-8"
    delimiters = ["=", ":", " "]

    @classmethod
    def encode(cls, string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectJavaUtf16(DialectJava):
    name = "java-utf16"
    default_encoding = "utf-16"
    delimiters = ["=", ":", " "]

    @classmethod
    def encode(cls, string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectFlex(DialectJava):
    name = "flex"
    default_encoding = "utf-8"


@register_dialect
class DialectMozilla(DialectJavaUtf8):
    name = "mozilla"
    delimiters = ["="]

    @classmethod
    def encode(cls, string, encoding=None):
        """Encode the string"""
        string = quote.java_utf8_properties_encode(string or "")
        string = quote.mozillaescapemarginspaces(string or "")
        return string


@register_dialect
class DialectGaia(DialectMozilla):
    name = "gaia"
    delimiters = ["="]


@register_dialect
class DialectGwt(DialectJava):
    plural_regex = re.compile(r'([^\[\]]*)(?:\[(.*)\])?')
    name = "gwt"
    default_encoding = "utf-8"
    delimiters = ["="]

    gwt_plural_categories = [
        ('', "other"),
        ('none', "zero"),
        ('one', 'one'),
        ('two', 'two'),
        ('few', 'few'),
        ('many', 'many'),
    ]

    gwt2cldr = collections.OrderedDict(gwt_plural_categories)
    cldr2gwt = collections.OrderedDict([(b, a) for a, b in gwt_plural_categories])

    @classmethod
    def get_key_cldr_name(cls, key):
        match = cls.plural_regex.match(key)
        key = match.group(1)
        variant = match.group(2)
        if not variant:
            variant = ""

        variant = cls.gwt2cldr.get(variant)
        # Some sanity checks
        if not variant:
            raise Exception("Key \"%s\" variant \"%s\" is invalid" % (key, variant))
        return (key, variant)

    @classmethod
    def get_cldr_names_order(cls):
        return [y for x, y in cls.gwt_plural_categories]

    @classmethod
    def get_key(cls, key, variant):
        variant = cls.cldr2gwt.get(variant)

        # Some sanity checks
        if not variant:
            raise Exception("Key \"%s\" variant \"%s\" is invalid" % (key, variant))
        return "%s[%s]" % (key, variant)

    @classmethod
    def encode(cls, string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectSkype(Dialect):
    name = "skype"
    default_encoding = "utf-16"
    delimiters = ["="]

    @classmethod
    def encode(cls, string, encoding=None):
        return quote.java_utf8_properties_encode(string or "")


@register_dialect
class DialectStrings(Dialect):
    name = "strings"
    default_encoding = "utf-16"
    delimiters = ["="]
    pair_terminator = ";"
    key_wrap_char = '"'
    value_wrap_char = '"'
    out_ending = ';'
    out_delimiter_wrappers = ' '
    drop_comments = ["/* No comment provided by engineer. */"]

    @classmethod
    def key_strip(cls, key):
        """Strip unneeded characters from the key"""
        newkey = key.rstrip().rstrip('"')
        # If string now ends in \ we put back the char that was escaped
        if newkey[-1:] == "\\":
            newkey += key[len(newkey):len(newkey)+1]
        ret = newkey.lstrip().lstrip('"')
        return ret.replace('\\"', '"')

    @classmethod
    def value_strip(cls, value):
        """Strip unneeded characters from the value"""
        newvalue = value.rstrip().rstrip(';').rstrip('"')
        # If string now ends in \ we put back the char that was escaped
        if newvalue[-1:] == "\\":
            newvalue += value[len(newvalue):len(newvalue)+1]
        ret = newvalue.lstrip().lstrip('"')
        return ret.replace('\\"', '"')

    @classmethod
    def encode(cls, string, encoding=None):
        return string.replace("\n", r"\n").replace("\t", r"\t")

    @classmethod
    def is_line_continuation(self, line):
        l = line.rstrip()
        if l and l[-1] == ';':
            return False
        return True

    @classmethod
    def strip_line_continuation(cls, value):
        return value


@register_dialect
class DialectStringsUtf8(DialectStrings):
    name = "strings-utf8"
    default_encoding = "utf-8"


class proppluralunit(base.TranslationUnit):
    KEY = 'other'

    def __init__(self, source="", personality="java"):
        """Construct a blank propunit."""
        self.personality = get_dialect(personality)
        super(proppluralunit, self).__init__(source)
        self.units = collections.OrderedDict()
        self.name = ""

    @staticmethod
    def _get_language_mapping(lang):
        if lang:
            locale = lang.replace('_', '-').split('-')[0]
            cldr_mapping = data.plural_tags.get(locale, data.plural_tags['en'])
            if cldr_mapping:
                return cldr_mapping
        return None

    def _get_target_mapping(self):
        cldr_mapping = proppluralunit._get_language_mapping(self._store.targetlanguage)
        if cldr_mapping:
            return cldr_mapping
        return self.units.keys()

    def _get_source_mapping(self):
        cldr_mapping = proppluralunit._get_language_mapping(self._store.sourcelanguage)
        if cldr_mapping:
            return cldr_mapping
        return self.units.keys()

    def _get_units(self, mapping):
        ret = []
        if len(self.units) > 1:
            for name in mapping:
                if name not in self.units:
                    unit = propunit("", self.personality.name)
                    unit.name = self.personality.get_key(self.name, name)
                    self.units[name] = unit
                ret.append(self.units[name])
        else:
            ret.append(self.units[proppluralunit.KEY])
        return ret

    def _get_strings(self, strings, mapping):
        ret = []
        if len(strings) > 1:
            for i, name in enumerate(mapping):
                if i < len(strings):
                    ret.append(strings[i])
                else:
                    ret.append("")
        else:
            ret.append(strings[0])
        return ret

    def _get_source_unit(self):
        self._get_units(self._get_source_mapping())  # Generate missing forms
        return self.units[proppluralunit.KEY]

    def _get_ordered_units(self):
        # Used for str (GWT order)
        mapping = self._get_target_mapping()
        names = []
        for name in self.personality.get_cldr_names_order():
            if name in mapping:
                names.append(name)
        return self._get_units(names)

    def hasplural(self, key=None):
        if key is None:
            return len(self.units) > 1
        return key in self.units

    def settarget(self, text):
        mapping = None
        if isinstance(text, multistring):
            strings = text.strings
        elif isinstance(text, list):
            strings = text
        elif isinstance(text, dict):
            mapping, strings = map(list, zip(*text.items()))
        else:
            strings = [text]
        if mapping is None:
            mapping = self._get_target_mapping()

        strings = self._get_strings(strings, mapping)
        units = self._get_units(mapping)
        if len(strings) != len(units):
            raise Exception('Not same plural counts between "%s" and "%s"' % (str(strings), str(units)))

        for a, b in zip(strings, units):
            b.target = a

    def gettarget(self):
        ll = [x.target for x in self._get_units(self._get_target_mapping())]
        if len(ll) > 1:
            return multistring(ll)
        return ll[0]

    target = property(gettarget, settarget)

    def getsource(self):
        ll = [x.source for x in self._get_units(self._get_source_mapping())]
        if len(ll) > 1:
            return multistring(ll)
        else:
            return ll[0]

    def setsource(self, text):
        mapping = None
        if isinstance(text, multistring):
            strings = text.strings
        elif isinstance(text, list):
            strings = text
        elif isinstance(text, dict):
            mapping, strings = tuple(map(list, zip(*text.items())))
        else:
            strings = [text]
        if mapping is None:
            mapping = self._get_source_mapping()

        strings = self._get_strings(strings, mapping)
        units = self._get_units(mapping)
        if len(strings) != len(units):
            raise Exception('Not same plural counts between "%s" and "%s"' % (str(strings), str(units)))

        for a, b in zip(strings, units):
            b.source = a

    source = property(getsource, setsource)

    def getvalue(self):
        value = self._get_source_unit().value
        return multistring(value) if value is not None else None

    def setvalue(self, value):
        if isinstance(value, multistring):
            strings = value.strings
        elif isinstance(value, list):
            strings = value
        else:
            strings = [value]
        self._get_source_unit().value = strings[0]

    value = property(getvalue, setvalue)

    def getcomments(self):
        return self._get_source_unit().comments

    def setcomments(self, comments):
        self._get_source_unit().comments = comments

    comments = property(getcomments, setcomments)

    def getdelimiter(self):
        return self._get_source_unit().delimiter

    def setdelimiter(self, delimiter):
        self._get_source_unit().delimiter = delimiter

    delimiter = property(getdelimiter, setdelimiter)

    def getnotes(self, origin=None):
        return self._get_source_unit().getnotes(origin)

    def getlocations(self):
        return self._get_source_unit().getlocations()

    def add_unit(self, unit, variant):
        self.units[variant] = unit

    def isblank(self):
        """returns whether this is a blank element, containing only
        comments.
        """
        return not (self.name or self.value)

    def istranslatable(self):
        return bool(self.name)

    def getid(self):
        return self.name

    def setid(self, value):
        self.name = value

    def __str__(self):
        """Convert to a string. Double check that unicode is handled
        somehow here.
        """
        return self.getoutput()

    def getoutput(self):
        ret = ""
        for x in self._get_ordered_units():
            ret += x.getoutput()
        return ret

    @property
    def encoding(self):
        if self._store:
            return self._store.encoding
        return self.personality.default_encoding


@register_dialect
class DialectJoomla(Dialect):
    name = "joomla"
    default_encoding = "utf-8"
    delimiters = ["="]
    out_delimiter_wrappers = ''

    @classmethod
    def value_strip(cls, value):
        """Strip unneeded characters from the value"""
        newvalue = value.strip()
        if not newvalue:
            return newvalue
        if newvalue[0] == '"' and newvalue[-1] == '"':
            newvalue = newvalue[1:-1]
        return newvalue.replace('"_QQ_"', '"')

    @classmethod
    def decode(cls, string):
        return cls.value_strip(string)

    @classmethod
    def encode(cls, string, encoding=None):
        """Encode the string"""
        if not string:
            return string
        return '"%s"' % string.replace("\n", r"\n").replace("\t", r"\t").replace('"', '"_QQ_"')


class propunit(base.TranslationUnit):
    """An element of a properties file i.e. a name and value, and any comments
    associated.
    """

    def __init__(self, source="", personality="java"):
        """Construct a blank propunit."""
        self.personality = get_dialect(personality)
        super().__init__(source)
        self.name = ""
        self.value = ""
        self.translation = ""
        self.delimiter = "="
        self.comments = []
        self.source = source
        # a pair of symbols to enclose delimiter on the output
        # (a " " can be used for the sake of convenience)
        self.out_delimiter_wrappers = getattr(self.personality,
                                              'out_delimiter_wrappers', '')
        # symbol that should end every property sentence
        # (e.g. ";" is required for Mac OS X strings)
        self.out_ending = getattr(self.personality, 'out_ending', '')

    @property
    def source(self):
        return self.personality.decode(self.value)

    @source.setter
    def source(self, source):
        self._rich_source = None
        self.value = self.personality.encode(data.forceunicode(source) or "",
                                             self.encoding)

    @property
    def target(self):
        return re.sub("\\\\ ", " ", self.personality.decode(self.translation))

    @target.setter
    def target(self, target):
        self._rich_target = None
        target = data.forceunicode(target)
        self.translation = self.personality.encode(target or "",
                                                   self.encoding)

    @property
    def encoding(self):
        if self._store:
            return self._store.encoding
        else:
            return self.personality.default_encoding

    def __str__(self):
        """Convert to a string."""
        return self.getoutput()

    def getoutput(self):
        """Convert the element back into formatted lines for a .properties file
        """
        notes = self.getnotes()
        if notes:
            notes += "\n"
        if self.isblank():
            return notes + "\n"
        else:
            self.value = self.personality.encode(self.source, self.encoding)
            self.translation = self.personality.encode(self.target,
                                                       self.encoding)
            # encode key, if needed
            key = self.name
            kwc = self.personality.key_wrap_char
            if kwc:
                key = key.replace(kwc, '\\%s' % kwc)
                key = '%s%s%s' % (kwc, key, kwc)
            # encode value, if needed
            value = self.translation or self.value
            vwc = self.personality.value_wrap_char
            if vwc:
                value = value.replace(vwc, '\\%s' % vwc)
                value = '%s%s%s' % (vwc, value, vwc)
            wrappers = self.out_delimiter_wrappers
            delimiter = '%s%s%s' % (wrappers, self.delimiter, wrappers)
            ending = self.out_ending
            out_dict = {
                "notes": notes,
                "key": key,
                "del": delimiter,
                "value": value,
                "ending": ending,
            }
            return "%(notes)s%(key)s%(del)s%(value)s%(ending)s\n" % out_dict

    def getlocations(self):
        return [self.name]

    def addnote(self, text, origin=None, position="append"):
        if origin in ['programmer', 'developer', 'source code', None]:
            text = data.forceunicode(text)
            self.comments.append(text)
        else:
            return super().addnote(text, origin=origin, position=position)

    def getnotes(self, origin=None):
        if origin in ['programmer', 'developer', 'source code', None]:
            return '\n'.join(self.comments)
        else:
            return super().getnotes(origin)

    def removenotes(self, origin=None):
        self.comments = []

    def isblank(self):
        """returns whether this is a blank element, containing only comments.
        """
        return not (self.name or self.value)

    def istranslatable(self):
        return bool(self.name)

    def getid(self):
        return self.name

    def setid(self, value):
        self.name = value


class propfile(base.TranslationStore):
    """this class represents a .properties file, made up of propunits"""

    UnitClass = propunit

    def __init__(self, inputfile=None, personality="java", encoding=None):
        """construct a propfile, optionally reading in from inputfile"""
        super().__init__()
        self.personality = get_dialect(personality)
        self.encoding = encoding or self.personality.default_encoding
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
            propsrc = inputfile.read()
            inputfile.close()
            self.parse(propsrc)
            self.makeindex()

    def parse(self, propsrc):
        """Read the source of a properties file in and include them as units.
        """
        text, encoding = self.detect_encoding(
            propsrc, default_encodings=[self.personality.default_encoding,
                                        'utf-8', 'utf-16'])
        if not text and propsrc:
            raise IOError("Cannot detect encoding for %s." % (self.filename or
                                                              "given string"))
        self.encoding = encoding
        propsrc = text

        newunit = propunit("", self.personality.name)
        inmultilinevalue = False
        inmultilinecomment = False
        was_header = False

        for line in propsrc.split("\n"):
            # handle multiline value if we're in one
            line = quote.rstripeol(line)
            if inmultilinevalue:
                newunit.value += line.lstrip()
                # see if there's more
                inmultilinevalue = self.personality.is_line_continuation(
                    newunit.value)
                # if we're still waiting for more...
                if inmultilinevalue:
                    newunit.value = self.personality.strip_line_continuation(
                        newunit.value)
                if not inmultilinevalue:
                    # we're finished, add it to the list...
                    newunit.value = self.personality.value_strip(newunit.value)
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
            # otherwise, this could be a comment
            # FIXME handle // inline comments
            elif (inmultilinecomment or is_comment_one_line(line) or
                  is_comment_start(line) or is_comment_end(line)):
                # add a comment
                if line not in self.personality.drop_comments:
                    newunit.comments.append(line)
                if is_comment_start(line):
                    inmultilinecomment = True
                elif is_comment_end(line):
                    inmultilinecomment = False
            elif not line.strip():
                # this is a blank line...
                # avoid adding comment only units
                if newunit.name:
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
                elif not was_header and str(newunit).strip():
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
                    was_header = True
                elif newunit.comments:
                    newunit.comments.append("")
            else:
                newunit.delimiter, delimiter_pos = self.personality.find_delimiter(line)
                if delimiter_pos == -1:
                    newunit.name = self.personality.key_strip(line)
                    newunit.value = ""
                    newunit.delimiter = ""
                    self.addunit(newunit)
                    newunit = propunit("", self.personality.name)
                else:
                    newunit.name = self.personality.key_strip(line[:delimiter_pos])
                    if self.personality.is_line_continuation(
                            line[delimiter_pos+1:].lstrip()):
                        inmultilinevalue = True
                        newunit.value = line[delimiter_pos+1:].lstrip()[:-1]
                        newunit.value = self.personality.strip_line_continuation(
                            line[delimiter_pos+1:].lstrip())
                    else:
                        newunit.value = self.personality.value_strip(line[delimiter_pos+1:])
                        self.addunit(newunit)
                        newunit = propunit("", self.personality.name)
        # see if there is a leftover one...
        if inmultilinevalue or len(newunit.comments) > 0:
            self.addunit(newunit)

        self.fold()

    def fold(self):
        old_units = self.units
        self.units = []
        plurals = {}
        for unit in old_units:
            if not unit.istranslatable():
                self.addunit(unit)
                continue
            (key, variant) = self.personality.get_key_cldr_name(unit.name)
            if key not in plurals or plurals[key].hasplural(variant):
                # Generate fake unit for each keys (MUST use None as source)
                new_unit = proppluralunit(None, self.personality.name)
                new_unit.name = key
                self.addunit(new_unit)
                plurals[key] = new_unit

            # Put the unit
            plurals[key].add_unit(unit, variant)

    def serialize(self, out):
        """Write the units back to file."""
        # Thanks to iterencode, a possible BOM is written only once
        for chunk in iterencode((unit.getoutput() for unit in self.units), self.encoding):
            out.write(chunk)


class javafile(propfile):
    Name = "Java Properties"
    Extensions = ['properties']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "java"
        kwargs['encoding'] = "auto"
        super().__init__(*args, **kwargs)


class javautf8file(propfile):
    Name = "Java Properties (UTF-8)"
    Extensions = ['properties']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "java-utf8"
        kwargs['encoding'] = "utf-8"
        super().__init__(*args, **kwargs)


class javautf16file(propfile):
    Name = "Java Properties (UTF-16)"
    Extensions = ['properties']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "java-utf16"
        kwargs['encoding'] = "utf-16"
        super().__init__(*args, **kwargs)


class gwtfile(propfile):
    Name = "Gwt Properties"
    Extensions = ['properties']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "gwt"
        kwargs['encoding'] = "utf-8"
        super(gwtfile, self).__init__(*args, **kwargs)


class stringsfile(propfile):
    Name = "OS X Strings"
    Extensions = ['strings']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "strings"
        super().__init__(*args, **kwargs)


class stringsutf8file(stringsfile):
    Name = "OS X Strings (UTF-8)"
    Extensions = ['strings']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "strings-utf8"
        kwargs['encoding'] = "utf-8"
        super().__init__(*args, **kwargs)


class joomlafile(propfile):
    Name = "Joomla Translations"
    Extensions = ['ini']

    def __init__(self, *args, **kwargs):
        kwargs['personality'] = "joomla"
        super().__init__(*args, **kwargs)
