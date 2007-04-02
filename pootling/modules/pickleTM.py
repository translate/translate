#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module provides interface for pickle and unpickle each matcher candidates of base object files

import os, tempfile, pickle
from translate.storage import factory
from translate.search import match
from translate.storage import poheader
from ConfigParser import *

class pickleTM:
    """This class is for pickling and unpickling TM or Terminology"""
    def __init__(self, confFile = "", section = None):
        self.config = ConfigParser()
        self.confFile = confFile
        self.section = section
        self.config.read(self.confFile)
        
    def createStore(self, file):
        """Create a base object from file.
        
        @param file: as a file path or object
        @return: store as a base object
        
        """
        try:
            store = factory.getobject(file)
            store.filepath = file
            if (isinstance(store, poheader.poheader)):
                headerDic = store.parseheader()
                store.translator = headerDic['Last-Translator']
                store.date = headerDic['PO-Revision-Date']
            else:
                store.translator = ""
                store.date = ""
            
        except:
            store = None
        return store
    
    def getStore(self, TMpath):
        """Return base object as store or storelist.
        
        @param TMpath: file or translation memory path as string
        @return store or storelist
        
        """
        diveSub = False
        if (self.config.has_option(self.section, "diveIntoSub")):
            diveSub = self.config.get(self.section, "diveIntoSub")
        path = str(TMpath)
        
        if (os.path.isfile(path)):
            return self.createStore(path)
        
        if (os.path.isdir(path)):
            storelist = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    store = self.createStore(os.path.join(root + '/' + file))
                    if (store):
                        storelist.append(store)
                # whether dive into subfolder
                if (not diveSub):
                    # not dive into subfolder
                    break
            return storelist
        
    def getStoreList(self, stringlist):
        '''return a list of stores of file locations.
        
        @param stringlist: a list of file paths
        @return storelist: a list of stores
        '''
        store = None
        storelist = []
        for i in range(len(stringlist)):
            store = self.getStore(stringlist[i])
            if (store):
                if (not isinstance(store, list)):
                    storelist.append(store)
                else:
                    storelist += store
        return storelist
    
    def pickleMatcher(self, matcher):
        """Pickle matcher to a location.
        
        @param matcher: matcher of TM files or Glossary files
        """
        if (not self.config.has_section(self.section)):
            self.config.add_section(self.section)
        if (self.config.has_option(self.section, "location")):
            filename = self.config.get(self.section, "location")
        else:
            handle, filename = tempfile.mkstemp('','PKL')
        tmpFile = open(filename, 'w')
        if (matcher):
            pickle.dump(matcher, tmpFile)
        tmpFile.close()
        self.config.set(self.section, "location", filename)
        confFilefp = open(self.confFile, 'w')
        self.config.write(confFilefp)
        confFilefp.close()
    
    def getMatcher(self):
        """Unpickle matcher from file.
        
        @return matcher: matcher of TM locations
        
        """
        filename = None
        matcher = None
        if (self.config.has_section(self.section) and self.config.has_option(self.section, "location")):
            filename = self.config.get(self.section, "location")
            if (filename and os.path.exists(filename)):
                tmpFile = open(filename, 'rb')
                try:
                    matcher = pickle.load(tmpFile)
                except:
                    pass
                tmpFile.close()
        return matcher
    
    def buildTMMatcher(self, stringlist, max_candidates, min_similarity,  max_string_len):
        """Build new matcher of TM locations and dump it to file.
        
        @param stringlist: List of TM locations as string of path
        @param max_candidates: The maximum number of candidates that should be assembled,
        @param min_similarity: The minimum similarity that must be attained to be included in
        @param max_string_len: maximum length of source string to be searched.
        @return: matcher object
        """
        storelist = self.getStoreList(stringlist)
        matcher = match.matcher(storelist, max_candidates, min_similarity,  max_string_len)
        self.pickleMatcher(matcher)
        return matcher

    def buildTermMatcher(self, stringlist, max_candidates, min_similarity,  max_string_len):
        """Build new terminology matcher and dump it to file.
        
        @param stringlist: List of glossary locations as string of path
        @param max_candidates: The maximum number of candidates that should be assembled,
        @param min_similarity: The minimum similarity that must be attained to be included in
        @param max_string_len: maximum length of source string to be searched.
        @return: matcher object
        """
        storelist = self.getStoreList(stringlist)
        matcher = match.terminologymatcher(storelist, max_candidates, min_similarity,  max_string_len)
        self.pickleMatcher(matcher)
        return matcher
    
    def removeFile(self):
        '''remove file which stores matcher
        '''
        if (self.config.has_section(self.section) and self.config.has_option(self.section, "location")):
            filename = self.config.get(self.section, "location")
            os.remove(filename)
            self.config.remove_option(self.section, "location")
            confFilefp = open(self.confFile, 'w')
            self.config.write(confFilefp)
            confFilefp.close()
            
