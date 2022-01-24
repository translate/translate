#
# Copyright 2009-2010 Zuza Software Foundation
#
# This file is part of translate.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#

"""Convert web2py translation dictionaries (.py) to GNU/gettext PO files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/web2py2po.html
for examples and usage instructions.
"""

from translate.storage import po


class web2py2po:
    def __init__(self, pofile=None, duplicatestyle="msgctxt"):
        self.mypofile = pofile
        self.duplicatestyle = duplicatestyle

    @staticmethod
    def convertunit(source_str, target_str):
        pounit = po.pounit(encoding="UTF-8")
        pounit.settypecomment("python-format")
        pounit.source = source_str
        if target_str:
            pounit.target = target_str
        return pounit

    def convertstore(self, mydict):
        targetheader = self.mypofile.header()
        targetheader.addnote("extracted from web2py", "developer")

        for source_str in mydict.keys():
            target_str = mydict[source_str]
            if target_str == source_str.replace("@markmin\x01", ""):
                # a convention with new (untranslated) web2py files
                target_str = ""
            pounit = self.convertunit(source_str, target_str)
            self.mypofile.addunit(pounit)

        self.mypofile.removeduplicates(self.duplicatestyle)

        return self.mypofile


def convertpy(inputfile, outputfile, encoding="UTF-8", duplicatestyle="msgctxt"):

    new_pofile = po.pofile()
    convertor = web2py2po(new_pofile)

    mydict = eval(inputfile.read())
    if not isinstance(mydict, dict):
        return 0

    outputstore = convertor.convertstore(mydict)

    if outputstore.isempty():
        return 0

    outputstore.serialize(outputfile)
    return 1


def main(argv=None):
    from translate.convert import convert

    formats = {("py", "po"): ("po", convertpy), ("py", None): ("po", convertpy)}
    parser = convert.ConvertOptionParser(
        formats, usetemplates=False, usepots=True, description=__doc__
    )
    parser.add_duplicates_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
