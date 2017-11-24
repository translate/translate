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

"""Convert Gettext PO localization files to plain text (.txt) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/txt2po.html
for examples and usage instructions.
"""

import textwrap

from translate.convert import convert
from translate.storage import factory


class po2txt(object):
    """po2txt can take a po file and generate txt.

    best to give it a template file otherwise will just concat msgstrs
    """

    def __init__(self, wrap=None):
        """Initialize the converter."""
        self.wrap = wrap

    def wrapmessage(self, message):
        """rewraps text as required"""
        if self.wrap is None:
            return message
        return "\n".join([textwrap.fill(line, self.wrap, replace_whitespace=False)
                          for line in message.split("\n")])

    def convert_store(self, inputstore, includefuzzy):
        """Convert a source file to a target file."""
        txtresult = ""
        for unit in inputstore.units:
            if not unit.istranslatable():
                continue
            if unit.istranslated() or (includefuzzy and unit.isfuzzy()):
                txtresult += self.wrapmessage(unit.target) + "\n\n"
            else:
                txtresult += self.wrapmessage(unit.source) + "\n\n"
        return txtresult.rstrip()

    def merge_stores(self, inputstore, templatetext, includefuzzy):
        """Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        txtresult = templatetext
        # TODO: make a list of blocks of text and translate them individually
        # rather than using replace
        for unit in inputstore.units:
            if not unit.istranslatable():
                continue
            if not unit.isfuzzy() or includefuzzy:
                txtsource = unit.source
                txttarget = self.wrapmessage(unit.target)
                if unit.istranslated():
                    txtresult = txtresult.replace(txtsource, txttarget)
        return txtresult


def run_converter(inputfile, outputfile, templatefile, wrap=None,
                  includefuzzy=False, encoding='utf-8', outputthreshold=None):
    """Wrapper around converter."""
    inputstore = factory.getobject(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return False

    convertor = po2txt(wrap=wrap)

    if templatefile is None:
        outputstring = convertor.convert_store(inputstore, includefuzzy)
    else:
        templatestring = templatefile.read().decode(encoding)
        outputstring = convertor.merge_stores(inputstore, templatestring, includefuzzy)

    outputfile.write(outputstring.encode('utf-8'))
    return True


formats = {
    ("po", "txt"): ("txt", run_converter),
    ("po"): ("txt", run_converter),
    ("xlf", "txt"): ("txt", run_converter),
    ("xlf"): ("txt", run_converter),
    ("xliff", "txt"): ("txt", run_converter),
    ("xliff"): ("txt", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_option(
        "", "--encoding", dest="encoding", default='utf-8', type="string",
        help="The encoding of the template file (default: UTF-8)")
    parser.passthrough.append("encoding")
    parser.add_option(
        "-w", "--wrap", dest="wrap", default=None, type="int",
        help="set number of columns to wrap text at", metavar="WRAP")
    parser.passthrough.append("wrap")
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
