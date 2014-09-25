#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2014 Zuza Software Foundation
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Convert OpenDocument (ODF) files to XLIFF localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/odf2xliff.html
for examples and usage instructions.
"""

from cStringIO import StringIO

from translate.convert import convert
from translate.storage import factory, odf_io, odf_shared
from translate.storage.xml_extract import extract


def convertodf(inputfile, outputfile, templates):
    """reads in stdin using fromfileclass, converts using convertorclass,
       writes to stdout
    """
    # Since the convertoptionsparser will give us an open file, we risk that
    # it could have been opened in non-binary mode on Windows, and then we'll
    # have problems, so let's make sure we have what we want.
    inputfile.close()
    inputfile = file(inputfile.name, mode='rb')

    store = factory.getobject(outputfile)

    try:
        store.setfilename(store.getfilenode('NoName'), inputfile.name)
    except:
        print("couldn't set origin filename")

    contents = odf_io.open_odf(inputfile)
    for data in contents.values():
        parse_state = extract.ParseState(odf_shared.no_translate_content_elements,
                                         odf_shared.inline_elements)
        extract.build_store(StringIO(data), store, parse_state)

    store.save()
    return True


def main(argv=None):
    # For formats see OpenDocument 1.2 draft 7 Appendix C
    formats = {
        "sxw": ("xlf", convertodf),
        "odt": ("xlf", convertodf),  # Text
        "ods": ("xlf", convertodf),  # Spreadsheet
        "odp": ("xlf", convertodf),  # Presentation
        "odg": ("xlf", convertodf),  # Drawing
        "odc": ("xlf", convertodf),  # Chart
        "odf": ("xlf", convertodf),  # Formula
        "odi": ("xlf", convertodf),  # Image
        "odm": ("xlf", convertodf),  # Master Document
        "ott": ("xlf", convertodf),  # Text template
        "ots": ("xlf", convertodf),  # Spreadsheet template
        "otp": ("xlf", convertodf),  # Presentation template
        "otg": ("xlf", convertodf),  # Drawing template
        "otc": ("xlf", convertodf),  # Chart template
        "otf": ("xlf", convertodf),  # Formula template
        "oti": ("xlf", convertodf),  # Image template
        "oth": ("xlf", convertodf),  # Web page template
    }
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == '__main__':
    main()
