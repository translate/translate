#
# Copyright 2004-2014 Zuza Software Foundation
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
Convert Gettext PO localization files to OpenDocument (ODF) files.

This converter combines the functionality of po2xliff and xliff2odf to provide
a direct conversion from PO files to ODF files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/
for examples and usage instructions.
"""

from io import BytesIO
from typing import BinaryIO

from translate.convert import convert, po2xliff, xliff2odf
from translate.storage import po


def convertpo(input_file: BinaryIO, output_file: BinaryIO, template: BinaryIO) -> int:
    """Create a translated ODF using an ODF template and a PO file."""
    # Read the PO file
    inputstore = po.pofile(input_file)
    if inputstore.isempty():
        return 0

    # Convert PO to XLIFF
    convertor = po2xliff.po2xliff()
    xliff_bytes = convertor.convertstore(inputstore, None)

    # Convert XLIFF to ODF
    xliff_file = BytesIO(xliff_bytes)
    xliff2odf.convertxliff(xliff_file, output_file, template)
    return 1


def main(argv=None):
    formats = {
        ("po", "odt"): ("odt", convertpo),  # Text
        ("po", "ods"): ("ods", convertpo),  # Spreadsheet
        ("po", "odp"): ("odp", convertpo),  # Presentation
        ("po", "odg"): ("odg", convertpo),  # Drawing
        ("po", "odc"): ("odc", convertpo),  # Chart
        ("po", "odf"): ("odf", convertpo),  # Formula
        ("po", "odi"): ("odi", convertpo),  # Image
        ("po", "odm"): ("odm", convertpo),  # Master Document
        ("po", "ott"): ("ott", convertpo),  # Text template
        ("po", "ots"): ("ots", convertpo),  # Spreadsheet template
        ("po", "otp"): ("otp", convertpo),  # Presentation template
        ("po", "otg"): ("otg", convertpo),  # Drawing template
        ("po", "otc"): ("otc", convertpo),  # Chart template
        ("po", "otf"): ("otf", convertpo),  # Formula template
        ("po", "oti"): ("oti", convertpo),  # Image template
        ("po", "oth"): ("oth", convertpo),  # Web page template
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.run(argv)


if __name__ == "__main__":
    main()
