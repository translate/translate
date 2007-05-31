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

import os, pickle

class pickleTM:
    """This class is for pickling and unpickling a matcher"""
    def getMatcher(self, filename):
        """
        Unpickle matcher from filename.
        @return matcher: matcher of TM locations
        """
        matcher = None
        if (filename and os.path.exists(filename)):
            tmpFile = open(filename, 'rb')
            try:
                matcher = pickle.load(tmpFile)
            except:
                pass
            tmpFile.close()
        return matcher
    
    def dumpMatcher(self, matcher, filename):
        """
        Pickle matcher to a filename.
        @param matcher: matcher of TM files or Glossary files
        """
        #TODO: fix "can't pickle instancemethod objects"
        pickleFile = open(filename, 'w')
        pickle.dump(matcher, pickleFile)
        pickleFile.close()

