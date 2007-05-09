#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005-2006 Zuza Software Foundation
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

"""Module for handling XLIFF files for translation.

The official recommendation is to use the extention .xlf for XLIFF files.
"""

from translate.storage import base
from translate.storage import lisa

# TODO: handle translation types

class xliffunit(lisa.LISAunit):
    """A single term in the xliff file."""

    rootNode = "trans-unit"
    languageNode = "source"
    textNode = ""

    #TODO: id and all the trans-unit level stuff

    def createlanguageNode(self, lang, text, purpose):
        """Returns an xml Element setup with given parameters."""

        #TODO: for now we do source, but we have to test if it is target, perhaps 
        # with parameter. Alternatively, we can use lang, if supplied, since an xliff 
        #file has to conform to the bilingual nature promised by the header.
        assert purpose
        langset = self.document.createElement(purpose)
        #TODO: check language
#        langset.setAttribute("xml:lang", lang)

#        message = self.document.createTextNode(text)
#        langset.appendChild(message)
        self.createPHnodes(langset, text)
        return langset
    
    def getlanguageNodes(self):
        """We override this to get source and target nodes."""

        sources = self.xmlelement.getElementsByTagName(self.languageNode)
        targets = self.xmlelement.getElementsByTagName("target")
        sourcesl = len(sources)
        targetsl = len(targets)
        nodes = []
        for pair in zip(sources, targets):
            nodes.extend(list(pair))
        if sourcesl > targetsl:
            nodes.extend(sources[- (sourcesl - targetsl):])
        return nodes

    def addalttrans(self, txt, origin=None, lang=None):
        """Adds an alt-trans tag and alt-trans components to the unit.
        
        @type txt: String
        @param txt: Alternative translation of the source text.
        """

        #TODO: support adding a source tag ad match quality attribute.  At 
        # the source tag is needed to inject fuzzy matches from a TM.
        if isinstance(txt, str):
            txt = txt.decode("utf-8")
        alttarget = self.document.createElement("target")
        alttarget.appendChild(self.document.createTextNode(txt))
        alttrans = self.document.createElement("alt-trans")
        alttrans.appendChild(alttarget)
        if origin:
            alttrans.setAttribute("origin", origin)
        if lang:
            alttrans.setAttribute("xml:lang", lang)
        self.xmlelement.appendChild(alttrans)

    def getalttrans(self, origin=None):
        """Returns <alt-trans> for the given origin as a list of units. No 
        origin means all alternatives."""
        nodes = self.xmlelement.getElementsByTagName("alt-trans")
        translist = []
        for i in range(len(nodes)):
            if self.correctorigin(nodes[i], origin):
                # We build some mini units that keep the xmlelement. This 
                # makes it easier to delete it if it is passed back to us.
                newunit = base.TranslationUnit(self.source)
                node = nodes[i]

                # the source tag is optional
                sourcelist = node.getElementsByTagName("source")
                if sourcelist:
                    newunit.source = lisa.getText(sourcelist[0])

                # must have one or more targets
                targetlist = node.getElementsByTagName("target")
                newunit.target = lisa.getText(targetlist[0])
                #TODO: support multiple targets better
                #TODO: support notes in alt-trans
                newunit.xmlelement = node

                translist.append(newunit)
        return translist

    def delalttrans(self, alternative):
        """Removes the supplied alternative from the list of alt-trans tags"""
        self.xmlelement.removeChild(alternative.xmlelement)

    def addnote(self, text, origin=None):
        """Add a note specifically in a "note" tag"""
        if isinstance(text, str):
            text = text.decode("utf-8")
        note = self.document.createElement("note")
        note.appendChild(self.document.createTextNode(text))
        if origin:
            note.setAttribute("from", origin)
        self.xmlelement.appendChild(note)        

    def getnotelist(self, origin=None):
        """Private method that returns the text from notes matching 'origin' or all notes."""
        notenodes = self.xmlelement.getElementsByTagName("note")
        initial_list = [lisa.getText(note) for note in notenodes if self.correctorigin(note, origin)]

        # Remove duplicate entries from list:
        dictset = {}
        notelist = [dictset.setdefault(note, note) for note in initial_list if note not in dictset]

        return notelist 

    def getnotes(self, origin=None):
        return '\n'.join(self.getnotelist(origin=origin)) 

    def removenotes(self):
        """Remove all the translator notes."""
        notes = self.xmlelement.getElementsByTagName("note")
        for note in notes:
            if self.correctorigin(note, origin="translator"):
                self.xmlelement.removeChild(note)

    def adderror(self, errorname, errortext):
        """Adds an error message to this unit."""
        text = errorname + ': ' + errortext
        self.addnote(text, origin="pofilter")

    def geterrors(self):
        """Get all error messages."""
        notelist = self.getnotelist(origin="pofilter")
        errordict = {}
        for note in notelist:
            errorname, errortext = note.split(': ')
            errordict[errorname] = errortext
        return errordict

    def isapproved(self):
        """States whether this unit is approved"""
        return self.xmlelement.getAttribute("approved") == "yes"

    def isreview(self):
        """States whether this unit needs to be reviewed"""
        targetnode = self.getlanguageNode(lang=None, index=1)
        return not targetnode is None and \
                "needs-review" in targetnode.getAttribute("state")

    def markreviewneeded(self, needsreview=True, explanation=None):
        """Marks the unit to indicate whether it needs review. Adds an optional explanation as a note."""
        targetnode = self.getlanguageNode(lang=None, index=1)
        if targetnode:
            if needsreview:
                targetnode.setAttribute("state", "needs-review-translation")
                if explanation:
                    self.addnote(explanation, origin="translator")
            else:
                targetnode.removeAttribute("state")

    def isfuzzy(self):
