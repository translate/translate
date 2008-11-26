#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
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
#

import zipfile

def open_odf(filename):
    z = zipfile.ZipFile(filename, 'r')
    return {'content.xml': z.read("content.xml"),
            'meta.xml':    z.read("meta.xml"),
            'styles.xml':  z.read("styles.xml")}

def copy_odf(input_file, output_file, exclusion_list):
    input_zip  = zipfile.ZipFile(input_file,  'r')
    output_zip = zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED)
    for name in [name for name in input_zip.namelist() if name not in exclusion_list]:
        output_zip.writestr(name, input_zip.read(name))
    return output_zip

