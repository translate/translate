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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Convert Gettext PO localization files to Qt Linguist Phrase Book (.qph) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/po2qph.html
for examples and usage instructions.
"""

from translate.storage import po, qph


class po2qph(object):

    def convertstore(self, inputstore, sourcelanguage='en', targetlanguage=None):
        """converts a .po file to .qph format"""
        qphfile = qph.QphFile(sourcelanguage=sourcelanguage, targetlanguage=targetlanguage)
        for inputunit in inputstore.units:
            if inputunit.isheader() or inputunit.isblank():
                continue

            source = inputunit.source
            translation = inputunit.target
            definition = inputunit.getcontext()
            pos = inputunit.getnotes()

            unit = qph.QphUnit(source)
            unit.settarget(translation)
            unit.addnote(definition)
            unit.addnote(pos)

            qphfile.addunit(unit)
        return qphfile


def convertpo(inputfile, outputfile, sourcelanguage='en', targetlanguage=None):
    """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
    inputstore = po.pofile(inputfile)
    if inputstore.isempty():
        return 0
    convertor = po2qph()
    outputstore = convertor.convertstore(inputstore, sourcelanguage, targetlanguage)
    outputstore.serialize(outputfile)
    return 1


def main(argv=None):
    from translate.convert import convert
    formats = {"po": ("qph", convertpo), ("po", "qph"): ("qph", convertpo)}
    parser = convert.ConvertOptionParser(formats, usetemplates=False, description=__doc__)
    parser.add_option(
        "-l", "--language", dest="targetlanguage", default=None,
        help="set target language code (e.g. af-ZA) [required]", metavar="LANG")
    parser.passthrough.append("sourcelanguage")
    parser.passthrough.append("targetlanguage")
    parser.run(argv)


if __name__ == '__main__':
    main()
