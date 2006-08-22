#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2006 Zuza Software Foundation
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

"""factory methods to build real storage objects that conform to base.py"""

from translate.storage import base
from translate.storage import po
from translate.storage import csvl10n
from translate.storage import xliff
from translate.storage import poxliff
from translate.storage import tmx
from translate.storage import tbx

import os

#TODO: Monolingual formats (with template?)
#TODO: guess from first lines

classes = {"po": po.pofile, "pot": po.pofile, "csv": csvl10n.csvfile, 
            "xliff": xliff.xlifffile, "xlf": xliff.xlifffile, 
            "tmx": tmx.tmxfile, "tbx": tbx.tbxfile}

def getname(storefile):
    """returns the filename"""
    if not isinstance(storefile, basestring):
        if not hasattr(storefile, "name"):
            raise Exception("Factory can only guess filetype from filename")
        else:
            storefilename = storefile.name
    else:
        storefilename = storefile
    return storefilename

def getclass(storefile, ignore=None):
    """Factory that returns the applicable class for the type of file presented.
    Specify ignore to ignore some part at the back of the name (like .gz). """
    storefilename = getname(storefile)
    if ignore and storefilename.endswith(ignore):
        storefilename = storefile[:-len(ignore)]
    root, ext = os.path.splitext(storefilename)
    ext = ext[len(os.path.extsep):].lower()
    try:
        storeclass = classes[ext]
    except KeyError:
        raise Exception("Unknown filetype (%s)" % storefilename)
    return storeclass

def getobject(storefile, ignore=None):
    """Factory that returns a usable object for the type of file presented.
    Specify ignore to ignore some part at the back of the name (like .gz). """
    if isinstance(storefile, base.TranslationStore):
        return storefile
    storefilename = getname(storefile)
    storeclass = getclass(storefilename, ignore)
    if os.path.exists(storefilename) or not getattr(storefile, "closed", True):
        store = storeclass.parsefile(storefile)
    else:
        store = storeclass()
    return store

