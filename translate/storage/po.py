#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2002-2007 Zuza Software Foundation
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

"""classes that hold units of .po files (pounit) or entire files (pofile)
gettext-style .po (or .pot) files are used in translations for KDE et al (see kbabel)"""

from __future__ import generators
from translate.misc.multistring import multistring
from translate.misc import quote
from translate.misc import textwrap
from translate.storage import base
from translate.storage import poheader
import re
import codecs

# general functions for quoting / unquoting po strings

po_unescape_map = {"\\r": "\r", "\\t": "\t", '\\"': '"', '\\n': '\n', '\\\\': '\\'}
po_escape_map = dict([(value, key) for (key, value) in po_unescape_map.items()])

def escapeforpo(line):
  """Escapes a line for po format. assumes no \n occurs in the line.
  
  @param line: unescaped text
  """
  special_locations = []
  for special_key in po_escape_map:
    special_locations.extend(quote.find_all(line, special_key))
  special_locations = dict.fromkeys(special_locations).keys()
  special_locations.sort()
  escaped_line = ""
  last_location = 0
  for location in special_locations:
    escaped_line += line[last_location:location]
    escaped_line += po_escape_map[line[location:location+1]]
    last_location = location+1
  escaped_line += line[last_location:]
  return escaped_line

def unescapehandler(escape):

  return po_unescape_map.get(escape, escape)

def wrapline(line):
    """Wrap text for po files."""
    wrappedlines = textwrap.wrap(line, 76, replace_whitespace=False, expand_tabs=False, drop_whitespace=False)

    # Lines should not start with a space...
    if len(wrappedlines) > 1:
        for index, line in enumerate(wrappedlines[1:]):
            if line.startswith(' '):
                # Remove the space at the beginning of the line:
                wrappedlines[index+1] = line[1:]

                # Append a space to the previous line:
                wrappedlines[index] += ' '
    return wrappedlines

def quoteforpo(text):
  """quotes the given text for a PO file, returning quoted and escaped lines"""
  polines = []
  if text is None:
    return polines
  lines = text.split("\n")
  if len(lines) > 1 or (len(lines) == 1 and len(lines[0]) > 71):
    if len(lines) != 2 or lines[1]:
        polines.extend(['""'])
    for line in lines[:-1]:
      lns = wrapline(line)
      if len(lns) > 0:
        for ln in lns[:-1]:
          polines.extend(['"' + escapeforpo(ln) + '"'])
        if lns[-1]:
          polines.extend(['"' + escapeforpo(lns[-1]) + '\\n"'])
      else:
        polines.extend(['"\\n"'])
  if lines[-1]:
    polines.extend(['"' + escapeforpo(line) + '"' for line in wrapline(lines[-1])])
  return polines

def extractpoline(line):
  """Remove quote and unescape line from po file.
   
  @param line: a quoted line from a po file (msgid or msgstr)
  """
  extracted = quote.extractwithoutquotes(line,'"','"','\\',includeescapes=unescapehandler)[0]
  return extracted

def unquotefrompo(postr, joinwithlinebreak=False):
  if joinwithlinebreak:
    joiner = "\n"
    if postr and postr[0] == '""': postr = postr[1:]
  else:
    joiner = ""
  return joiner.join([extractpoline(line) for line in postr])

def encodingToUse(encoding):
  """Tests whether the given encoding is known in the python runtime, or returns utf-8.
  This function is used to ensure that a valid encoding is always used."""
  if encoding == "CHARSET" or encoding == None: return 'utf-8'
  return encoding
#  if encoding is None: return False
#  return True
#  try:
#    tuple = codecs.lookup(encoding)
#  except LookupError:
#    return False
#  return True

"""
From the GNU gettext manual:
     WHITE-SPACE
     #  TRANSLATOR-COMMENTS
     #. AUTOMATIC-COMMENTS
     #| PREVIOUS MSGID                 (Gettext 0.16 - check if this is the correct position - not yet implemented)
     #: REFERENCE...
     #, FLAG...
     msgctxt CONTEXT                   (Gettext 0.15)
     msgid UNTRANSLATED-STRING
     msgstr TRANSLATED-STRING
"""

