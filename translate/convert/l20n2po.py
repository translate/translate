# -*- coding: utf-8 -*-
#
# Copyright 2016 Zuza Software Foundation
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

"""Convert Mozilla .l20n files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/l20n2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import l20n, po


class l20n2po(object):
    """convert a .l20n file to a .po file for handling the translation.
    """

    def __init__(self, blankmsgstr=False, duplicatestyle="msgctxt"):
        self.blankmsgstr = blankmsgstr
        self.duplicatestyle = duplicatestyle

    def convert_l20nunit(self, unit):
        po_unit = po.pounit(encoding="UTF-8")
        po_unit.setid(unit.getid())
        po_unit.addlocation(unit.getid())
        po_unit.source = unit.value
        po_unit.addnote(unit.comment, "developer")

        return po_unit

    def convert_store(self, l20n_store):
        """converts a .l20n file to a .po file..."""
        target_store = po.pofile()
        l20n_store.makeindex()
        for l20nunit in l20n_store.units:
            pounit = self.convert_l20nunit(l20nunit)
            target_store.addunit(pounit)
        target_store.removeduplicates(self.duplicatestyle)
        return target_store

    def merge_stores(self, origl20nfile, translatedl20nfile):
        """converts two .l20n files to a .po file..."""
        target_store = po.pofile()
        translatedl20nfile.makeindex()
        for l20nunit in origl20nfile.units:
            pounit = self.convert_l20nunit(l20nunit)
            target_store.addunit(pounit)
            for location in pounit.getlocations():
                if location in translatedl20nfile.id_index:
                    l20nunit = translatedl20nfile.id_index[location]
                    pounit.target = l20nunit.target
        target_store.removeduplicates(self.duplicatestyle)
        return target_store


def convertl20n(inputfile, outputfile, templatefile,
                pot=False, duplicatestyle="msgctxt"):
    inputstore = l20n.l20nfile(inputfile)
    convertor = l20n2po(blankmsgstr=pot, duplicatestyle=duplicatestyle)
    if templatefile is None:
        outputstore = convertor.convert_store(inputstore)
    else:
        templatestore = l20n.l20nfile(templatefile)
        outputstore = convertor.merge_stores(templatestore, inputstore)
    if outputstore.isempty():
        return 0
    outputstore.serialize(outputfile)
    return 1


formats = {
    "ftl": ("po", convertl20n),
    ("ftl", "ftl"): ("po", convertl20n),
    "l20n": ("po", convertl20n),
    ("l20n", "l20n"): ("po", convertl20n),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()
