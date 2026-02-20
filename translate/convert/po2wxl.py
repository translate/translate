#
# Copyright 2025 Translate Authors
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

"""
Convert Gettext PO localization files to WiX Localization (.wxl) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/wxl2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, wxl


class po2wxl:
    """Convert a PO file to a WXL file, optionally merging into a template."""

    TargetStoreClass = wxl.WxlFile
    TargetUnitClass = wxl.WxlUnit

    def __init__(self, inputfile, outputfile, templatefile=None) -> None:
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.templatefile = templatefile
        self.source_store = po.pofile(inputfile)
        self.target_store = self.TargetStoreClass(templatefile)

    def convert_unit(self, unit):
        """Convert a PO unit to a WXL unit."""
        target_unit = self.TargetUnitClass(source=unit.source)
        if unit.istranslated() or not unit.source:
            target_unit.target = unit.target
        else:
            target_unit.target = unit.source
        return target_unit

    def convert_store(self) -> None:
        """Convert the PO store to a WXL file."""
        for unit in self.source_store.units:
            key = unit.source
            if not key:
                continue
            target_unit = self.target_store.findid(key)
            if target_unit is None:
                target_unit = self.convert_unit(unit)
                self.target_store.addunit(target_unit)
            elif unit.istranslated():
                target_unit.target = unit.target

    def run(self) -> int:
        """Run the converter."""
        self.convert_store()
        if self.target_store.isempty():
            return 0
        self.target_store.serialize(self.outputfile)
        return 1


def run_converter(inputfile, outputfile, templatefile=None):
    """Wrapper around the converter."""
    return po2wxl(inputfile, outputfile, templatefile).run()


formats = {
    "po": ("wxl", run_converter),
    ("po", "wxl"): ("wxl", run_converter),
}


def main(argv=None) -> None:
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.run(argv)


if __name__ == "__main__":
    main()
