#
# Copyright 2012 Michal Čihař
# Copyright 2014 Luca De Petrillo
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

"""Module for handling Android String and Plurals resource files."""

import copy
import os
import re

from lxml import etree

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import base, lisa


EOF = None
WHITESPACE = " \n\t"  # Whitespace that we collapse.
MULTIWHITESPACE = re.compile("[ \n\t]{2}(?!\\\\n)")


class AndroidResourceUnit(base.TranslationUnit):
    """A single entry in the Android String resource file."""

    @classmethod
    def createfromxmlElement(cls, element):
        term = None
        # Actually this class supports only plurals and string tags
        if element.tag in ("plurals", "string"):
            term = cls(None, xmlelement=element)
        return term

    def __init__(self, source, empty=False, xmlelement=None, **kwargs):
        if xmlelement is not None:
            self.xmlelement = xmlelement
        else:
            if self.hasplurals(source):
                self.xmlelement = etree.Element("plurals")
            else:
                self.xmlelement = etree.Element("string")
        if source is not None:
            self.setid(source)
        super().__init__(source)

    def istranslatable(self):
        return bool(self.getid()) and self.xmlelement.get("translatable") != "false"

    def isblank(self):
        return not bool(self.getid())

    def getid(self):
        return self.xmlelement.get("name")

    def setid(self, newid):
        return self.xmlelement.set("name", newid)

    def getcontext(self):
        return self.xmlelement.get("name")

    @staticmethod
    def unescape(text, strip=True):
        """
        Remove escaping from Android resource.

        Code stolen from android2po
        <https://github.com/miracle2k/android2po>
        """
        # Return text for empty elements
        if text is None:
            return ""

        # We need to collapse multiple whitespace while paying
        # attention to Android's quoting and escaping.
        space_count = 0
        active_quote = False
        active_percent = False
        active_escape = False
        i = 0
        text = list(text) + [EOF]
        while i < len(text):
            c = text[i]

            if not active_escape:
                # Handle whitespace collapsing
                if c is not EOF and c in WHITESPACE:
                    space_count += 1
                elif space_count > 1:
                    # Remove duplicate whitespace; Pay attention: We
                    # don't do this if we are currently inside a quote,
                    # except for one special case: If we have unbalanced
                    # quotes, e.g. we reach eof while a quote is still
                    # open, we *do* collapse that trailing part; this is
                    # how Android does it, for some reason.
                    if not active_quote or c is EOF:
                        # Replace by a single space, will get rid of
                        # non-significant newlines/tabs etc.
                        text[i - space_count : i] = " "
                        i -= space_count - 1
                        if strip and (i == 1 or c is EOF):
                            del text[i - 1]
                    space_count = 0
                elif space_count == 1:
                    # At this point we have a single whitespace character,
                    # but it might be a newline or tab. If we write this
                    # kind of insignificant whitespace into the .po file,
                    # it will be considered significant on import. So,
                    # make sure that this kind of whitespace is always a
                    # standard space.
                    text[i - 1] = " "
                    if strip and not active_quote and (i == 1 or c is EOF):
                        del text[i - 1]
                    space_count = 0
                else:
                    space_count = 0

            # Handle quotes
            if c == '"' and not active_escape:
                active_quote = not active_quote
                del text[i]
                i -= 1

            # If the string is run through a formatter, it will have
            # percentage signs for String.format
            if c == "%" and not active_escape:
                active_percent = not active_percent
            elif not active_escape and active_percent:
                active_percent = False

            # Handle escapes
            if c == "\\":
                if not active_escape:
                    active_escape = True
                else:
                    # A double-backslash represents a single;
                    # simply deleting the current char will do.
                    del text[i]
                    i -= 1
                    active_escape = False
            else:
                if active_escape:
                    # Handle the limited amount of escape codes
                    # that we support.
                    # TODO: What about \r, or \r\n?
                    if c is EOF:
                        # Basically like any other char, but put
                        # this first so we can use the ``in`` operator
                        # in the clauses below without issue.
                        pass
                    elif c in ("n", "N"):
                        # Remove whitespace just before newline. Most likely this is result of
                        # having real newline in the XML in front of \n.
                        if i >= 2 and text[i - 2] == " ":
                            offset = 2
                        else:
                            offset = 1
                        text[i - offset : i + 1] = "\n"  # an actual newline
                        i -= offset
                    elif c in ("t", "T"):
                        text[i - 1 : i + 1] = "\t"  # an actual tab
                        i -= 1
                    elif c == " ":
                        text[i - 1 : i + 1] = " "  # an actual space
                        i -= 1
                    elif c in "\"'@?":
                        text[i - 1 : i] = ""  # remove the backslash
                        i -= 1
                    elif c == "u":
                        # Unicode sequence. Android is nice enough to deal
                        # with those in a way which let's us just capture
                        # the next 4 characters and raise an error if they
                        # are not valid (rather than having to use a new
                        # state to parse the unicode sequence).
                        # Exception: In case we are at the end of the
                        # string, we support incomplete sequences by
                        # prefixing the missing digits with zeros.
                        # Note: max(len()) is needed in the slice due to
                        # trailing ``None`` element.
                        max_slice = min(i + 5, len(text) - 1)
                        codepoint_str = "".join(text[i + 1 : max_slice])
                        if len(codepoint_str) < 4:
                            codepoint_str = (
                                "0" * (4 - len(codepoint_str)) + codepoint_str
                            )
                        try:
                            # We can't trust int() to raise a ValueError,
                            # it will ignore leading/trailing whitespace.
                            if not codepoint_str.isalnum():
                                raise ValueError(codepoint_str)
                            codepoint = chr(int(codepoint_str, 16))
                        except ValueError:
                            raise ValueError("bad unicode escape sequence")

                        text[i - 1 : max_slice] = codepoint
                        i -= 1
                    else:
                        # All others, remove, like Android does as well.
                        text[i - 1 : i + 1] = ""
                        i -= 1
                    active_escape = False

            i += 1

        # Join the string together again, but w/o EOF marker
        return "".join(text[:-1])

    @staticmethod
    def xml_escape_space(matchobj):
        return matchobj.group(0).replace("  ", r" \u0020")

    def escape(self, text, quote_wrapping_whitespaces=True):
        """Escape all the characters which need to be escaped in an Android XML
        file.

        :param text: Text to escape
        :param quote_wrapping_whitespaces: If True, heading and trailing
               whitespaces will be quoted placing the entire resulting text in
               double quotes.
        """
        if text is None:
            return
        if len(text) == 0:
            return ""
        text = text.replace("\\", "\\\\")
        # This will add non intrusive real newlines to
        # ones in translation improving readability of result
        text = text.replace("\n", "\n\\n")
        text = text.replace("\t", "\\t")
        text = text.replace("'", "\\'")
        text = text.replace("?", "\\?")
        text = text.replace('"', '\\"')

        # @ needs to be escaped at start
        if text.startswith("@"):
            text = "\\@" + text[1:]
        # Quote strings with more whitespace
        multispace = MULTIWHITESPACE.findall(text)
        if quote_wrapping_whitespaces and (
            text[0] in WHITESPACE or text[-1] in WHITESPACE or multispace
        ):
            return '"%s"' % text
        # In xml multispace
        if not quote_wrapping_whitespaces and multispace:
            return MULTIWHITESPACE.sub(self.xml_escape_space, text)

        return text

    @base.TranslationUnit.source.getter
    def source(self):
        if super().source is None:
            return self.target
        return super().source

    def get_xml_text_value(self, xmltarget):
        if len(xmltarget) == 0:
            # There are no html markups, so unescaping it as plain text.
            return self.unescape(xmltarget.text)
        else:
            # There are html markups, so clone it to perform unescaping for all elements.
            cloned_target = copy.deepcopy(xmltarget)

            # Unescaping texts.
            if cloned_target.text is not None:
                cloned_target.text = self.unescape(cloned_target.text, False)
            for xmlelement in cloned_target.iterdescendants():
                if xmlelement.text is not None and xmlelement.tag is not etree.Entity:
                    xmlelement.text = self.unescape(xmlelement.text, False)
                if xmlelement.tail is not None:
                    xmlelement.tail = self.unescape(xmlelement.tail, False)

            # Grab root text (using a temporary xml element for text escaping)
            if cloned_target.text is not None:
                tmp_element = etree.Element("t")
                tmp_element.text = cloned_target.text
                target = etree.tostring(tmp_element, encoding="unicode")[3:-4]
            else:
                target = ""

            # Include markup as well
            target += "".join(
                etree.tostring(child, encoding="unicode")
                for child in cloned_target.iterchildren()
            )
            return target

    def set_xml_text_plain(self, target, xmltarget):
        # Remove possible old elements
        for x in xmltarget.iterchildren():
            xmltarget.remove(x)
        # Handle text only
        xmltarget.text = self.escape(target)

    def set_xml_text_value(self, target, xmltarget):
        if "<" in target or "&" in target:
            # Try to handle it as legacy XML
            parser = etree.XMLParser(strip_cdata=False, resolve_entities=False)
            if self._store is not None:
                cloned_doc = copy.deepcopy(self._store.document)
                cloned_root = cloned_doc.getroot()
                cloned_root.clear()
                # Add content to the element so that we get a real closing tag
                cloned_root.text = " "
                template = etree.tostring(
                    cloned_doc,
                    encoding="unicode",
                    doctype=copy.copy(self._store.XMLdoctype),
                )
            else:
                template = "<resources></resources>"
            newstring = template.replace(
                "</resources>", f"<string>{target}</string></resources>"
            )
            try:
                newstring = etree.fromstring(newstring, parser)[0]
            except Exception:
                self.set_xml_text_plain(target, xmltarget)
            else:
                # Escape all text parts.
                if newstring.text is not None:
                    newstring.text = self.escape(newstring.text, False)
                for x in newstring.iterdescendants():
                    if x.text is not None and x.tag is not etree.Entity:
                        x.text = self.escape(x.text, False)
                    if x.tail is not None:
                        x.tail = self.escape(x.tail, False)

                # Update text
                xmltarget.text = newstring.text

                # Remove old elements
                for x in xmltarget.iterchildren():
                    xmltarget.remove(x)
                # Add new elements
                for x in newstring.iterchildren():
                    xmltarget.append(x)
        else:
            self.set_xml_text_plain(target, xmltarget)

    def gettargetlanguage(self):
        if self._store is None:
            return "en"
        return super().gettargetlanguage()

    def get_plural_tags(self):
        locale = self.gettargetlanguage()
        if not locale:
            return data.plural_tags["en"]
        # Handle b+ style language codes
        if locale.startswith("b+"):
            locale = locale[2:]
        locale = locale.replace("_", "-").replace("+", "-").split("-")[0]
        return data.plural_tags.get(locale, data.plural_tags["en"])

    @property
    def target(self):
        if self.xmlelement.tag != "plurals":
            return self.get_xml_text_value(self.xmlelement)
        plurals = {
            entry.get("quantity"): self.get_xml_text_value(entry)
            for entry in self.xmlelement.iterchildren("item")
        }
        plural_tags = self.get_plural_tags()
        print(plurals, plural_tags)
        print([plurals.get(tag, "") for tag in plural_tags])
        return multistring([plurals.get(tag, "") for tag in plural_tags])

    @target.setter
    def target(self, target):
        if self.hasplurals(self.source) or self.hasplurals(target):
            # Fix the root tag if mismatching
            if self.xmlelement.tag != "plurals":
                old_id = self.getid()
                self.xmlelement = etree.Element("plurals")
                self.setid(old_id)

            plural_tags = self.get_plural_tags()

            # Get string list to handle, wrapping non multistring/list targets into a list.
            if isinstance(target, multistring):
                plural_strings = target.strings
            elif isinstance(target, list):
                plural_strings = target
            else:
                plural_strings = [target]

            # Sync plural_strings elements to plural_tags count.
            if len(plural_strings) < len(plural_tags):
                plural_strings += [""] * (len(plural_tags) - len(plural_strings))
            plural_strings = plural_strings[: len(plural_tags)]

            # Rebuild plurals.
            for entry in self.xmlelement.iterchildren():
                self.xmlelement.remove(entry)

            self.xmlelement.text = "\n    "

            # Include "other" as copy of "many" if "other" is not present. This avoids crashes
            # of Android builts with broken plurals handling.
            if "other" not in plural_tags and "many" in plural_tags:
                # Create copy here to avoid modifications to laguage.data
                plural_tags = plural_tags + ["other"]
                plural_strings.append(plural_strings[-1])

            for plural_tag, plural_string in zip(plural_tags, plural_strings):
                item = etree.Element("item")
                item.set("quantity", plural_tag)
                self.set_xml_text_value(plural_string, item)
                self.xmlelement.append(item)
        else:
            # Fix the root tag if mismatching
            if self.xmlelement.tag != "string":
                old_id = self.getid()
                self.xmlelement = etree.Element("string")
                self.setid(old_id)

            self.set_xml_text_value(target, self.xmlelement)

        self._rich_target = None
        self._target = target

    def getlanguageNode(self, lang=None, index=None):
        return self.xmlelement

    # Notes are handled as previous sibling comments.
    def addnote(self, text, origin=None, position="append"):
        if origin in ["programmer", "developer", "source code", None]:
            self.xmlelement.addprevious(etree.Comment(text))
        else:
            super().addnote(text, origin=origin, position=position)

    def getnotes(self, origin=None):
        if origin in ["programmer", "developer", "source code", None]:
            comments = []
            if self.xmlelement is not None:
                prevSibling = self.xmlelement.getprevious()
                while (prevSibling is not None) and (prevSibling.tag is etree.Comment):
                    comments.insert(0, prevSibling.text)
                    prevSibling = prevSibling.getprevious()

            return "\n".join(comments)
        else:
            return super().getnotes(origin)

    def removenotes(self, origin=None):
        if (self.xmlelement is not None) and (self.xmlelement.getparent is not None):
            prevSibling = self.xmlelement.getprevious()
            while (prevSibling is not None) and (prevSibling.tag is etree.Comment):
                prevSibling.getparent().remove(prevSibling)
                prevSibling = self.xmlelement.getprevious()

        super().removenotes()

    def __str__(self):
        return etree.tostring(self.xmlelement, pretty_print=True, encoding="unicode")

    def __eq__(self, other):
        return str(self) == str(other)

    @staticmethod
    def hasplurals(thing):
        if isinstance(thing, multistring):
            return True
        elif isinstance(thing, list):
            return True
        return False