class pounit(base.TranslationUnit):
  # othercomments = []      #   # this is another comment
  # automaticcomments = []  #   #. comment extracted from the source code
  # sourcecomments = []     #   #: sourcefile.xxx:35
  # typecomments = []       #   #, fuzzy
  # visiblecomments = []    #   #_ note to translator  (this is nonsense)
  # msgidcomments = []      #   _: within msgid
  # msgctxt
  # msgid = []
  # msgstr = []

  def __init__(self, source=None, encoding="UTF-8"):
    self.encoding = encodingToUse(encoding)
    self.obsolete = False
    self.initallcomments(blankall=True)
    self.msgctxt = []
    self.msgid = []
    self.msgid_pluralcomments = []
    self.msgid_plural = []
    self.msgstr = []
    self.obsoletemsgctxt = []
    self.obsoletemsgid = []
    self.obsoletemsgid_pluralcomments = []
    self.obsoletemsgid_plural = []
    self.obsoletemsgstr = []
    if source:
      self.setsource(source)
    super(pounit, self).__init__(source)

  def initallcomments(self, blankall=False):
    """Initialises allcomments"""
    if blankall:
      self.othercomments = []
      self.automaticcomments = []
      self.sourcecomments = []
      self.typecomments = []
      self.visiblecomments = []
      self.msgidcomments = []
      self.obsoletemsgidcomments = []
    self.allcomments = [self.othercomments, 
                        self.automaticcomments, 
                        self.sourcecomments, 
                        self.typecomments, 
                        self.visiblecomments, 
                        self.msgidcomments,
                        self.obsoletemsgidcomments]

  def getsource(self):
    """Returns the unescaped msgid"""
    multi = multistring(unquotefrompo(self.msgid), self.encoding)
    if self.hasplural():
      pluralform = unquotefrompo(self.msgid_plural)
      if isinstance(pluralform, str):
          pluralform = pluralform.decode(self.encoding)
      multi.strings.append(pluralform)
    return multi

  def setsource(self, source):
    """Sets the msgid to the given (unescaped) value.
    
    @param source: an unescaped source string.
    """
    if isinstance(source, str):
      source = source.decode(self.encoding)
    if isinstance(source, multistring):
      source = source.strings
    if isinstance(source, list):
      self.msgid = quoteforpo(source[0])
      if len(source) > 1:
        self.msgid_plural = quoteforpo(source[1])
    else:
      self.msgid = quoteforpo(source)
  source = property(getsource, setsource)

  def gettarget(self):
    """Returns the unescaped msgstr"""
    if isinstance(self.msgstr, dict):
      multi = multistring(map(unquotefrompo, self.msgstr.values()), self.encoding)
    else:
      multi = multistring(unquotefrompo(self.msgstr), self.encoding)
    return multi

  def settarget(self, target):
    """Sets the msgstr to the given (unescaped) value"""
    if isinstance(target, str):
      target = target.decode(self.encoding)
    if target == self.target:
      return
    if self.hasplural():
      if isinstance(target, multistring):
        target = target.strings
      elif isinstance(target, basestring):
        target = [target]
    elif isinstance(target,(dict, list)):
      if len(target) == 1:
        target = target[0]
      else:
        raise ValueError("po msgid element has no plural but msgstr has %d elements (%s)" % (len(target), target))
    templates = self.msgstr
    if isinstance(templates, list):
      templates = {0: templates}
    if isinstance(target, list):
      self.msgstr = dict([(i, quoteforpo(target[i])) for i in range(len(target))])
    elif isinstance(target, dict):
      self.msgstr = dict([(i, quoteforpo(targetstring)) for i, targetstring in target.iteritems()])
    else:
      self.msgstr = quoteforpo(target)
  target = property(gettarget, settarget)

  def getnotes(self, origin=None):
    """Return comments based on origin value (programmer, developer, source code and translator)"""
    if origin == None:
      comments = "".join([comment[2:] for comment in self.othercomments])
      comments += "".join([comment[3:] for comment in self.automaticcomments])
    elif origin == "translator":
      comments = "".join ([comment[2:] for comment in self.othercomments])
    elif origin in ["programmer", "developer", "source code"]:
      comments = "".join([comment[3:] for comment in self.automaticcomments])
    else:
      raise ValueError("Comment type not valid")
    # Let's drop the last newline
    return comments[:-1]

  def addnote(self, text, origin=None, position="append"):
    """This is modeled on the XLIFF method. See xliff.py::xliffunit.addnote"""
    # We don't want to put in an empty '#' without a real comment:
    if not text:
      return
    commentlist = self.othercomments
    linestart = "# "
    if origin in ["programmer", "developer", "source code"]:
      autocomments = True
      commentlist = self.automaticcomments
      linestart = "#. "
    text = text.split("\n")
    if position == "append":
      commentlist += [linestart + line + "\n" for line in text]
    else:
      newcomments = [linestart + line + "\n" for line in text]
      newcomments += [line for line in commentlist]
      if autocomments:
        self.automaticcomments = newcomments
      else:
        self.othercomments = newcomments
    
  def removenotes(self):
    """Remove all the translator's notes (other comments)"""
    self.othercomments = []

  def adderror(self, errorname, errortext):
    """Adds an error message to this unit."""
    text = u'(pofilter) %s: %s' % (errorname, errortext)
    # Don't add the same error twice:
    if text not in self.getnotes(origin='translator'):
        self.addnote(text, origin="translator")

  def geterrors(self):
    """Get all error messages."""
    notes = self.getnotes(origin="translator").split('\n')
    errordict = {}
    for note in notes:
      if '(pofilter) ' in note:
        error = note.replace('(pofilter) ', '')
        errorname, errortext = error.split(': ')
        errordict[errorname] = errortext
    return errordict

  def copy(self):
    newpo = self.__class__()
    newpo.othercomments = self.othercomments[:]
    newpo.automaticcomments = self.automaticcomments[:]
    newpo.sourcecomments = self.sourcecomments[:]
    newpo.typecomments = self.typecomments[:]
    newpo.visiblecomments = self.visiblecomments[:]
    newpo.obsolete = self.obsolete
    newpo.msgidcomments = self.msgidcomments[:]
    newpo.initallcomments()
    newpo.msgctxt = self.msgctxt[:]
    newpo.msgid = self.msgid[:]
    newpo.msgid_pluralcomments = self.msgid_pluralcomments[:]
    newpo.msgid_plural = self.msgid_plural[:]
    if isinstance(self.msgstr, dict):
      newpo.msgstr = self.msgstr.copy()
    else:
      newpo.msgstr = self.msgstr[:]
      
    newpo.obsoletemsgctxt = self.obsoletemsgctxt[:]
    newpo.obsoletemsgid = self.obsoletemsgid[:]
    newpo.obsoletemsgid_pluralcomments = self.obsoletemsgid_pluralcomments[:]
    newpo.obsoletemsgid_plural = self.obsoletemsgid_plural[:]
    if isinstance(self.obsoletemsgstr, dict):
      newpo.obsoletemsgstr = self.obsoletemsgstr.copy()
    else:
      newpo.obsoletemsgstr = self.obsoletemsgstr[:]
    return newpo

  def msgidlen(self):
    if self.hasplural():
      return len(unquotefrompo(self.msgid).strip()) + len(unquotefrompo(self.msgid_plural).strip())
    else:
      return len(unquotefrompo(self.msgid).strip())

  def msgstrlen(self):
    if isinstance(self.msgstr, dict):
      combinedstr = "\n".join([unquotefrompo(msgstr).strip() for msgstr in self.msgstr.itervalues()])
      return len(combinedstr.strip())
    else:
      return len(unquotefrompo(self.msgstr).strip())

  def merge(self, otherpo, overwrite=False, comments=True, authoritative=False):
    """Merges the otherpo (with the same msgid) into this one.

    Overwrite non-blank self.msgstr only if overwrite is True
    merge comments only if comments is True
    
    """

    def mergelists(list1, list2, split=False):
      #decode where necessary
      if unicode in [type(item) for item in list2] + [type(item) for item in list1]:
        for position, item in enumerate(list1):
          if isinstance(item, str):
            list1[position] = item.decode("utf-8")
        for position, item in enumerate(list2):
          if isinstance(item, str):
            list2[position] = item.decode("utf-8")
            
      #Determine the newline style of list1
      lineend = ""
      if list1 and list1[0]:
        for candidate in ["\n", "\r", "\n\r"]:
          if list1[0].endswith(candidate):
            lineend = candidate
        if not lineend:
          lineend = ""
      else:
        lineend = "\n"
      
      #Split if directed to do so:    
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
        list1.extend(["%s %s%s" % (prefix,item,lineend) for item in splitlist2 if not item in splitlist1])
      else:
        #Normal merge, but conform to list1 newline style
        for item in list2:
          if lineend:
            item = item.rstrip() + lineend
          if item not in list1:
            list1.append(item)
    if not isinstance(otherpo, pounit):
      super(pounit, self).merge(otherpo, overwrite, comments)
      return
    if comments:
      mergelists(self.othercomments, otherpo.othercomments)
      mergelists(self.typecomments, otherpo.typecomments)
      mergelists(self.visiblecomments, otherpo.visiblecomments)
      if not authoritative:
        # We don't bring across otherpo.automaticcomments as we consider ourself
        # to be the the authority.  Same applies to otherpo.msgidcomments
        mergelists(self.automaticcomments, otherpo.automaticcomments)
        mergelists(self.msgidcomments, otherpo.msgidcomments)
        mergelists(self.sourcecomments, otherpo.sourcecomments, split=True)
    if self.isblankmsgstr() or overwrite:
      # Remove kde-style comments from the translation (if any).
      if self.extract_msgidcomments(otherpo.target):
        otherpo.target = otherpo.target.replace('_: ' + otherpo.extract_msgidcomments()+ '\n', '')
      self.target = otherpo.target
      if self.source != otherpo.source:
        self.markfuzzy()
      else:
        self.markfuzzy(otherpo.isfuzzy())
    elif otherpo.isblankmsgstr():
      if self.source != otherpo.source:
        self.markfuzzy()
    else:
      if self.target != otherpo.target:
        self.markfuzzy()

  def isheader(self):
    #return (self.msgidlen() == 0) and (self.msgstrlen() > 0) and (len(self.msgidcomments) == 0)
    #rewritten here for performance:
    return ((self.msgid == [] or self.msgid == ['""']) and 
            not (self.msgstr == [] or self.msgstr == ['""']) 
            and self.msgidcomments == [])

  def isblank(self):
    if self.isheader() or len(self.msgidcomments):
      return False
    if (self.msgidlen() == 0) and (self.msgstrlen() == 0):
      return True
    return False
    # TODO: remove:
    # Before, the equivalent of the following was the final return statement:
    # return len(self.source.strip()) == 0

  def isblankmsgstr(self):
    """checks whether the msgstr is blank"""
    return self.msgstrlen() == 0

  def hastypecomment(self, typecomment):
    """check whether the given type comment is present"""
    # check for word boundaries properly by using a regular expression...
    return sum(map(lambda tcline: len(re.findall("\\b%s\\b" % typecomment, tcline)), self.typecomments)) != 0

  def hasmarkedcomment(self, commentmarker):
    """check whether the given comment marker is present as # (commentmarker) ..."""
    commentmarker = "(%s)" % commentmarker
    for comment in self.othercomments:
      if comment.replace("#", "", 1).strip().startswith(commentmarker):
        return True
    return False

  def settypecomment(self, typecomment, present=True):
    """alters whether a given typecomment is present"""
    if self.hastypecomment(typecomment) != present:
      if present:
        self.typecomments.append("#, %s\n" % typecomment)
      else:
        # this should handle word boundaries properly ...
        typecomments = map(lambda tcline: re.sub("\\b%s\\b[ \t,]*" % typecomment, "", tcline), self.typecomments)
        self.typecomments = filter(lambda tcline: tcline.strip() != "#,", typecomments)

  def istranslated(self):
    return super(pounit, self).istranslated() and not self.isobsolete()

  def istranslatable(self):
    return not (self.isheader() or self.isblank())

  def isfuzzy(self):
    return self.hastypecomment("fuzzy")

  def markfuzzy(self, present=True):
    self.settypecomment("fuzzy", present)

  def isreview(self):
    return self.hastypecomment("review") or self.hasmarkedcomment("review") or self.hasmarkedcomment("pofilter")

  def markreviewneeded(self, needsreview=True, explanation=None):
    """Marks the unit to indicate whether it needs review. Adds an optional explanation as a note."""
    if needsreview:
      reviewnote = "(review)"
      if explanation:
        reviewnote += " " + explanation
      self.addnote(reviewnote, origin="translator")
    else:
      # Strip (review) notes.
      notestring = self.getnotes(origin="translator")
      notes = notestring.split('\n')
      newnotes = []
      for note in notes:
        if not '(review)' in note:
          newnotes.append(note)
      newnotes = '\n'.join(newnotes)
      self.removenotes()
      self.addnote(newnotes, origin="translator")
      
  def isobsolete(self):
    return self.obsolete

  def makeobsolete(self):
    """Makes this unit obsolete"""
    self.obsolete = True
    if self.msgctxt:
      self.obsoletemsgctxt = self.msgctxt
    if self.msgid:
      self.obsoletemsgid = self.msgid
      self.msgid = []
    if self.msgidcomments:
      self.obsoletemsgidcomments = self.msgidcomments
      self.msgidcomments = []
    if self.msgid_plural:
      self.obsoletemsgid_plural = self.msgid_plural
      self.msgid_plural = []
    if self.msgstr:
      self.obsoletemsgstr = self.msgstr
      self.msgstr = []
    self.sourcecomments = []
    self.automaticcomments = []

  def resurrect(self):
    """Makes an obsolete unit normal"""
    self.obsolete = False
    if self.obsoletemsgctxt:
      self.msgid = self.obsoletemsgctxt
      self.obsoletemsgctxt = []
    if self.obsoletemsgid:
      self.msgid = self.obsoletemsgid
      self.obsoletemsgid = []
    if self.obsoletemsgidcomments:
      self.msgidcomments = self.obsoletemsgidcomments
      self.obsoletemsgidcomments = []
    if self.obsoletemsgid_plural:
      self.msgid_plural = self.obsoletemsgid_plural
      self.obsoletemsgid_plural = []
    if self.obsoletemsgstr:
      self.msgstr = self.obsoletemsgstr
      self.obsoletemgstr = []

  def hasplural(self):
    """returns whether this pounit contains plural strings..."""
    return len(self.msgid_plural) > 0

  def parse(self, src):
    inmsgctxt = 0
    inmsgid = 0
    inmsgid_comment = 0
    inmsgid_plural = 0
    inmsgstr = 0
    msgstr_pluralid = None
    linesprocessed = 0
    for line in src.split("\n"):
      line = line + "\n"
      linesprocessed += 1
      if len(line) == 0:
        continue
      elif line[0] == '#':
        if inmsgstr and not line[1] == '~':
          # if we're already in the message string, this is from the next element
          break
        if line[1] == '.':
          self.automaticcomments.append(line)
        elif line[1] == ':':
          self.sourcecomments.append(line)
        elif line[1] == ',':
          self.typecomments.append(line)
        elif line[1] == '_':
          self.visiblecomments.append(line)
        elif line[1] == '~':
          line = line[3:]
          self.obsolete = True
        else:
          self.othercomments.append(line)
      if line.startswith('msgid_plural'):
        inmsgctxt = 0
        inmsgid = 0
        inmsgid_plural = 1
        inmsgstr = 0
        inmsgid_comment = 0
      elif line.startswith('msgctxt'):
        inmsgctxt = 1
        inmsgid = 0
        inmsgid_plural = 0
        inmsgstr = 0
        inmsgid_comment = 0
      elif line.startswith('msgid'):
        # if we just finished a msgstr or msgid_plural, there is probably an 
        # empty line missing between the units, so let's stop the parsing now.
        if inmsgstr or inmsgid_plural:
          break
        inmsgctxt = 0
        inmsgid = 1
        inmsgid_plural = 0
        inmsgstr = 0
        inmsgid_comment = 0
      elif line.startswith('msgstr'):
        inmsgctxt = 0
        inmsgid = 0
        inmsgid_plural = 0
        inmsgstr = 1
        if line.startswith('msgstr['):
          msgstr_pluralid = int(line[len('msgstr['):line.find(']')].strip())
        else:
          msgstr_pluralid = None
      extracted = quote.extractstr(line)
      if not extracted is None:
        if inmsgctxt:
          self.msgctxt.append(extracted)
        elif inmsgid:
          # TODO: improve kde comment detection
          if extracted.find("_:") != -1:
            inmsgid_comment = 1
          if inmsgid_comment:
            self.msgidcomments.append(extracted)
          else:
            self.msgid.append(extracted)
          if inmsgid_comment and extracted.find("\\n") != -1:
            inmsgid_comment = 0
        elif inmsgid_plural:
          if extracted.find("_:") != -1:
            inmsgid_comment = 1
          if inmsgid_comment:
            self.msgid_pluralcomments.append(extracted)
          else:
            self.msgid_plural.append(extracted)
          if inmsgid_comment and extracted.find("\\n") != -1:
            inmsgid_comment = 0
        elif inmsgstr:
          if msgstr_pluralid is None:
            self.msgstr.append(extracted)
          else:
            if type(self.msgstr) == list:
              self.msgstr = {0: self.msgstr}
            if msgstr_pluralid not in self.msgstr:
              self.msgstr[msgstr_pluralid] = []
            self.msgstr[msgstr_pluralid].append(extracted)
    if self.obsolete:
      self.makeobsolete()
    # If this unit is the header, we have to get the encoding to ensure that no
    # methods are called that need the encoding before we obtained it.
    if self.isheader():
      charset = re.search("charset=([^\\s]+)", unquotefrompo(self.msgstr))
      if charset:
        self.encoding = encodingToUse(charset.group(1))
    return linesprocessed

  def getmsgpartstr(self, partname, partlines, partcomments=""):
    if isinstance(partlines, dict):
      partkeys = partlines.keys()
      partkeys.sort()
      return "".join([self.getmsgpartstr("%s[%d]" % (partname, partkey), partlines[partkey], partcomments) for partkey in partkeys])
    partstr = partname + " "
    partstartline = 0
    if len(partlines) > 0 and len(partcomments) == 0:
      partstr += partlines[0]
      partstartline = 1
    elif len(partcomments) > 0:
      if len(partlines) > 0 and len(unquotefrompo(partlines[:1])) == 0:
        # if there is a blank leader line, it must come before the comment
        partstr += partlines[0] + '\n'
        # but if the whole string is blank, leave it in
        if len(partlines) > 1:
          partstartline += 1
      else:
        # All partcomments should start on a newline
        partstr += '""\n'
      # combine comments into one if more than one
      if len(partcomments) > 1:
        combinedcomment = []
        for comment in partcomments:
          comment = unquotefrompo([comment])
          if comment.startswith("_:"):
            comment = comment[len("_:"):]
          if comment.endswith("\\n"):
            comment = comment[:-len("\\n")]
          #Before we used to strip. Necessary in some cases?
          combinedcomment.append(comment)
        partcomments = quoteforpo("_:%s" % "".join(combinedcomment))
      # comments first, no blank leader line needed
      partstr += "\n".join(partcomments)
      partstr = quote.rstripeol(partstr)
    else:
      partstr += '""'
    partstr += '\n'
    # add the rest
    for partline in partlines[partstartline:]:
      partstr += partline + '\n'
    return partstr

  def encodeifneccessary(self, output):
    """encodes unicode strings and returns other strings unchanged"""
    if isinstance(output, unicode):
      encoding = encodingToUse(getattr(self, "encoding", "UTF-8"))
      return output.encode(encoding)
    return output

  def __str__(self):
    """convert to a string. double check that unicode is handled somehow here"""
    output = self.getoutput()
    return self.encodeifneccessary(output)

  def getoutput(self):
    """return this po element as a string"""
    lines = []
    lines.extend(self.othercomments)
    if self.isobsolete():
      lines.extend(self.typecomments)
      obsoletelines = []
      if self.obsoletemsgctxt:
        obsoletelines.append(self.getmsgpartstr("#~ msgctxt", self.obsoletemsgctxt))
      obsoletelines.append(self.getmsgpartstr("#~ msgid", self.obsoletemsgid, self.obsoletemsgidcomments))
      if self.obsoletemsgid_plural or self.obsoletemsgid_pluralcomments:
        obsoletelines.append(self.getmsgpartstr("#~ msgid_plural", self.obsoletemsgid_plural, self.obsoletemsgid_pluralcomments))
      obsoletelines.append(self.getmsgpartstr("#~ msgstr", self.obsoletemsgstr))
      for index, obsoleteline in enumerate(obsoletelines):
        # We need to account for a multiline msgid or msgstr here
        obsoletelines[index] = obsoleteline.replace('\n"', '\n#~ "')
      lines.extend(obsoletelines)
      lines = [self.encodeifneccessary(line) for line in lines]
      return "".join(lines)
    # if there's no msgid don't do msgid and string, unless we're the header
    # this will also discard any comments other than plain othercomments...
    if (len(self.msgid) == 0) or ((len(self.msgid) == 1) and (self.msgid[0] == '""')):
      if not (self.isheader() or self.msgidcomments or self.sourcecomments):
        return "".join(lines)
    lines.extend(self.automaticcomments)
    lines.extend(self.sourcecomments)
    lines.extend(self.typecomments)
    lines.extend(self.visiblecomments)
    if self.msgctxt:
      lines.append(self.getmsgpartstr("msgctxt", self.msgctxt))
    lines.append(self.getmsgpartstr("msgid", self.msgid, self.msgidcomments))
    if self.msgid_plural or self.msgid_pluralcomments:
      lines.append(self.getmsgpartstr("msgid_plural", self.msgid_plural, self.msgid_pluralcomments))
    lines.append(self.getmsgpartstr("msgstr", self.msgstr))
    lines = [self.encodeifneccessary(line) for line in lines]
    postr = "".join(lines)
    return postr

  def getlocations(self):
    """Get a list of locations from sourcecomments in the PO unit

    rtype: List
    return: A list of the locations with '#: ' stripped

    """
    locations = []
    for sourcecomment in self.sourcecomments:
      locations += quote.rstripeol(sourcecomment)[3:].split()
    return locations

  def addlocation(self, location):
    """Add a location to sourcecomments in the PO unit

    @param location: Text location e.g. 'file.c:23' does not include #:
    @type location: String

    """
    self.sourcecomments.append("#: %s\n" % location)

  def extract_msgidcomments(self, text=None):
    """Extract KDE style msgid comments from the unit.
    
    @rtype: String
    @return: Returns the extracted msgidcomments found in this unit's msgid.
    
    """

    if not text:
        text = unquotefrompo(self.msgidcomments)
    return text.split('\n')[0].replace('_: ', '', 1)

  def getcontext(self):
    """Get the message context."""
    return unquotefrompo(self.msgctxt) + self.extract_msgidcomments()

  def getid(self):
    """Returns a unique identifier for this unit."""
    context = self.getcontext()
    id = self.source
    if self.msgidcomments:
      id = "_: %s\n%s" % (context, id)
    elif context:
      id = "%s\04%s" % (context, id)
    return id

