#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2009 Zuza Software Foundation
# 
# This file is part of translate.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""This module contains functions for identifying languages based on language models.

   It wraps U{libtextcat<http://software.wise-guys.nl/libtextcat/>} to get the language
   identification functionality.

   To use first create an instance of I{LanguageIdentifier} and then use the methods 
   I{identify} or I{identify_store} to detect the language in a string or in a translation
   store respectively.
"""

from ctypes import *
import ctypes.util

from translate.lang.data import *

# Load libtextcat
textcat = None
# 'textcat' is recognised on Unix, while only 'libtextcat' is recognised on
# windows. Therefore we test both.
names = ['textcat', 'libtextcat']
for name in names:
    lib_location = ctypes.util.find_library(name)
    if lib_location:
        textcat = cdll.LoadLibrary(lib_location)
        if textcat:
            break
else:
    # Now we are getting desperate, so let's guess a unix type DLL that might 
    # be in LD_LIBRARY_PATH or loaded with LD_PRELOAD
    try:
        textcat = cdll.LoadLibrary('libtextcat.so')
    except OSError, e:
        raise ImportError("textcat library not found")

# Original initialisation
textcat.textcat_Init.argtypes = [c_char_p]
textcat.textcat_Init.retype = c_int

# Initialisation used in OpenOffice.org modification which allows the models to be in a different directory
textcat.special_textcat_Init.argtypes = [c_char_p, c_char_p]
textcat.special_textcat_Init.restype = c_int

# Cleans up textcat
textcat.textcat_Done.argtypes = [c_int]

# Perform language guessing
textcat.textcat_Classify.argtypes = [c_int, c_char_p, c_int]
textcat.textcat_Classify.restype = c_char_p

class LanguageIdentifier(object):

    def __init__(self, config, model_dir):
        """
        @param config: path to .conf for textcat
        @type config: String
        @param model_dir: path to language models
        @type model_dir: String
        """
        if textcat is None:
            return None
        self._handle = textcat.special_textcat_Init(config, model_dir)

    lang_list_re = re.compile("\[(.+?)\]+")

    def _lang_result_to_list(self, lang_result):
        """Converts a text result of '[lang][lang]' into a Python list of language codes"""
        if lang_result in ('SHORT', 'UNKNOWN'):
            return []
        return self.lang_list_re.findall(lang_result)

    def identify(self, text, sample_length=None):
        """Identify the language in I{text} by sampling I{sample_length}

        @param text: Text to be identified
        @type text: String
        @param sample_length: The amount of I{text} to be analysed
        @type sample_length: Int
        @return: list of language codes
        """
        if sample_length is None or sample_length > len(text):
            sample_length = len(text)
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        matches = self._lang_result_to_list(textcat.textcat_Classify(self._handle, text, sample_length))
        return [(simplify_to_common(match, languages), 0.8) for match in matches]

    def identify_store(self, store, sample_length=None):
        """Identify the language of a translation store

        @param store: Store to be identified
        @type store: L{TranslationStore <storage.base.TranslatonStore>}
        @param sample_length: The amount of text to be analysed
        @type sample_length: Int
        @return: list of language codes
        """
        text = ""
        for unit in store.units:
            text = text + unit.target
            if sample_length is not None and len(text) >= sample:
                break
        return self.identify(text, sample_length)

    def __del__(self):
        textcat.textcat_Done(self._handle)
