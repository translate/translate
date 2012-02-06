#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008,2011 Zuza Software Foundation
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

# Original Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

"""convert Gettext PO localization files to Mozilla .lang files

see: http://translate.sourceforge.net/wiki/toolkit/po2mozlang for examples and
usage instructions
"""

from translate.storage import mozilla_lang as lang
from translate.storage import po


class po2lang:

    def __init__(self, duplicatestyle="msgctxt"):
        self.duplicatestyle = duplicatestyle

    def convertstore(self, inputstore, includefuzzy=False):
        """converts a file to .lang format"""
        thetargetfile = lang.LangStore()

        # Run over the po units
        for pounit in inputstore.units:
            # Skip the header
            if pounit.isheader():
                continue
            newunit = thetargetfile.addsourceunit(pounit.source)
            if includefuzzy or not pounit.isfuzzy():
                newunit.settarget(pounit.target)
            else:
                newunit.settarget(pounit.source)
        return thetargetfile


def convertlang(inputfile, outputfile, templates,  includefuzzy=False):
    """reads in stdin using fromfileclass, converts using convertorclass,
    writes to stdout"""
    inputstore = po.pofile(inputfile)
    if inputstore.isempty():
        return 0
    convertor = po2lang()
    outputstore = convertor.convertstore(inputstore,  includefuzzy)
    outputfile.write(str(outputstore))
    return 1


formats = {
    "po": ("lang", convertlang),
    ("po", "lang"): ("lang", convertlang),
}


def main(argv=None):
    from translate.convert import convert
    from translate.misc import stdiotell
    import sys
    sys.stdout = stdiotell.StdIOWrapper(sys.stdout)
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                           description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
