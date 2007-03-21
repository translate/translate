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
from ConfigParser import *

class pickleTM:
    """This class is for pickling TM"""
    def __init__(self, confFile = ""):
        self.config = ConfigParser()
        self.config.read(confFile)
        self.confFile = confFile
        
    def createStore(self, file):
        """Create a base object from file.
        
        @param file: as a file path or object
        @return: store as a base object
        
        """
        try:
            store = factory.getobject(file)
        except:
            store = None
        return store
    
    def getStore(self, TMpath):
        """Return base object as store or storelist.
        
        @param TMpath: file or translation memory path as string
        @return store or storelist
        
        """
        try:
            diveSub = self.config.get('General','diveIntoSub')
        except NoOptionError:
            pass
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
        
    def pickleMatcher(self, matcher, prefix = "PKL"):
        """Pickle matcher of TM locations.
        
        @param matcher: matcher of TM files or locations
        
        """
        try:
            filename = self.config.get('General','fileStoreMatcher')
        except NoOptionError:
            handle, filename = tempfile.mkstemp('','PKL')
        tmpFile = open(filename, 'w')
        if (matcher):
            pickle.dump(matcher, tmpFile)
        tmpFile.close()
        self.config.set('General', 'fileStoreMatcher', filename)
        confFilefp = open(self.confFile, 'w')
        self.config.write(confFilefp)
        confFilefp.close()
    
    def getMatcher(self):
        """Unpickle matcher from file.
        
        @return matcher: matcher of TM locations
        
        """
        matcher = None
        try:
            filename = self.config.get('General','fileStoreMatcher')
            if (filename and os.path.exists(filename)):
                tmpFile = open(filename, 'rb')
                try:
                    matcher = pickle.load(tmpFile)
                except:
                    pass
                tmpFile.close()
        except:
            pass
        return matcher
    
    def buildMatcher(self, stringlist, max_candidates, min_similarity,  max_string_len):
        """Build new matcher of TM locations and dump it to file.
        
        @param stringlist: List of TM locations as string of path
        @param max_candidates: The maximum number of candidates that should be assembled,
        @param min_similarity: The minimum similarity that must be attained to be included in
        @param max_string_len: maximum length of source string to be searched.
        @return: matcher object
        """
        store = None
        storelist = []
        for i in range(len(stringlist)):
            store = self.getStore(stringlist[i])
            if (store):
                if (not isinstance(store, list)):
                    storelist.append(store)
                else:
                    storelist += store
        matcher = match.matcher(storelist, max_candidates, min_similarity,  max_string_len)
        self.pickleMatcher(matcher)
        return matcher
    
    def removeFile(self):
        try:
            filename = self.config.get('General','fileStoreMatcher')
            os.remove(filename)
            self.config.remove_option('General', 'fileStoreMatcher')
        except:
            pass
            
