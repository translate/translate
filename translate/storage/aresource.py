#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Michal ÄŒihaÅ™
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
"""module for handling Android resource files"""

import re
import copy

from lxml import etree
from translate.misc.multistring import multistring
from translate.storage import lisa
from translate.storage import base
from translate.lang import data

EOF = None
WHITESPACE = ' \n\t' # Whitespace that we collapse
MULTIWHITESPACE = re.compile('[ \n\t]{2}')

class AndroidResourceUnit(base.TranslationUnit):
    """A single term in the Android resource file."""
    """<string-array> <item> """
    """ <plurals> <item quantity=""> """
    
    """List built from Unicode plural rules page:"""
    """http://www.unicode.org/cldr/charts/supplemental/language_plural_rules.html"""
    unicodePlurals = {
            'af': ('one','other'),
            'ak': ('one','other'),
            'sq': ('one','other'),
            'am': ('one','other'),
            'ar': ('zero','one','two','few','many','other'),
            'ast': ('one','other'),
            'asa': ('one','other'),
            'az': ('other'),
            'bm': ('other'),
            'eu': ('one','other'),
            'be': ('one','few','many','other'),
            'bem': ('one','other'),
            'bez': ('one','other'),
            'bn': ('one','other'),
            'bh': ('one','other'),
            'brx': ('one','other'),
            'bs': ('one','few','many','other'),
            'br': ('one','two','few','other'),
            'bg': ('one','other'),
            'my': ('other'),
            'ca': ('one','other'),
            'tzm': ('one','other'),
            'chr': ('one','other'),
            'cgg': ('one','other'),
            'zh': ('other'),
            'ksh': ('zero','one','other'),
            'kw': ('one','two','other'),
            'hr': ('one','few','many','other'),
            'cs': ('one','few','other'),
            'da': ('one','other'),
            'dv': ('one','other'),
            'nl': ('one','other'),
            'dz': ('other'),
            'en': ('one','other'),
            'eo': ('one','other'),
            'et': ('one','other'),
            'ee': ('one','other'),
            'fo': ('one','other'),
            'fil': ('one','other'),
            'fi': ('one','other'),
            'fr': ('one','other'),
            'fur': ('one','other'),
            'ff': ('one','other'),
            'gl': ('one','other'),
            'lg': ('one','other'),
            'ka': ('other'),
            'de': ('one','other'),
            'el': ('one','other'),
            'gu': ('one','other'),
            'guw': ('one','other'),
            'ha': ('one','other'),
            'haw': ('one','other'),
            'he': ('one','two','many','other'),
            'hi': ('one','other'),
            'hu': ('other'),
            'is': ('one','other'),
            'ig': ('other'),
            'smn': ('one','two','other'),
            'id': ('other'),
            'iu': ('one','two','other'),
            'ga': ('one','two','few','many','other'),
            'it': ('one','other'),
            'ja': ('other'),
            'jv': ('other'),
            'kaj': ('one','other'),
            'kea': ('other'),
            'kab': ('one','other'),
            'kkj': ('one','other'),
            'kl': ('one','other'),
            'kn': ('other'),
            'ks': ('one','other'),
            'kk': ('one','other'),
            'km': ('other'),
            'ky': ('one','other'),
            'ko': ('other'),
            'ses': ('other'),
            'ku': ('one','other'),
            'lag': ('zero','one','other'),
            'lo': ('other'),
            'lv': ('zero','one','other'),
            'ln': ('one','other'),
            'lt': ('one','few','other'),
            'smj': ('one','two','other'),
            'lb': ('one','other'),
            'mk': ('one','other'),
            'jmc': ('one','other'),
            'kde': ('other'),
            'mg': ('one','other'),
            'ms': ('other'),
            'ml': ('one','other'),
            'mt': ('one','few','many','other'),
            'gv': ('one','other'),
            'mr': ('one','other'),
            'mas': ('one','other'),
            'mgo': ('one','other'),
            'mo': ('one','few','other'),
            'mn': ('one','other'),
            'nah': ('one','other'),
            'naq': ('one','two','other'),
            'ne': ('one','other'),
            'nnh': ('one','other'),
            'jgo': ('one','other'),
            'nd': ('one','other'),
            'se': ('one','two','other'),
            'nso': ('one','other'),
            'no': ('one','other'),
            'nb': ('one','other'),
            'nn': ('one','other'),
            'ny': ('one','other'),
            'nyn': ('one','other'),
            'or': ('one','other'),
            'om': ('one','other'),
            'os': ('one','other'),
            'pap': ('one','other'),
            'ps': ('one','other'),
            'fa': ('other'),
            'pl': ('one','few','many','other'),
            'pt': ('one','other'),
            'pa': ('one','other'),
            'ro': ('one','few','other'),
            'rm': ('one','other'),
            'rof': ('one','other'),
            'root': ('other'),
            'ru': ('one','few','many','other'),
            'rwk': ('one','other'),
            'ssy': ('one','other'),
            'sah': ('other'),
            'saq': ('one','other'),
            'smi': ('one','two','other'),
            'sg': ('other'),
            'gd': ('one','two','few','other'),
            'seh': ('one','other'),
            'sr': ('one','few','many','other'),
            'sh': ('one','few','many','other'),
            'ksb': ('one','other'),
            'sn': ('one','other'),
            'ii': ('other'),
            'sms': ('one','two','other'),
            'sk': ('one','few','other'),
            'sl': ('one','two','few','other'),
            'xog': ('one','other'),
            'so': ('one','other'),
            'ckb': ('one','other'),
            'nr': ('one','other'),
            'sma': ('one','two','other'),
            'st': ('one','other'),
            'es': ('one','other'),
            'sw': ('one','other'),
            'ss': ('one','other'),
            'sv': ('one','other'),
            'gsw': ('one','other'),
            'syr': ('one','other'),
            'shi': ('one','few','other'),
            'tl': ('one','other'),
            'ta': ('one','other'),
            'te': ('one','other'),
            'teo': ('one','other'),
            'th': ('other'),
            'bo': ('other'),
            'tig': ('one','other'),
            'ti': ('one','other'),
            'to': ('other'),
            'ts': ('one','other'),
            'tn': ('one','other'),
            'tr': ('other'),
            'tk': ('one','other'),
            'kcg': ('one','other'),
            'uk': ('one','few','many','other'),
            'ur': ('one','other'),
            've': ('one','other'),
            'vi': ('other'),
            'vo': ('one','other'),
            'vun': ('one','other'),
            'wa': ('one','other'),
            'wae': ('one','other'),
            'cy': ('zero','one','two','few','many','other'),
            'fy': ('one','other'),
            'wo': ('other'),
            'xh': ('one','other'),
            'yo': ('other'),
            'zu': ('one','other'),
        }
    
    xmlelement = None
    
    def __init__(self, source, empty=False, xmlelement=None, **kwargs):
        if xmlelement is not None:
            self.xmlelement = xmlelement
        else:
            if self.hasplurals(source):
                self.xmlelement = etree.Element("plurals")
            else:
                self.xmlelement = etree.Element("string")
            
            self.xmlelement.tail = '\n'
            
        super(AndroidResourceUnit, self).__init__(source)

    def istranslatable(self):
        return (
            bool(self.getid())
            and self.xmlelement.get('translatable') != 'false'
        )

    def isblank(self):
        return not bool(self.getid())

    def getid(self):
        return self.xmlelement.get("name")

    def getcontext(self):
        return self.xmlelement.get("name")

    def setid(self, newid):
        return self.xmlelement.set("name", newid)

    def setcontext(self, context):
        return self.xmlelement.set("name", context)

    def unescape(self, text):
        '''
        Remove escaping from Android resource.

        Code stolen from android2po
        <https://github.com/miracle2k/android2po>
        '''
        # Return text for empty elements
        if text is None:
            return ''

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
                    text[i-space_count : i] = ' '
                    i -= space_count - 1
                space_count = 0
            elif space_count == 1:
                # At this point we have a single whitespace character,
                # but it might be a newline or tab. If we write this
                # kind of insignificant whitespace into the .po file,
                # it will be considered significant on import. So,
                # make sure that this kind of whitespace is always a
                # standard space.
                text[i-1] = ' '
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
            if c == '%' and not active_escape:
                active_percent = not active_percent
            elif not active_escape and active_percent:
                active_percent = False

            # Handle escapes
            if c == '\\':
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
                    elif c == 'n' or c == 'N':
                        text[i-1 : i+1] = '\n' # an actual newline
                        i -= 1
                    elif c == 't' or c == 'T':
                        text[i-1 : i+1] = '\t' # an actual tab
                        i -= 1
                    elif c == ' ':
                        text[i-1 : i+1] = ' ' # an actual space
                        i -= 1
                    elif c in '"\'@':
                        text[i-1 : i] = '' # remove the backslash
                        i -= 1
                    elif c == 'u':
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
                        max_slice = min(i+5, len(text)-1)
                        codepoint_str = "".join(text[i+1 : max_slice])
                        if len(codepoint_str) < 4:
                            codepoint_str = u"0" * (4-len(codepoint_str)) + codepoint_str
                        try:
                            # We can't trust int() to raise a ValueError,
                            # it will ignore leading/trailing whitespace.
                            if not codepoint_str.isalnum():
                                raise ValueError(codepoint_str)
                            codepoint = unichr(int(codepoint_str, 16))
                        except ValueError:
                            raise ValueError('bad unicode escape sequence')

                        text[i-1 : max_slice] = codepoint
                        i -= 1
                    else:
                        # All others, remove, like Android does as well.
                        text[i-1 : i+1] = ''
                        i -= 1
                    active_escape = False

            i += 1

        # Join the string together again, but w/o EOF marker
        return "".join(text[:-1])

    def escape(self, text, quoteStartingWhitespace=True, quoteEndingWhitespace=True):
        '''
        Escape all the characters which need to be escaped in an Android XML file.
        '''
        if text is None:
            return
        if len(text) == 0:
            return ''
        text = text.replace('\\', '\\\\')
        text = text.replace('\n', '\\n')
        # This will add non intrusive real newlines to
        # ones in translation improving readability of result
        text = text.replace(' \\n', '\n\\n')
        text = text.replace('\t', '\\t')
        text = text.replace('\'', '\\\'')
        text = text.replace('"', '\\"')

        # @ needs to be escaped at start
        if text.startswith('@'):
            text = '\\@' + text[1:]
        # Quote strings with more whitespace
        if ((quoteStartingWhitespace and (text[0] in WHITESPACE)) 
                or (quoteEndingWhitespace and (text[-1] in WHITESPACE)) 
                or len(MULTIWHITESPACE.findall(text))) > 0:
            return '"%s"' % text
        return text

    def setsource(self, source):
        super(AndroidResourceUnit, self).setsource(source)

    def getsource(self, lang=None):
        if (super(AndroidResourceUnit, self).source is None):
            return self.target
        else:
            return super(AndroidResourceUnit, self).source

    source = property(getsource, setsource)

    def setXmlTextValue(self, target, xmltarget):
        if '<' in target:
            # Handle text with possible markup
            target = target.replace('&', '&amp;')
            
            try:
                # Try as XML
                newstring = etree.fromstring('<string>%s</string>' % target)
            except:
                # Fallback to string with XML escaping
                target = target.replace('<', '&lt;')
                newstring = etree.fromstring('<string>%s</string>' % target)
            # Update text
            if newstring.text is None:
                xmltarget.text = ''
            else:
                xmltarget.text = newstring.text
            # Remove old elements
            for x in xmltarget.iterchildren():
                xmltarget.remove(x)
            # Add new elements
            for x in newstring.iterchildren():
                xmltarget.append(x)
                
            
            # Escape all text elements inside the xml tree.
            # Starting single whitespace must be escaped only for the root tag 
            xmltarget.text = self.escape(xmltarget.text, True, False)
            for x in xmltarget.iterdescendants():
                x.text = self.escape(x.text, False, False)
                # Ending single whitespace must be escaped only for tail of the last child
                x.tail = self.escape(x.tail, False, (x == list(xmltarget)[-1]))
        else:
            # Handle text only
            xmltarget.text = self.escape(target)

    def settarget(self, target):
        if (self.hasplurals(self.source) or self.hasplurals(target)):
            # Replace the root tag if non matching
            if self.xmlelement.tag != "plurals":
                oldId = self.getid()
                self.xmlelement = etree.Element("plurals")
                self.setid(oldId)
        
            targetLang = self.gettargetlanguage();
            
            # If target language isn't set on the store, we try to extract it from the file path
            if (targetLang is None):
                # Android standard expect the folder to be in format "values-{lang}"
                match = re.search('values-(\w*)', self._store.filename);
                if (match is not None):
                    targetLang = re.search('values-(\w*)', self._store.filename).group(1);
                else:
                    # If the store is using the "values" folder, than it is the default language. 
                    targetLang = self._store.sourcelanguage
            
            if (targetLang in self.unicodePlurals):
                targetPlurals = self.unicodePlurals[targetLang]
            else:
                # If we don't know the language, we will use only the general plural form.
                targetPlurals = ("other")
            
            for entry in self.xmlelement.iterchildren():
                self.xmlelement.remove(entry)
                
            self.xmlelement.text = "\n\t"
            
            
            # Getting the string list to handle, wrapping non multistring or list targets into a list.
            if isinstance(target, multistring):
                targetStrings = target.strings
            elif isinstance(target, list):
                targetStrings = target
            else:
                targetStrings = [target]
            
            
            i = 0 
            while i < len(targetPlurals):
                item = etree.Element("item")
                item.set("quantity", targetPlurals[i])
                
                # Safety check: for some language, Unicode rules are more than gettext rules, because Unicode handle 
                # also a different plural for fractional numbers (not support in gettext). 
                # In this case, we use the last gettext plural for both general and fractional numbers.
                if i < len(targetStrings):
                    currentTarget = targetStrings[i];
                else:
                    currentTarget = targetStrings[-1];
                    
                self.setXmlTextValue(currentTarget, item)
                
                item.tail = "\n\t"
                
                self.xmlelement.append(item)
                
                i += 1
            
            # Remove the tab from last item
            item.tail = "\n"
        else:
            # Replace the root tag if wrong
            if self.xmlelement.tag != "string":
                oldId = self.getid()
                self.xmlelement = etree.Element("string")
                self.setid(oldId)
                
            self.setXmlTextValue(target, self.xmlelement)
        
        super(AndroidResourceUnit, self).settarget(target)

    def getXmlTextValue(self, xmltarget):
        # Cloning xml tree to perform unescaping on all the structure (including nested tags text) 
        clonedTarget = copy.deepcopy(xmltarget)
        
        # Unescaping the text for the complete xml tree
        clonedTarget.text = self.unescape(clonedTarget.text);
        for x in clonedTarget.iterdescendants():
            x.text = self.unescape(x.text)
            x.tail = self.unescape(x.tail)
               
        # Grab inner text
        target = clonedTarget.text or u''
        # Include markup as well
        target += u''.join([data.forceunicode(etree.tostring(child, encoding='utf-8')) for child in clonedTarget.iterchildren()])
        
        return target

    def gettarget(self, lang=None):
        if (self.xmlelement.tag == "plurals"):
            target = []
            for entry in self.xmlelement.iterchildren():
                target.append(self.getXmlTextValue(entry))
            return multistring(target, self._store._encoding)
        else:
            return self.getXmlTextValue(self.xmlelement)

    target = property(gettarget, settarget)

    def getlanguageNode(self, lang=None, index=None):
        return self.xmlelement

    def createfromxmlElement(cls, element):
        term = None
        # Actaully this class supports only plurals and string tags 
        if ((element.tag == "plurals") or (element.tag == "string")):
            term = cls(None, xmlelement = element)
            
        return term
    
    createfromxmlElement = classmethod(createfromxmlElement)

    # Notes are handled as previous sibling comments.
    def addnote(self, text, origin=None, position="append"):
        if origin in ['programmer', 'developer', 'source code', None]:
            self.xmlelement.addprevious(etree.Comment(text))
        else:
            return super(AndroidResourceUnit, self).addnote(text, origin=origin,
                                                 position=position)

    def getnotes(self, origin=None):
        if origin in ['programmer', 'developer', 'source code', None]:
            comments = []
            if (self.xmlelement is not None):
                prevSibling = self.xmlelement.getprevious()
                while ((prevSibling is not None) and (prevSibling.tag is etree.Comment)):
                    comments.insert(0, prevSibling.text)
                    prevSibling = prevSibling.getprevious()

            return u'\n'.join(comments)
        else:
            return super(AndroidResourceUnit, self).getnotes(origin)

    def removenotes(self):
        if ((self.xmlelement is not None) and (self.xmlelement.getparent is not None)):
            prevSibling = self.xmlelement.getprevious()
            while ((prevSibling is not None) and (prevSibling.tag is etree.Comment)):
                prevSibling.getparent().remove(prevSibling)
                prevSibling = self.xmlelement.getprevious()

        super(AndroidResourceUnit, self).removenotes()

    def __str__(self):
        return etree.tostring(self.xmlelement, pretty_print=True,
                              encoding='utf-8')

    def __eq__(self, other):
        return (str(self) == str(other))
    
    def hasplurals(self, thing):
        if isinstance(thing, multistring):
            return True
        elif isinstance(thing, list):
            return True
        return False



