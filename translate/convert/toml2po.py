#
# Copyright 2025 translate-toolkit contributors
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
Convert TOML files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/toml2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import po, toml


class toml2po:
    """
    Convert one or two TOML files to a single PO file.

    Extracts translatable strings from TOML configuration files and creates
    Gettext PO files for translation. Supports both plain TOML and Go i18n
    TOML formats with plurals.
    """

    SourceStoreClass = toml.TOMLFile
    TargetStoreClass = po.pofile
    TargetUnitClass = po.pounit

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        blank_msgstr=False,
        duplicate_style="msgctxt",
    ):
        """Initialize the converter."""
        self.blank_msgstr = blank_msgstr
        self.duplicate_style = duplicate_style

        self.extraction_msg = None
        self.output_file = output_file
        self.source_store = self.SourceStoreClass(input_file)
        self.target_store = self.TargetStoreClass()
        self.template_store = None

        if template_file is not None:
            self.template_store = self.SourceStoreClass(template_file)

    def convert_unit(self, unit):
        """Convert a TOML unit to a PO unit with location and developer notes."""
        target_unit = self.TargetUnitClass(encoding="UTF-8")
        target_unit.setid(unit.getid())
        target_unit.addlocation(unit.getid())
        target_unit.addnote(unit.getnotes(), "developer")
        target_unit.source = unit.source
        return target_unit

    def convert_store(self):
        """
        Convert a single TOML file to PO format.

        Used when only one TOML file is provided (extraction mode).
        """
        self.extraction_msg = f"extracted from {self.source_store.filename}"

        for source_unit in self.source_store.units:
            self.target_store.addunit(self.convert_unit(source_unit))

    def merge_stores(self):
        """
        Merge template and translated TOML files into PO format.

        Template provides the structure, source file provides translations.
        """
        self.extraction_msg = f"extracted from {self.template_store.filename}, {self.source_store.filename}"

        self.source_store.makeindex()
        for template_unit in self.template_store.units:
            target_unit = self.convert_unit(template_unit)

            for location in target_unit.getlocations():
                if location in self.source_store.id_index:
                    source_unit = self.source_store.id_index[location]
                    target_unit.target = source_unit.target
            self.target_store.addunit(target_unit)

    def run(self):
        """Run the conversion process, returning 1 if successful or 0 if empty."""
        if self.template_store is None:
            self.convert_store()
        else:
            self.merge_stores()

        if self.extraction_msg:
            self.target_store.header().addnote(self.extraction_msg, "developer")

        self.target_store.removeduplicates(self.duplicate_style)

        if self.target_store.isempty():
            return 0

        self.target_store.serialize(self.output_file)
        return 1


def run_converter(
    input_file, output_file, template_file=None, pot=False, duplicatestyle="msgctxt"
):
    """Wrapper around converter for command-line usage."""
    return toml2po(
        input_file,
        output_file,
        template_file,
        blank_msgstr=pot,
        duplicate_style=duplicatestyle,
    ).run()


formats = {
    "toml": ("po", run_converter),
    ("toml", "toml"): ("po", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, usepots=True, description=__doc__
    )
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == "__main__":
    main()
