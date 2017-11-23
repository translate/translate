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

"""Convert plain text (.txt) files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/txt2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, txt


class txt2po(object):
    """Convert one plain text (.txt) file to a single PO file."""

    def __init__(self, output_file, duplicate_style="msgctxt"):
        """Initialize the converter."""
        self.duplicate_style = duplicate_style

        self.output_file = output_file

    def convertstore(self, thetxtfile):
        """Convert a single source format file to a target format file."""
        self.target_store = po.pofile()
        targetheader = self.target_store.header()
        targetheader.addnote("extracted from %s" % thetxtfile.filename,
                             "developer")

        for txtunit in thetxtfile.units:
            newunit = self.target_store.addsourceunit(txtunit.source)
            newunit.addlocations(txtunit.getlocations())
        self.target_store.removeduplicates(self.duplicate_style)
        return self.target_store


def run_converter(inputfile, outputfile, templates, duplicatestyle="msgctxt",
                  encoding="utf-8", flavour=None):
    """Wrapper around converter."""
    inputstore = txt.TxtFile(inputfile, encoding=encoding, flavour=flavour)
    convertor = txt2po(outputfile, duplicate_style=duplicatestyle)
    outputstore = convertor.convertstore(inputstore)
    if outputstore.isempty():
        return 0
    outputstore.serialize(outputfile)
    return 1


formats = {
    "txt": ("po", run_converter),
    "*": ("po", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usepots=True,
                                         description=__doc__)
    parser.add_option("", "--encoding", dest="encoding", default='utf-8',
                      type="string",
                      help="The encoding of the input file (default: UTF-8)")
    parser.passthrough.append("encoding")
    parser.add_option("", "--flavour", dest="flavour", default="plain",
                      type="choice",
                      choices=["plain", "dokuwiki", "mediawiki"],
                      help=("The flavour of text file: plain (default), "
                            "dokuwiki, mediawiki"),
                      metavar="FLAVOUR")
    parser.passthrough.append("flavour")
    parser.add_duplicates_option()
    parser.run(argv)
