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
Convert WiX Localization (.wxl) files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/wxl2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, wxl


class wxl2po:
    """Convert a single WXL file to a single PO file."""

    SourceStoreClass = wxl.WxlFile
    TargetStoreClass = po.pofile
    TargetUnitClass = po.pounit

    def __init__(self, inputfile, outputfile, templatefile=None) -> None:
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.source_store = self.SourceStoreClass(inputfile)
        self.target_store = self.TargetStoreClass()

    def convert_unit(self, unit):
        """Convert a WXL unit to a PO unit."""
        return self.TargetUnitClass.buildfromunit(unit)

    def convert_store(self) -> None:
        """Convert the source store to a PO file."""
        for source_unit in self.source_store.units:
            self.target_store.addunit(self.convert_unit(source_unit))

    def run(self) -> int:
        """Run the converter."""
        self.convert_store()
        if self.target_store.isempty():
            return 0
        self.target_store.serialize(self.outputfile)
        return 1


def run_converter(inputfile, outputfile, templatefile=None):
    """Wrapper around the converter."""
    return wxl2po(inputfile, outputfile, templatefile).run()


formats = {
    "wxl": ("po", run_converter),
}


def main(argv=None) -> None:
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == "__main__":
    main()
