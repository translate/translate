#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2007 Zuza Software Foundation
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

"""module for parsing Qt .ts files for translation"""

from translate.misc import ourdom

class QtTsParser:
  contextancestors = dict.fromkeys(["TS"])
  messageancestors = dict.fromkeys(["TS", "context"])
  def __init__(self, inputfile=None):
    """make a new QtTsParser, reading from the given inputfile if required"""
    self.filename = getattr(inputfile, "filename", None)
    self.knowncontextnodes = {}
    self.indexcontextnodes = {}
    if inputfile is None:
      self.document = ourdom.parseString("<!DOCTYPE TS><TS></TS>")
    else:
      self.document = ourdom.parse(inputfile)
      assert self.document.documentElement.tagName == "TS"

  def addtranslation(self, contextname, source, translation, comment=None, transtype=None, createifmissing=False):
    """adds the given translation (will create the nodes required if asked). Returns success"""
    contextnode = self.getcontextnode(contextname)
    if contextnode is None:
      if not createifmissing:
        return False
      # construct a context node with the given name
      contextnode = self.document.createElement("context")
      namenode = self.document.createElement("name")
      nametext = self.document.createTextNode(contextname)
      namenode.appendChild(nametext)
      contextnode.appendChild(namenode)
      self.document.documentElement.appendChild(contextnode)
    if contextname in self.indexcontextnodes:
      messagesourceindex = self.indexcontextnodes[contextname]
    else:
      messagesourceindex = {}
      for message in self.getmessagenodes(contextnode):
        messagesource = self.getmessagesource(message).strip()
        messagesourceindex[messagesource] = message
      self.indexcontextnodes[contextname] = messagesourceindex
    message = messagesourceindex.get(source.strip(), None)
    if message is not None:
      translationnode = ourdom.getFirstElementByTagName(message, "translation")
      newtranslationnode = self.document.createElement("translation")
      translationtext = self.document.createTextNode(translation)
      newtranslationnode.appendChild(translationtext)
      message.replaceChild(newtranslationnode, translationnode)
      return True
    if not createifmissing:
      return False
    messagenode = self.document.createElement("message")
    sourcenode = self.document.createElement("source")
    sourcetext = self.document.createTextNode(source)
    sourcenode.appendChild(sourcetext)
    messagenode.appendChild(sourcenode)
    if comment:
        commentnode = self.document.createElement("comment")
        commenttext = self.document.createTextNode(comment)
        commentnode.appendChild(commenttext)
        messagenode.appendChild(commentnode)
    translationnode = self.document.createElement("translation")
    translationtext = self.document.createTextNode(translation)
    translationnode.appendChild(translationtext)
    if transtype:
      translationnode.setAttribute("type",transtype)
    messagenode.appendChild(translationnode)
    contextnode.appendChild(messagenode)
    messagesourceindex[source.strip()] = messagenode
    return True

  def getxml(self):
    """return the ts file as xml"""
    xml = self.document.toprettyxml(indent="    ", encoding="utf-8")
    #This line causes empty lines in the translation text to be removed (when there are two newlines)
    xml = "\n".join([line for line in xml.split("\n") if line.strip()])
    return xml

  def getcontextname(self, contextnode):
    """returns the name of the given context"""
    namenode = ourdom.getFirstElementByTagName(contextnode, "name")
    return ourdom.getnodetext(namenode)

  def getcontextnode(self, contextname):
    """finds the contextnode with the given name"""
    contextnode = self.knowncontextnodes.get(contextname, None)
    if contextnode is not None:
      return contextnode
    contextnodes = self.document.searchElementsByTagName("context", self.contextancestors)
    for contextnode in contextnodes:
      if self.getcontextname(contextnode) == contextname:
        self.knowncontextnodes[contextname] = contextnode
        return contextnode
    return None

  def getmessagenodes(self, context=None):
    """returns all the messagenodes, limiting to the given context (name or node) if given"""
    if context is None:
      return self.document.searchElementsByTagName("message", self.messageancestors)
    else:
      if isinstance(context, (str, unicode)):
        # look up the context node by name
        context = self.getcontextnode(context)
        if context is None:
          return []
      return context.searchElementsByTagName("message", self.messageancestors)

  def getmessagesource(self, message):
    """returns the message source for a given node"""
    sourcenode = ourdom.getFirstElementByTagName(message, "source")
    return ourdom.getnodetext(sourcenode)

  def getmessagetranslation(self, message):
    """returns the message translation for a given node"""
    translationnode = ourdom.getFirstElementByTagName(message, "translation")
    return ourdom.getnodetext(translationnode)

  def getmessagetype(self, message):
    """returns the message translation attributes for a given node"""
    translationnode = ourdom.getFirstElementByTagName(message, "translation")
    return translationnode.getAttribute("type")

  def getmessagecomment(self, message):
    """returns the message comment for a given node"""
    commentnode = ourdom.getFirstElementByTagName(message, "comment")
    # NOTE: handles only one comment per msgid (OK)
    # and only one-line comments (can be VERY wrong) TODO!!!
    return ourdom.getnodetext(commentnode)

  def iteritems(self):
    """iterates through (contextname, messages)"""
    for contextnode in self.document.searchElementsByTagName("context", self.contextancestors):
      yield self.getcontextname(contextnode), self.getmessagenodes(contextnode)

  def __del__(self):
    """clean up the document if required"""
    if hasattr(self, "document"):
      self.document.unlink()

