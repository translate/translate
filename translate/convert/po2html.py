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

from translate.storage import po


class po2html:
    """po2html can take a po file and generate html. best to give it a
    template file otherwise will just concat msgstrs"""

    def mergestore(self, inputstore, templatetext, includefuzzy):
        """converts a file to .po format"""
        htmlresult = templatetext.replace("\n", " ")
        if isinstance(htmlresult, str):
            #TODO: get the correct encoding
            htmlresult = htmlresult.decode('utf-8')
        # TODO: use the algorithm from html2po to get blocks and translate
        # them individually rather than using replace
        for inputunit in inputstore.units:
            if inputunit.isheader():
                continue
            msgid = inputunit.source
            msgstr = None
            if includefuzzy or not inputunit.isfuzzy():
                msgstr = inputunit.target
            else:
                msgstr = inputunit.source
            if msgstr.strip():
                # TODO: "msgid" is already html-encoded ("&" -> "&amp;"), while
                #   "msgstr" is not encoded -> thus the replace fails
                #   see test_po2html.py in line 67
                htmlresult = htmlresult.replace(msgid, msgstr, 1)
        return htmlresult.encode('utf-8')


def converthtml(inputfile, outputfile, templatefile, includefuzzy=False):
    """reads in stdin using fromfileclass, converts using convertorclass,
    writes to stdout"""
    inputstore = po.pofile(inputfile)
    convertor = po2html()
    if templatefile is None:
        raise ValueError("must have template file for HTML files")
    else:
        templatestring = templatefile.read()
        outputstring = convertor.mergestore(inputstore, templatestring,
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
