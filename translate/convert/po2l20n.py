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

"""Convert Gettext PO localization files to .ftl files.
"""

import logging

from translate.convert import convert
from translate.storage import l20n, po


logger = logging.getLogger(__name__)


class po2l20n(object):

    SourceStoreClass = po.pofile
    TargetStoreClass = l20n.l20nfile
    TargetUnitClass = l20n.l20nunit

    def __init__(self, input_file, output_file, template_file=None,
                 include_fuzzy=False, output_threshold=None):

        if template_file is None:
            raise ValueError("must have template file for ftl files")

        self.source_store = self.SourceStoreClass(input_file)
        self.output_file = output_file
        self.template_store = self.TargetStoreClass(template_file)
        self.include_fuzzy = include_fuzzy
        self.output_threshold = output_threshold

    def convert_unit(self, unit):
        use_target = (unit.istranslated()
                      or unit.isfuzzy() and self.include_fuzzy)
        l20n_unit_value = unit.target if use_target else unit.source
        l20n_unit = self.TargetUnitClass(
            source=l20n_unit_value,
            id=unit.getlocations()[0],
            comment=unit.getnotes("developer")
        )
        return l20n_unit

    def convert_store(self):
        self.target_store = self.TargetStoreClass()
        self.source_store.makeindex()

        for l20nunit in self.template_store.units:
            l20nunit_id = l20nunit.getid()

            if l20nunit_id in self.source_store.locationindex:
                po_unit = self.source_store.locationindex[l20nunit_id]
                newunit = self.convert_unit(po_unit)
                self.target_store.addunit(newunit)

        return self.target_store

    def run(self):
        self.should_output_store = convert.should_output_store(
            self.source_store, self.output_threshold
        )
        if not self.should_output_store:
            return False

        self.convert_store().serialize(self.output_file)
        return True


def convertl20n(inputfile, outputfile, templatefile, includefuzzy=False,
                outputthreshold=None):
    return po2l20n(inputfile, outputfile, templatefile, includefuzzy,
                   outputthreshold).run()


formats = {
    ("po", "ftl"): ("ftl", convertl20n),
    "po": ("ftl", convertl20n),
}


def main(argv=None):
    # handle command line options
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == '__main__':
    main()
