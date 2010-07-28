#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
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


"""Convert Gettext PO localization files to subtitle files"""

from translate.storage import factory


class resub:

    def __init__(self, templatefile, inputstore):
        from translate.storage import subtitles
        self.templatefile = templatefile
        self.templatestore = subtitles.SubtitleFile(templatefile)
        self.inputstore = inputstore

    def convertstore(self, includefuzzy=False):
        self.includefuzzy = includefuzzy
        self.inputstore.makeindex()
        for unit in self.templatestore.units:
            for location in unit.getlocations():
                if location in self.inputstore.locationindex:
                    inputunit = self.inputstore.locationindex[location]
                    if inputunit.isfuzzy() and not self.includefuzzy:
                        unit.target = unit.source
                    else:
                        unit.target = inputunit.target 
                else:
                    unit.target = unit.source
        return str(self.templatestore)


def convertsub(inputfile, outputfile, templatefile, includefuzzy=False):
    inputstore = factory.getobject(inputfile)
    if templatefile is None:
        raise ValueError("must have template file for subtitle files")
    else:
        convertor = resub(templatefile, inputstore)
    outputstring = convertor.convertstore(includefuzzy)
    outputfile.write(outputstring)
    return 1


def main(argv=None):
    # handle command line options
    from translate.convert import convert
    formats = {
         ("po", "srt"): ("srt", convertsub),
         ("po", "sub"): ("sub", convertsub),
         ("po", "ssa"): ("ssa", convertsub),
         ("po", "ass"): ("ass", convertsub),
    }
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)

if __name__ == '__main__':
    main()
