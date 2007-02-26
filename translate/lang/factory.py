#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2007 Zuza Software Foundation
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

"""This module provides a factory to instantiate language classes."""

from translate.lang import common
from translate.lang import data

def getlanguage(code):
    """This returns a language class.

    @param code: The ISO 639 language code
    """
    if code:
        code = code.replace("-", "_")
    try:
        if code is None:
            raise ImportError ("Can't determine language code")
        exec("from translate.lang import %s" % code)
        exec("langclass = %s.%s" % (code, code))
        return langclass
    except ImportError, e:
        simplercode = data.simplercode(code)
        if simplercode:
            relatedlanguage = getlanguage(simplercode)
            if isinstance(relatedlanguage, common.Common):
                relatedlanguage = relatedlanguage.__class__(code)
            return relatedlanguage
        else:
            return common.Common(code)