class AndroidResourceFile(lisa.LISAfile):
    """Class representing an Android String resource file store."""

    UnitClass = AndroidResourceUnit
    Name = "Android String Resource"
    Mimetypes = ["application/xml"]
    Extensions = ["xml"]
    rootNode = "resources"
    bodyNode = "resources"
    XMLskeleton = """<?xml version="1.0" encoding="utf-8"?>
<resources></resources>"""
    XMLindent = {"indent": "    ", "leaves": {"string", "item"}}
    XMLuppercaseEncoding = False

    def initbody(self):
        """Initialises self.body so it never needs to be retrieved from the XML
        again.
        """
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.body = self.document.getroot()

    def parse(self, xml):
        """Populates this object from the given xml string"""
        if not hasattr(self, "filename"):
            self.filename = getattr(xml, "name", "")
        if hasattr(xml, "read"):
            xml.seek(0)
            posrc = xml.read()
            xml = posrc
        parser = etree.XMLParser(strip_cdata=False, resolve_entities=False)
        self.document = etree.fromstring(xml, parser).getroottree()
        self._encoding = self.document.docinfo.encoding
        self.initbody()
        assert self.document.getroot().tag == self.namespaced(self.rootNode)

        for entry in self.document.getroot().iterchildren():
            term = self.UnitClass.createfromxmlElement(entry)
            if term is not None:
                self.addunit(term, new=False)

    def gettargetlanguage(self):
        target_lang = super().gettargetlanguage()

        # If targetlanguage isn't set, we try to extract it from the filename path (if any).
        if target_lang is None and hasattr(self, "filename") and self.filename:
            # Android standards expect resource files to be in a directory named "values[-<lang>[-r<region>]]".
            parent_dir = os.path.split(os.path.dirname(self.filename))[1]
            match = re.search(r"^values-(\w*)", parent_dir)
            if match is not None:
                target_lang = match.group(1)
            elif parent_dir == "values":
                # If the resource file is inside the "values" directory, then it is the default/source language.
                target_lang = self.sourcelanguage

            # Cache it
            self.settargetlanguage(target_lang)

        return target_lang

    def addunit(self, unit, new=True):
        """Adds unit to the document

        In addition to the standard addunit, it also tries to move
        namespace definitions to the top <resources> element.
        """
        newns = {}
        do_cleanup = False
        if new:
            # Include any possible new namespaces
            newns = self.body.nsmap
            for ns in unit.xmlelement.nsmap:
                if ns not in newns:
                    do_cleanup = True
                    newns[ns] = unit.xmlelement.nsmap[ns]

            # Detect if unit is using XML entities
            hasentity = False
            for xmlelement in unit.xmlelement.iterdescendants():
                if xmlelement.tag is etree.Entity:
                    hasentity = True
                    break

            # Copy doctype to include possibly new entities
            if hasentity:
                cloned_doc = copy.deepcopy(unit._store.document)
                cloned_doc.getroot().clear()
                self.XMLdoctype = etree.tostring(
                    cloned_doc, xml_declaration=False, encoding="unicode"
                ).rsplit("\n", 1)[0]

        super().addunit(unit, new)
        # Move aliased namespaces to the <resources> tag
        # The top_nsmap was introduced in LXML 3.5.0
        if do_cleanup:
            etree.cleanup_namespaces(self.body, top_nsmap=newns)
