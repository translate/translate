# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
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

"""Convert Gettext PO localization files to .ini files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ini2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import ini, po


class po2ini(object):
    """Convert a PO file and a template INI file to a INI file."""

    MissingTemplateMessage = "A template INI file must be provided."

    def __init__(self, inputstore, template_file=None, include_fuzzy=False,
                 output_threshold=None, dialect="default"):
        """Initialize the converter."""
        if template_file is None:
            raise ValueError(self.MissingTemplateMessage)

        self.include_fuzzy = include_fuzzy

        self.template_store = ini.inifile(template_file, dialect=dialect)
        self.source_store = inputstore

    def merge_stores(self):
        """Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        self.source_store.makeindex()
        for template_unit in self.template_store.units:
            for location in template_unit.getlocations():
                if location in self.source_store.locationindex:
                    source_unit = self.source_store.locationindex[location]
                    if source_unit.isfuzzy() and not self.include_fuzzy:
                        template_unit.target = template_unit.source
                    else:
                        template_unit.target = source_unit.target
                else:
                    template_unit.target = template_unit.source
        return bytes(self.template_store)


def run_converter(inputfile, outputfile, templatefile=None, includefuzzy=False,
                  dialect="default", outputthreshold=None):
    """Wrapper around converter."""
    inputstore = po.pofile(inputfile)
    if not convert.should_output_store(inputstore, outputthreshold):
        return 0

    convertor = po2ini(inputstore, templatefile, includefuzzy, outputthreshold,
                       dialect)
    outputstring = convertor.merge_stores()
    outputfile.write(outputstring)
    return 1


def convertisl(inputfile, outputfile, templatefile=None, includefuzzy=False,
               dialect="inno", outputthreshold=None):
    run_converter(inputfile, outputfile, templatefile, includefuzzy, dialect,
                  outputthreshold)


formats = {
    ("po", "ini"): ("ini", run_converter),
    ("po", "isl"): ("isl", convertisl),
}


def main(argv=None):
    import sys
    if sys.version_info[0] == 3:
        print("Translate Toolkit doesn't yet support converting to INI in "
              "Python 3.")
        sys.exit()

    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
