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
from subprocess import call

def xmllint(fullpath):
    return call(['xmllint', '--noout', '--schema', 'xliff-core-1.1.xsd', fullpath]) == 0

def setup_module(module):
    os.chdir(path.dirname(__file__))

def find_files(base, check_ext):
    for dirpath, _dirnames, filenames in os.walk(base):
        for filename in filenames:
            fullpath = path.join(dirpath, filename)
            _namepath, ext = path.splitext(fullpath)
            if check_ext == ext:
                yield fullpath

def test_open_office_to_xliff():
    assert call(['oo2xliff', 'en-US.sdf', '-l', 'fr', 'fr']) == 0
    for filepath in find_files('fr', '.xlf'):
        assert xmllint(filepath)

def test_po_to_xliff():
    OUTPUT = 'af-pootle.xlf'
    assert call(['po2xliff', 'af-pootle.po', OUTPUT]) == 0
    assert xmllint(OUTPUT)

def teardown_module(module):
    # TODO: Add code to remove the automatically generated files
    pass