class pofile(base.TranslationStore, poheader.poheader):
  """this represents a .po file containing various units"""
  UnitClass = pounit
  def __init__(self, inputfile=None, encoding=None, unitclass=pounit):
    """construct a pofile, optionally reading in from inputfile.
    encoding can be specified but otherwise will be read from the PO header"""
    self.UnitClass = unitclass
    base.TranslationStore.__init__(self, unitclass=unitclass)
    self.units = []
    self.filename = ''
    self.encoding = encodingToUse(encoding)
    if inputfile is not None:
      self.parse(inputfile)

  def makeheader(self, **kwargs):
    """create a header for the given filename. arguments are specially handled, kwargs added as key: value
    pot_creation_date can be None (current date) or a value (datetime or string)
    po_revision_date can be None (form), False (=pot_creation_date), True (=now), or a value (datetime or string)"""

    headerpo = self.UnitClass(encoding=self.encoding)
    headerpo.markfuzzy()
    headerpo.msgid = ['""']
    headeritems = self.makeheaderdict(**kwargs)
    headerpo.msgstr = ['""']
    for (key, value) in headeritems.items():
        headerpo.msgstr.append(quote.quotestr("%s: %s\\n" % (key, value)))
    return headerpo

  def changeencoding(self, newencoding):
    """changes the encoding on the file"""
    self.encoding = encodingToUse(newencoding)
    if not self.units:
      return
    header = self.header()
    if not header or header.isblank():
      return
    charsetline = None
    headerstr = unquotefrompo(header.msgstr, True)
    for line in headerstr.split("\\n"):
      if not ":" in line: continue
      key, value = line.strip().split(":", 1)
      if key.strip() != "Content-Type": continue
      charsetline = line
    if charsetline is None:
      headerstr += "Content-Type: text/plain; charset=%s" % self.encoding
    else:
      charset = re.search("charset=([^ ]*)", charsetline)
      if charset is None:
        newcharsetline = charsetline
        if not newcharsetline.strip().endswith(";"):
          newcharsetline += ";"
        newcharsetline += " charset=%s" % self.encoding
      else:
        charset = charset.group(1)
        newcharsetline = charsetline.replace("charset=%s" % charset, "charset=%s" % self.encoding, 1)
      headerstr = headerstr.replace(charsetline, newcharsetline, 1)
    header.msgstr = quoteforpo(headerstr)

  def parsestring(cls, storestring):
    """Parses the po file contents in the storestring and returns a new pofile object (classmethod, constructor)"""
    parsedfile = pofile()
    parsedfile.parse(storestring)
    return parsedfile
  parsestring = classmethod(parsestring)

  def parse(self, input):
    """parses the given file or file source string"""
    if hasattr(input, 'name'):
      self.filename = input.name
    elif not getattr(self, 'filename', ''):
      self.filename = ''
    if hasattr(input, "read"):
      posrc = input.read()
      input.close()
      input = posrc
    # TODO: change this to a proper parser that doesn't do line-by-line madness
    lines = input.split("\n")
    start = 0
    end = 0
    # make only the first one the header
    linesprocessed = 0
    while end <= len(lines):
      if (end == len(lines)) or (not lines[end].strip()):   # end of lines or blank line
        newpe = self.UnitClass(encoding=self.encoding)
        linesprocessed = newpe.parse("\n".join(lines[start:end]))
        start += linesprocessed
        # TODO: find a better way of working out if we actually read anything
        if linesprocessed >= 1 and newpe.getoutput():
          self.units.append(newpe)
          if newpe.isheader():
            if "Content-Type" in self.parseheader():
              self.encoding = newpe.encoding
            # now that we know the encoding, decode the whole file
            if self.encoding is not None and self.encoding.lower() != 'charset':
              lines = self.decode(lines)
          if self.encoding is None: #still have not found an encoding, let's assume UTF-8
            #TODO: This might be dead code
            self.encoding = 'utf-8'
            lines = self.decode(lines)
            self.units = []
            start = 0
            end = 0
      end = end+1

  def removeduplicates(self, duplicatestyle="merge"):
    """make sure each msgid is unique ; merge comments etc from duplicates into original"""
    msgiddict = {}
    uniqueelements = []
    # we sometimes need to keep track of what has been marked
    # TODO: this is using a list as the pos aren't hashable, but this is slow...
    markedpos = []
    def addcomment(thepo):
      thepo.msgidcomments.append('"_: %s\\n"' % " ".join(thepo.getlocations()))
      markedpos.append(thepo)
    for thepo in self.units:
      if duplicatestyle.startswith("msgid_comment"):
        msgid = unquotefrompo(thepo.msgidcomments) + unquotefrompo(thepo.msgid)
      else:
        msgid = unquotefrompo(thepo.msgid)
      if thepo.isheader():
        # header msgids shouldn't be merged...
        uniqueelements.append(thepo)
      elif duplicatestyle == "msgid_comment_all":
        addcomment(thepo)
        uniqueelements.append(thepo)
      elif msgid in msgiddict:
        if duplicatestyle == "merge":
          if msgid:
            msgiddict[msgid].merge(thepo)
          else:
            addcomment(thepo)
            uniqueelements.append(thepo)
        elif duplicatestyle == "keep":
          uniqueelements.append(thepo)
        elif duplicatestyle == "msgid_comment":
          origpo = msgiddict[msgid]
          if origpo not in markedpos:
            addcomment(origpo)
          addcomment(thepo)
          uniqueelements.append(thepo)
        elif duplicatestyle == "msgctxt":
          origpo = msgiddict[msgid]
          if origpo not in markedpos:
            origpo.msgctxt.append('"%s"' % " ".join(origpo.getlocations()))
            markedpos.append(thepo)
          thepo.msgctxt.append('"%s"' % " ".join(thepo.getlocations()))
          uniqueelements.append(thepo)
      else:
        if not msgid and duplicatestyle != "keep":
          addcomment(thepo)
        msgiddict[msgid] = thepo
        uniqueelements.append(thepo)
    self.units = uniqueelements

  def __str__(self):
    """convert to a string. double check that unicode is handled somehow here"""
    output = self.getoutput()
    if isinstance(output, unicode):
      return output.encode(getattr(self, "encoding", "UTF-8"))
    return output

  def getoutput(self):
    """convert the units back to lines"""
    lines = []
    for pe in self.units:
      pesrc = str(pe) + "\n"
      lines.append(pesrc)
    lines = "".join(self.encode(lines)).rstrip()
    #After the last pounit we will have \n\n and we only want to end in \n:
    if lines: lines += "\n"
    return lines

  def encode(self, lines):
    """encode any unicode strings in lines in self.encoding"""
    newlines = []
    encoding = self.encoding
    if encoding is None or encoding.lower() == "charset":
      encoding = 'UTF-8'
    for line in lines:
      if isinstance(line, unicode):
        line = line.encode(encoding)
      newlines.append(line)
    return newlines

  def decode(self, lines):
    """decode any non-unicode strings in lines with self.encoding"""
    newlines = []
    for line in lines:
      if isinstance(line, str) and self.encoding is not None and self.encoding.lower() != "charset":
        try:
          line = line.decode(self.encoding)
        except UnicodeError, e:
          raise UnicodeError("Error decoding line with encoding %r: %s. Line is %r" % (self.encoding, e, line))
      newlines.append(line)
    return newlines

  def todict(self):
    """returns a dictionary of units based on msgid"""
    # NOTE: these units are quoted strings
    # TODO: make them unquoted strings, if useful...
    return dict([(" ".join(poel.msgid), poel) for poel in self.units])

  def unit_iter(self):
    for unit in self.units:
      if not (unit.isheader() or unit.isobsolete()):
        yield unit

if __name__ == '__main__':
  import sys
  pf = pofile(sys.stdin)
  sys.stdout.write(str(pf))

