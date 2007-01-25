#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
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
# This module is searching text from translation memory (PO, TMX, and Database)


from Pootle.tools import updatetm
from translate.storage import factory
import os, tempfile, sys

def autoTranslate(memo, inputfile):
    #TODO: Make it possible to search in Database. Set more conditions such as similarity....
    """return output as a po.pofile object.
        @param memo: String type"""
    try:
        matcher = updatetm.memory(memo)
    except Exception, e:
        raise e
    # create a usable filename for output
    handle, outputfile = tempfile.mkstemp('.po')
    output = updatetm.buildmatches(inputfile, outputfile, matcher)
    os.remove(outputfile)
    return output
    
