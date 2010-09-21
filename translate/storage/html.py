#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006,2008 Zuza Software Foundation
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
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""module for parsing html files for translation"""

import re
import htmlentitydefs
import HTMLParser

from translate.storage import base

# Override the piclose tag from simple > to ?> otherwise we consume HTML
# within the processing instructions
HTMLParser.piclose = re.compile('\?>')


strip_html_re = re.compile(r'''
^             # Start of the text
<             # Opening of HTML
(?P<tag>\S+)  # Tag
(?:
(?:\s+\w+\s*=\s*.*)+
|)
>             # Closing of tag

(.*)          # Contents of tag

</(?P=tag)>   # Ending tag
$             # End of text
''', re.VERBOSE | re.DOTALL)


def strip_html(text):
    """Strip unnecessary html from the text.

    HTML tags are deemed unnecessary if it fully encloses the translatable
    text, eg. '<a href="index.html">Home Page</a>'.

    HTML tags that occurs within the normal flow of text will not be removed,
    eg. 'This is a link to the <a href="index.html">Home Page</a>.'
    """
    text = text.strip()

    # If all that is left is PHP, return ""
    result = re.findall('(?s)^<\?.*?\?>$', text)
    if len(result) == 1:
        return ""

    result = strip_html_re.findall(text)
    if len(result) == 1:
        text = strip_html(result[0][1])
    return text


class htmlunit(base.TranslationUnit):
    """A unit of translatable/localisable HTML content"""

    def __init__(self, source=None):
        self.locations = []
        self.setsource(source)

    def getsource(self):
        #TODO: Rethink how clever we should try to be with html entities.
        return self.text.replace("&amp;", "&").replace("&lt;", "<").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

    def setsource(self, source):
        self._rich_source = None
        self.text = source.replace("&", "&amp;").replace("<", "&lt;")
    source = property(getsource, setsource)

    def addlocation(self, location):
        self.locations.append(location)

    def getlocations(self):
        return self.locations


class htmlfile(HTMLParser.HTMLParser, base.TranslationStore):
    UnitClass = htmlunit
    markingtags = ["p", "title", "h1", "h2", "h3", "h4", "h5", "h6", "th", "td", "div", "li", "dt", "dd", "address", "caption"]
    markingattrs = []
    includeattrs = ["alt", "summary", "standby", "abbr", "content"]

    def __init__(self, includeuntaggeddata=None, inputfile=None):
        self.units = []
        self.filename = getattr(inputfile, 'name', None)
        self.currentblock = u""
        self.currentblocknum = 0
        self.currentcomment = u""
        self.currenttag = None
        self.currentpos = -1
        self.tag_path = []
        self.filesrc = u""
        self.includeuntaggeddata = includeuntaggeddata
        HTMLParser.HTMLParser.__init__(self)

        if inputfile is not None:
            htmlsrc = inputfile.read()
            inputfile.close()
            self.parse(htmlsrc)

    def guess_encoding(self, htmlsrc):
        """Returns the encoding of the html text.

        We look for 'charset=' within a meta tag to do this.
        """

        pattern = '''(?i)<meta.*content.*=.*charset.*=\\s*([^\\s]*)\\s*["']'''
        result = re.findall(pattern, htmlsrc)
        encoding = None
        if result:
            encoding = result[0]
        return encoding

    def do_encoding(self, htmlsrc):
        """Return the html text properly encoded based on a charset."""
        charset = self.guess_encoding(htmlsrc)
        if charset:
            return htmlsrc.decode(charset)
        else:
            return htmlsrc.decode('utf-8')

    def parse(self, htmlsrc):
        htmlsrc = self.do_encoding(htmlsrc)
        self.feed(htmlsrc)

    def addhtmlblock(self, text):
        text = strip_html(text)
        if self.has_translatable_content(text):
            self.currentblocknum += 1
            unit = self.addsourceunit(text)
            unit.addlocation("%s+%s:%d" % (self.filename, ".".join(self.tag_path), self.currentpos))
            unit.addnote(self.currentcomment)

    def has_translatable_content(self, text):
        """Check if the supplied HTML snippet has any content that needs to be translated."""

        text = text.strip()
        result = re.findall('(?i).*(charset.*=.*)', text)
        if len(result) == 1:
            return False

        # TODO: Get a better way to find untranslatable entities.
        if text == '&nbsp;':
            return False

        pattern = '<\?.*?\?>' # Lazily strip all PHP
        result = re.sub(pattern, '', text).strip()
        pattern = '<[^>]*>' #Strip all HTML tags
        result = re.sub(pattern, '', result).strip()
        if result:
            return True
        else:
            return False

#From here on below, follows the methods of the HTMLParser

    def startblock(self, tag):
        self.addhtmlblock(self.currentblock)
        self.currentblock = ""
        self.currentcomment = ""
        self.currenttag = tag
        self.currentpos = self.getpos()[0]

    def endblock(self):
        self.addhtmlblock(self.currentblock)
        self.currentblock = ""
        self.currentcomment = ""
        self.currenttag = None
        self.currentpos = -1

    def handle_starttag(self, tag, attrs):
        newblock = False
        self.tag_path.append(tag)
        if tag in self.markingtags:
            newblock = True
        for attrname, attrvalue in attrs:
            if attrname in self.markingattrs:
                newblock = True
            if attrname in self.includeattrs and self.currentblock == "":
                self.addhtmlblock(attrvalue)

        if newblock:
            self.startblock(tag)
        elif self.currenttag is not None:
            self.currentblock += self.get_starttag_text()

        if attrs != []:
            self.filesrc += "<%(tag)s %(attrs)s>" % {"tag": tag, "attrs": " ".join(['%s="%s"' % pair for pair in attrs])}
        else:
            self.filesrc += "<%(tag)s>" % {"tag": tag}

    def handle_startendtag(self, tag, attrs):
        for attrname, attrvalue in attrs:
            if attrname in self.includeattrs and self.currentblock == "":
                self.addhtmlblock(attrvalue)
        if self.currenttag is not None:
            self.currentblock += self.get_starttag_text()

        self.filesrc += "<%(tag)s %(attrs)s />" % {"tag": tag, "attrs": " ".join(['%s="%s"' % pair for pair in attrs])}

    def handle_endtag(self, tag):
        if tag == self.currenttag:
            self.endblock()
        elif self.currenttag is not None:
            self.currentblock += '</%s>' % tag
        self.tag_path.pop()
        self.filesrc += "</%(tag)s>" % {"tag": tag}

    def handle_data(self, data):
        if self.currenttag is not None:
            self.currentblock += data
        elif self.includeuntaggeddata:
            self.startblock(None)
            self.currentblock += data
        self.filesrc += data

    def handle_charref(self, name):
        """Handle entries in the form &#NNNN; e.g. &#8417;"""
        self.handle_data(unichr(int(name)))

    def handle_entityref(self, name):
        """Handle named entities of the form &aaaa; e.g. &rsquo;"""
        if name in ['gt', 'lt', 'amp']:
            self.handle_data("&%s;" % name)
        else:
            self.handle_data(unichr(htmlentitydefs.name2codepoint.get(name, u"&%s;" % name)))

    def handle_comment(self, data):
        # we can place comments above the msgid as translator comments!
        if self.currentcomment == "":
            self.currentcomment = data
        else:
            self.currentcomment += u'\n' + data
        self.filesrc += "<!--%s-->" % data

    def handle_pi(self, data):
        self.handle_data("<?%s?>" % data)


class POHTMLParser(htmlfile):
    pass
