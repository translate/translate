#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
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

"""convert OpenDocument (ODF) files to Gettext PO localization files"""

import cStringIO
import zipfile

from translate.storage import factory
from translate.storage.xml_extract import extract
from translate.storage import odf_shared

def convertodf(inputfile, outputfile, templates):
    """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
    store = factory.getobject(outputfile)
    try:
        z = zipfile.ZipFile(inputfile, 'r')
        contents = z.read("content.xml")
    except (ValueError, zipfile.BadZipfile):
        contents = open(inputfile, 'r').read()
    parse_state = extract.ParseState(odf_shared.odf_namespace_table, odf_shared.odf_placables_table, odf_shared.odf_inline_placeables_table)
    extract.build_store(cStringIO.StringIO(contents), store, parse_state)
    store.save()
    return True

def main(argv=None):
    from translate.convert import convert
    formats = {"sxw": ("xlf", convertodf),
               "odt": ("xlf", convertodf),
               "ods": ("xlf", convertodf),
               "odp": ("xlf", convertodf)}
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)

if __name__ == '__main__':
    main()
