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

    SourceStoreClass = txt.TxtFile

    def __init__(self, input_file, output_file, duplicate_style="msgctxt",
                 encoding="utf-8", flavour=None):
        """Initialize the converter."""
        self.duplicate_style = duplicate_style

        self.output_file = output_file
        self.source_store = self.SourceStoreClass(input_file,
                                                  encoding=encoding,
                                                  flavour=flavour)

    def convertstore(self):
        """Convert a single source format file to a target format file."""
        self.target_store = po.pofile()
        targetheader = self.target_store.header()
        targetheader.addnote("extracted from %s" % self.source_store.filename,
                             "developer")

        for txtunit in self.source_store.units:
            newunit = self.target_store.addsourceunit(txtunit.source)
            newunit.addlocations(txtunit.getlocations())
        self.target_store.removeduplicates(self.duplicate_style)

        if self.target_store.isempty():
            return 0
        self.target_store.serialize(self.output_file)
        return 1


def run_converter(inputfile, outputfile, templates, duplicatestyle="msgctxt",
                  encoding="utf-8", flavour=None):
    """Wrapper around converter."""
    convertor = txt2po(inputfile, outputfile, duplicate_style=duplicatestyle,
                       encoding=encoding, flavour=flavour)
    return convertor.convertstore()


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
