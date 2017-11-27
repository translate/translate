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

"""Convert Gettext PO localization files to Mozilla .lang files.
"""

from translate.convert import convert
from translate.storage import mozilla_lang, po


class po2lang(object):
    """Convert a PO file to a Mozilla .lang file."""

    def __init__(self, mark_active=True):
        """Initialize the converter."""
        self.mark_active = mark_active

    def convert_store(self, source_store, include_fuzzy=False):
        """Convert a single source format file to a target format file."""
        self.include_fuzzy = include_fuzzy
        self.source_store = source_store
        self.target_store = mozilla_lang.LangStore(mark_active=self.mark_active)

        for source_unit in self.source_store.units:
            if source_unit.isheader() or not source_unit.istranslatable():
                continue
            target_unit = self.target_store.addsourceunit(source_unit.source)
            if self.include_fuzzy or not source_unit.isfuzzy():
                target_unit.target = source_unit.target
            else:
                target_unit.target = ""
            if source_unit.getnotes('developer'):
                target_unit.addnote(source_unit.getnotes('developer'), 'developer')
        return self.target_store


def run_converter(inputfile, outputfile, templates, includefuzzy=False,
                  mark_active=True, outputthreshold=None):
    """Wrapper around converter."""
    inputstore = po.pofile(inputfile)

    if not convert.should_output_store(inputstore, outputthreshold):
        return 0

    if inputstore.isempty():
        return 0

    convertor = po2lang(mark_active)
    outputstore = convertor.convert_store(inputstore, includefuzzy)
    outputstore.serialize(outputfile)
    return 1


formats = {
    "po": ("lang", run_converter),
    ("po", "lang"): ("lang", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_option(
        "", "--mark-active", dest="mark_active", default=False,
        action="store_true", help="mark the file as active")
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.passthrough.append("mark_active")
    parser.run(argv)


if __name__ == '__main__':
    main()