class AndroidResourceFile(lisa.LISAfile):
    """Class representing a Android resource file store."""
    UnitClass = AndroidResourceUnit
    Name = _("Android String Resource")
    Mimetypes = ["application/xml"]
    Extensions = ["xml"]
    rootNode = "resources"
    bodyNode = "resources"
    XMLskeleton = '''<?xml version="1.0" encoding="utf-8"?>
<resources></resources>'''

    def initbody(self):
        """Initialises self.body so it never needs to be retrieved from the
        XML again."""
        self.namespace = self.document.getroot().nsmap.get(None, None)
        self.body = self.document.getroot()

    def parse(self, xml):
        """Populates this object from the given xml string"""
        if not hasattr(self, 'filename'):
            self.filename = getattr(xml, 'name', '')
        if hasattr(xml, "read"):
            xml.seek(0)
            posrc = xml.read()
            xml = posrc
        if etree.LXML_VERSION >= (2, 1, 0):
            #Since version 2.1.0 we can pass the strip_cdata parameter to
            #indicate that we don't want cdata to be converted to raw XML
            parser = etree.XMLParser(strip_cdata=False)
        else:
            parser = etree.XMLParser()
        self.document = etree.fromstring(xml, parser).getroottree()
        self._encoding = self.document.docinfo.encoding
        self.initbody()
        assert self.document.getroot().tag == self.namespaced(self.rootNode)

        for entry in self.document.getroot().iterchildren():
            term = self.UnitClass.createfromxmlElement(entry)
            if term is not None:
                self.addunit(term, new=False)
            