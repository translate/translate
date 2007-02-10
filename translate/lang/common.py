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

"""This module contains all the common features for languages.

Supported features:
language code (km, af)
language name (Khmer, Afrikaans)
Plurals
  Number of plurals (nplurals)
  Plural equation

TODO:
Ideas for possible features:

Language-Team information

Segmentation
  words
  phrases
  sentences
Punctuation
  End of sentence
  Start of sentence
  Middle of sentence
  Quotes
    single
    double

Valid characters
Accelerator characters
Special characters
Direction (rtl or ltr)
"""
class Common:
    """This class is the common parent class for all language classes."""
    
    code = ""
    fullname = ""
    # 0 is not a valid value - it must be overridden
    nplurals = 0
    pluralequation = "0"
