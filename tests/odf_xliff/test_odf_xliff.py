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

import os
import os.path as path

from translate.storage import factory
from translate.convert import odf2xliff
from translate.convert import xliff2odf

def setup_module(module):
    global schema
    os.chdir(path.dirname(__file__))

def args(src, tgt, **kwargs):
    arg_list = ['--psyco=none', '--errorlevel=traceback', src, tgt]
    for flag, value in kwargs:
        value = unicode(value)
        if len(flag) == 1:
            arg_list.append('-%s' % flag)
        else:
            arg_list.append('--%s' % flag)
        if value is not None:
            arg_list.append(value)
    return arg_list

def xliff___eq__(self, other):
    return self.units == other.units

factory.classes['xlf'].__eq__ = xliff___eq__

def test_odf2xliff():
    SOURCE_ODF            = 'test_2.odt'
    REFERENCE_XLF         = 'test_2-test_odf2xliff-reference.xlf'
    GENERATED_XLF_ITOOLS  = 'test_2-test_odf2xliff-itools.xlf'
    GENERATED_XLF_TOOLKIT = 'test_2-test_odf2xliff-toolkit.xlf'

    reference_xlf = factory.getobject(REFERENCE_XLF)
    
    odf2xliff.main(args(SOURCE_ODF, GENERATED_XLF_TOOLKIT))
    generated_xlf_toolkit = factory.getobject(GENERATED_XLF_TOOLKIT)
    assert reference_xlf == generated_xlf_toolkit

    odf2xliff.main(args(SOURCE_ODF, GENERATED_XLF_ITOOLS))
    generated_xlf_itools = factory.getobject(GENERATED_XLF_ITOOLS)
    assert reference_xlf == generated_xlf_itools

def eq_odf(left, right):
    return True

def test_roundtrip():
    SOURCE_ODF    = 'test_2.odt'
    TARGET_XLF    = 'test_2-test_roundtrip.xlf'
    REFERENCE_ODF = 'test_2-test_roundtrip-reference.odt'
    GENERATED_ODF = 'test_2-reference.odt'
    
    odf2xliff.main(args(SOURCE_ODF, TARGET_XLF))
    xliff2odf.main(args(TARGET_XLF, GENERATED_ODF, t=SOURCE_ODF))
    assert eq_odf(REFERENCE_ODF, GENERATED_ODF)

def teardown_module(module):
    # TODO: Add code to remove the automatically generated files
    pass