#        targetnode = self.getlanguageNode(lang=None, index=1)
#        return not targetnode is None and \
#                (targetnode.getAttribute("state-qualifier") == "fuzzy-match" or \
#                targetnode.getAttribute("state") == "needs-review-translation")
        return not self.isapproved()
                
    def markfuzzy(self, value=True):
        if value:
            self.xmlelement.setAttribute("approved", "no")
        else:
            self.xmlelement.setAttribute("approved", "yes")
        targetnode = self.getlanguageNode(lang=None, index=1)
        if targetnode:
            if value:
                targetnode.setAttribute("state", "needs-review-translation")
            else:
                for attribute in ["state", "state-qualifier"]:
                    if targetnode.hasAttribute(attribute):
                        targetnode.removeAttribute(attribute)

    def settarget(self, text, lang='xx', append=False):
        """Sets the target string to the given value."""
        super(xliffunit, self).settarget(text, lang, append)
        if text:
            self.marktranslated()

# This code is commented while this will almost always return false.
# This way pocount, etc. works well.
#    def istranslated(self):
#        targetnode = self.getlanguageNode(lang=None, index=1)
#        return not targetnode is None and \
#                (targetnode.getAttribute("state") == "translated")

    def marktranslated(self):
        targetnode = self.getlanguageNode(lang=None, index=1)
        if not targetnode:
            return
        if self.isfuzzy() and targetnode.hasAttribute("state-qualifier"):
            #TODO: consider
            targetnode.removeAttribute("state-qualifier")
        targetnode.setAttribute("state", "translated")

    def setid(self, id):
        self.xmlelement.setAttribute("id", id)

    def getid(self):
        return self.xmlelement.getAttribute("id")

    def getlocations(self):
        return [self.getid()]

    def createcontextgroup(self, name, contexts=None, purpose=None):
        """Add the context group to the trans-unit with contexts a list with
        (type, text) tuples describing each context."""
        assert contexts
        group = self.document.createElement("context-group")
        group.setAttribute("name", name)
        if purpose:
            group.setAttribute("purpose", purpose)
        for type, text in contexts:
            if isinstance(text, str):
                text = text.decode("utf-8")
            context = self.document.createElement("context")
            context.setAttribute("context-type", type)
            nodetext = self.document.createTextNode(text)
            context.appendChild(nodetext)
            group.appendChild(context)
        self.xmlelement.appendChild(group)

    def getcontextgroups(self, name):
        """Returns the contexts in the context groups with the specified name"""
        groups = []
        grouptags = self.xmlelement.getElementsByTagName("context-group")
        for group in grouptags:
            if group.getAttribute("name") == name:
                contexts = group.getElementsByTagName("context")
                pairs = []
                for context in contexts:
                    pairs.append((context.getAttribute("context-type"), lisa.getText(context)))
                groups.append(pairs) #not extend
        return groups
        
    def getrestype(self):
        """returns the restype attribute in the trans-unit tag"""
        return self.xmlelement.getAttribute("restype")

    def merge(self, otherunit, overwrite=False, comments=True):
        #TODO: consider other attributes like "approved"
        super(xliffunit, self).merge(otherunit, overwrite, comments)
        if self.target:
            self.marktranslated()
        if otherunit.isfuzzy():
            self.markfuzzy()

    def correctorigin(self, node, origin):
        """Check against node tag's origin (e.g note or alt-trans)"""
        if origin == None:
            return True
        elif origin in node.getAttribute("from"):
            return True
        elif origin in node.getAttribute("origin"):
            return True
        else:
            return False

