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

"""module for parsing .xliff files for translation"""

from translate.storage import lisa
from xml.dom import minidom

def writexml(self, writer, indent="", addindent="", newl=""):
    """a replacement to writexml that formats it more like typical .ts files"""
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 and self.childNodes[0].nodeType == self.TEXT_NODE:
          writer.write(">")
          for node in self.childNodes:
              node.writexml(writer,"","","")
          writer.write("</%s>%s" % (self.tagName,newl))
        else:
          writer.write(">%s"%(newl))
          for node in self.childNodes:
              node.writexml(writer,indent+addindent,addindent,newl)
          writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))

# commented out modifications to minidom classes
'''
Element_writexml = minidom.Element.writexml
for elementclassname in dir(minidom):
  elementclass = getattr(minidom, elementclassname)
  if not isinstance(elementclass, type(minidom.Element)):
    continue
  if not issubclass(elementclass, minidom.Element):
    continue
  if elementclass.writexml != Element_writexml:
    continue
  elementclass.writexml = writexml
'''

# TODO: handle translation types

class xliffunit(lisa.LISAunit):
    """A single term in the xliff file.""" 
    rootNode = "trans-unit"
    languageNode = "source"
    textNode = ""

    #TODO: id and all the trans-unit level stuff

    def createlanguageNode(self, lang, text, purpose):
        """returns an xml Element setup with given parameters"""
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
        """Adds a alt-trans tag and alt-trans components to <source>"""
        if isinstance(txt, str):
            txt = txt.decode("utf-8")
        alttrans = self.document.createElement("alt-trans")
        alttrans.appendChild(self.document.createTextNode(txt))
        if origin:
            alttrans.setAttribute("origin", origin)
        if lang:
            alttrans.setAttribute("xml:lang", lang)
        self.xmlelement.appendChild(alttrans)

    def getalttrans(self, origin=None):
        """Returns <alt-trans> for source as a list"""
        nodes = self.xmlelement.getElementsByTagName("alt-trans")
        translist = []
        if not origin:
            for i in range(len(nodes)):
                translist.append(lisa.getText(nodes[i]))
        else:
            for i in range(len(nodes)):
                if self.correctorigin(nodes[i], origin):
                    translist.append(lisa.getText(nodes[i]))
        return translist

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
        """Returns the text from notes matching 'origin' or all notes"""
        notenodes = self.xmlelement.getElementsByTagName("note")
        initial_list = [lisa.getText(note) for note in notenodes if self.correctorigin(note, origin)]

        # Remove duplicate entries from list:
        dictset = {}
        notelist = [dictset.setdefault(note, note) for note in initial_list if note not in dictset]

        return notelist 

    def getnotes(self, origin=None):
        return '\n'.join(self.getnotelist(origin=origin)) 

    def removenotes(self):
        """Remove all the notes"""
        # TODO: Do we really want to remove all the notes?
        notes = self.xmlelement.getElementsByTagName("note")
        for i in range(len(notes)):
            self.xmlelement.removeChild(notes[i])    
 
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
        targetnode = self.getlanguageNode(lang=None, index=1)
        return not targetnode is None and \
                (targetnode.getAttribute("state-qualifier") == "fuzzy-match" or \
                targetnode.getAttribute("state") == "needs-review-translation")
                
    def markfuzzy(self, value=True):
        targetnode = self.getlanguageNode(lang=None, index=1)
        if targetnode:
            if value:
                targetnode.setAttribute("state", "needs-review-translation")
                targetnode.setAttribute("state-qualifier", "fuzzy-match")
            elif self.isfuzzy():                
                targetnode.removeAttribute("state")
                targetnode.removeAttribute("state-qualifier")
        elif value:
            #If there is no target, we can't really indicate fuzzyness, so we set
            #approved to "no", but we don't take it into account in isfuzzy()
            #TODO: review decision
            self.xmlelement.setAttribute("approved", "no")

    def istranslated(self):
        targetnode = self.getlanguageNode(lang=None, index=1)
        return not targetnode is None and \
                (targetnode.getAttribute("state") == "translated")

    def marktranslated(self):
        targetnode = self.getlanguageNode(lang=None, index=1)
        if not targetnode:
            return
        if self.isfuzzy():
            #TODO: consider
            targetnode.removeAttribute("state-qualifier")
        targetnode.setAttribute("state", "translated")

    def setid(self, id):
        self.xmlelement.setAttribute("id", id)

    def getid(self):
        return self.xmlelement.getAttribute("id")

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

    def addheader(self):
        """Initialise the file header."""
        self.document.getElementsByTagName("file")[0].setAttribute("source-language", self.sourcelanguage)
        if self.targetlanguage:
            self.document.getElementsByTagName("file")[0].setAttribute("target-language", self.targetlanguage)

    def createfilenode(self, filename, sourcelanguage=None, datatype='plaintext'):
        """creates a filenode with the given filename. All parameters are needed
        for XLIFF compliance."""
        self.removedefaultfile()
        if sourcelanguage is None:
            sourcelanguage = self.sourcelanguage
        filenode = self.document.createElement("file")
        filenode.setAttribute("original", filename)
        filenode.setAttribute("source-language", sourcelanguage)
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
        return [self.getfilename(filenode) for filenode in filenodes]

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
        #Deprecated?
        headernodes = list(filenode.getElementsByTagName("header"))
        if headernodes:
            return headernodes[0]
        if not createifmissing:
            return None
        headernode = minidom.Element("header")
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

    def parsefile(cls, storefile):
        """Normal parsing, but if it smells like a PO-XLIFF, rather hand over to poxliff."""
        if isinstance(storefile, basestring):
            storefile = open(storefile, "r")
        storestring = storefile.read()
        return xlifffile.parsestring(storestring)

    parsefile = classmethod(parsefile)

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

