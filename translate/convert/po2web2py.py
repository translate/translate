# -*- coding: utf-8 -*-
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

"""Convert GNU/gettext PO files to web2py translation dictionaries (.py).

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/web2py2po.html
for examples and usage instructions.
"""

from io import BytesIO

from translate.convert import convert
from translate.storage import factory


class po2pydict(object):

    def __init__(self):
        return

    def convertstore(self, inputstore, includefuzzy):
        str_obj = BytesIO()

        mydict = dict()
        for unit in inputstore.units:
            if unit.isheader():
                continue
            if unit.istranslated() or (includefuzzy and unit.isfuzzy()):
                mydict[unit.source] = unit.target
            else:
                mydict[unit.source] = unit.source
                # The older convention is to prefix with "*** ":
                #mydict[unit.source] = '*** ' + unit.source

        str_obj.write('{\n')
        for source_str in mydict:
            str_obj.write("%s:%s,\n" % (repr(str(source_str)), repr(str(mydict[source_str]))))
        str_obj.write('}\n')
        str_obj.seek(0)
        return str_obj


def convertpy(inputfile, outputfile, templatefile=None, includefuzzy=False,
              outputthreshold=None):
    inputstore = factory.getobject(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    convertor = po2pydict()
    outputstring = convertor.convertstore(inputstore, includefuzzy)
    outputfile.write(outputstring.read())
    return 1


def main(argv=None):
    formats = {("po", "py"): ("py", convertpy), ("po"): ("py", convertpy)}
    parser = convert.ConvertOptionParser(formats, usetemplates=False, description=__doc__)
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
