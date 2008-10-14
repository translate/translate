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
    parse_state = extract.ParseState(odf_shared.no_translate_content_elements, 
                                     odf_shared.inline_elements)
    extract.build_store(cStringIO.StringIO(contents), store, parse_state)
    store.save()
    return True

def main(argv=None):
    from translate.convert import convert
    # For formats see OpenDocument 1.2 draft 7 Appendix C
    formats = {"sxw": ("xlf", convertodf),
               "odt": ("xlf", convertodf), # Text
               "ods": ("xlf", convertodf), # Spreadsheet
               "odp": ("xlf", convertodf), # Presentation
               "odg": ("xlf", convertodf), # Drawing
               "odc": ("xlf", convertodf), # Chart
               "odf": ("xlf", convertodf), # Formula
               "odi": ("xlf", convertodf), # Image
               "odm": ("xlf", convertodf), # Master Document
               "ott": ("xlf", convertodf), # Text template
               "ots": ("xlf", convertodf), # Spreadsheet template
               "otp": ("xlf", convertodf), # Presentation template
               "otg": ("xlf", convertodf), # Drawing template
               "otc": ("xlf", convertodf), # Chart template
               "otf": ("xlf", convertodf), # Formula template
               "oti": ("xlf", convertodf), # Image template
               "oth": ("xlf", convertodf), # Web page template
              }
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)

if __name__ == '__main__':
    main()