class xlifffile(lisa.LISAfile):
    """Class representing a XLIFF file store."""
    UnitClass = xliffunit
    rootNode = "xliff"
    bodyNode = "body"
    XMLskeleton = '''<?xml version="1.0" ?>
<xliff version='1.1' xmlns='urn:oasis:names:tc:xliff:document:1.1'>
 <file original='NoName' source-language='en' datatype='plaintext'>
  <body>
  </body>
 </file>
</xliff>'''

    def __init__(self,*args,**kwargs):
        lisa.LISAfile.__init__(self,*args,**kwargs)
        self._filename = "NoName"
        self._messagenum = 0

        # Allow the inputfile to override defaults for source and target language.
        filenode = self.document.getElementsByTagName('file')[0]
        sourcelanguage = filenode.getAttribute('source-language')
        if sourcelanguage:
            self.setsourcelanguage(sourcelanguage)
        targetlanguage = filenode.getAttribute('target-language')
        if targetlanguage:
            self.settargetlanguage(targetlanguage)

    def addheader(self):
        """Initialise the file header."""
        self.document.getElementsByTagName("file")[0].setAttribute("source-language", self.sourcelanguage)
        if self.targetlanguage:
            self.document.getElementsByTagName("file")[0].setAttribute("target-language", self.targetlanguage)

    def createfilenode(self, filename, sourcelanguage=None, targetlanguage=None, datatype='plaintext'):
        """creates a filenode with the given filename. All parameters are needed
        for XLIFF compliance."""
        self.removedefaultfile()
        if sourcelanguage is None:
            sourcelanguage = self.sourcelanguage
        if targetlanguage is None:
            targetlanguage = self.targetlanguage
        filenode = self.document.createElement("file")
        filenode.setAttribute("original", filename)
        filenode.setAttribute("source-language", sourcelanguage)
        if targetlanguage:
            filenode.setAttribute("target-language", targetlanguage)
        filenode.setAttribute("datatype", datatype)
        bodyNode = self.document.createElement(self.bodyNode)
        filenode.appendChild(bodyNode)
        return filenode

    def getfilename(self, filenode):
        """returns the name of the given file"""
        return filenode.getAttribute("original")

    def getfilenames(self):
        """returns all filenames in this XLIFF file"""
        filenodes = self.document.getElementsByTagName("file")
        filenames = [self.getfilename(filenode) for filenode in filenodes]
        if len(filenames) == 1 and filenames[0] == '':
            filenames = []
        return filenames

    def getfilenode(self, filename):
        """finds the filenode with the given name"""
        filenodes = self.document.getElementsByTagName("file")
        for filenode in filenodes:
            if self.getfilename(filenode) == filename:
                return filenode
        return None

    def getdatatype(self, filename=None):
        """Returns the datatype of the stored file. If no filename is given,
        the datatype of the first file is given."""
        if filename:
            node = self.getfilenode(filename)
            if node:
                return node.getAttribute("datatype")
        else:
            filenames = self.getfilenames()
            if len(filenames) > 0 and filenames[0] != "NoName":
                return self.getdatatype(filenames[0])
        return ""

    def removedefaultfile(self):
        """We want to remove the default file-tag as soon as possible if we 
        know if still present and empty."""
        filenodes = self.document.getElementsByTagName("file")
        if len(filenodes) > 1:
            for filenode in filenodes:
                if filenode.getAttribute("original") == "NoName" and \
                        not filenode.getElementsByTagName(self.UnitClass.rootNode):
                    self.document.documentElement.removeChild(filenode)
                break

    def getheadernode(self, filenode, createifmissing=False):
        """finds the header node for the given filenode"""
        # TODO: Deprecated?
        headernodes = list(filenode.getElementsByTagName("header"))
        if headernodes:
            return headernodes[0]
        if not createifmissing:
            return None
        headernode = ourdom.Element("header")
        filenode.appendChild(headernode)
        return headernode

    def getbodynode(self, filenode, createifmissing=False):
        """finds the body node for the given filenode"""
        bodynodes = list(filenode.getElementsByTagName("body"))
        if bodynodes:
            return bodynodes[0]
        if not createifmissing:
            return None
        bodynode = self.document.createElement("body")
        filenode.appendChild(bodynode)
        return bodynode

    def addsourceunit(self, source, filename="NoName", createifmissing=False):
        """adds the given trans-unit to the last used body node if the filename has changed it uses the slow method instead (will create the nodes required if asked). Returns success"""
        if self._filename != filename:
            if not self.switchfile(filename, createifmissing):
              return None
        unit = super(xlifffile, self).addsourceunit(source)
        self._messagenum += 1
        unit.setid("%d" % self._messagenum)
        unit.xmlelement.setAttribute("xml:space", "preserve")
        return unit

    def switchfile(self, filename, createifmissing=False):
        """adds the given trans-unit (will create the nodes required if asked). Returns success"""
        self._filename = filename
        filenode = self.getfilenode(filename)
        if filenode is None:
            if not createifmissing:
                return False
            filenode = self.createfilenode(filename)
            self.document.documentElement.appendChild(filenode)

        self.body = self.getbodynode(filenode, createifmissing=createifmissing)
        if self.body is None:
            return False
        self._messagenum = len(list(self.body.getElementsByTagName("trans-unit")))
        #TODO: was 0 based before - consider
    #    messagenum = len(self.units)
        #TODO: we want to number them consecutively inside a body/file tag
        #instead of globally in the whole XLIFF file, but using len(self.units)
        #will be much faster
        return True
    
    def creategroup(self, filename="NoName", createifmissing=False, restype=None):
        """adds a group tag into the specified file"""
        if self._filename != filename:
            if not self.switchfile(filename, createifmissing):
              return None
        group = self.document.createElement("group")
        if restype:
            group.setAttribute("restype", restype)
        self.body.appendChild(group)
        return group
        
    def __str__(self):
        self.removedefaultfile()
        return super(xlifffile, self).__str__()

    def parsestring(cls, storestring):
        """Parses the string to return the correct file object"""
        xliff = super(xlifffile, cls).parsestring(storestring)
        if xliff.units:
            header = xliff.units[0]
            if ("gettext-domain-header" in header.getrestype() or xliff.getdatatype() == "po") \
                    and cls.__name__.lower() != "poxlifffile":
                import poxliff
                xliff = poxliff.PoXliffFile.parsestring(storestring)
        return xliff
    parsestring = classmethod(parsestring)

