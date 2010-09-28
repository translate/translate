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

"""convert Gettext PO localization files to HTML files

see: http://translate.sourceforge.net/wiki/toolkit/po2html for examples and
usage instructions
"""

from translate.storage import html
from translate.storage import po


class po2html:
    """po2html can take a po file and generate html. best to give it a
    template file otherwise will just concat msgstrs"""

    def lookup(self, string):
        unit = self.inputstore.sourceindex.get(string, None)
        if unit is None:
            return string
        unit = unit[0]
        if self.includefuzzy or not unit.isfuzzy():
            return unit.target
        else:
            return string

    def mergestore(self, inputstore, templatetext, includefuzzy):
        """converts a file to .po format"""
        self.inputstore = inputstore
        self.inputstore.makeindex()
        self.includefuzzy = includefuzzy
        output_store = html.htmlfile(inputfile=templatetext, callback=self.lookup)
        return output_store.filesrc


def converthtml(inputfile, outputfile, templatefile, includefuzzy=False):
    """reads in stdin using fromfileclass, converts using convertorclass,
    writes to stdout"""
    inputstore = po.pofile(inputfile)
    convertor = po2html()
    if templatefile is None:
        raise ValueError("must have template file for HTML files")
    else:
        outputstring = convertor.mergestore(inputstore, templatefile,
                                            includefuzzy)
    outputfilepos = outputfile.tell()
    outputfile.write(outputstring)
    return 1


def main(argv=None):
    from translate.convert import convert
    from translate.misc import stdiotell
    import sys
    sys.stdout = stdiotell.StdIOWrapper(sys.stdout)
    formats = {("po", "htm"): ("htm", converthtml),
               ("po", "html"): ("html", converthtml),
               ("po", "xhtml"): ("xhtml", converthtml),
               ("po"): ("html", converthtml),
              }
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
