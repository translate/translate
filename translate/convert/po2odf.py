#
# Copyright 2004-2014 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

"""
Convert Gettext PO localization files to OpenDocument (ODF) files.

See: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/odf2po.html
for examples and usage instructions.
"""

from typing import IO

from translate.convert import convert
from translate.convert.xliff2odf import translate_odf, write_odf
from translate.storage.odf_shared import ODF_EXTENSIONS
from translate.storage.xml_extract.generate import get_po_source_target_doms


def convertpo(
    input_file: IO[bytes], output_file: IO[bytes], template: IO[bytes]
) -> bool:
    """Create a translated ODF using an ODF template and a PO file."""
    dom_trees = translate_odf(
        template,
        input_file,
        get_po_source_target_doms,
        include_fuzzy=False,
    )
    write_odf(template, output_file, dom_trees)
    output_file.close()
    return True


def main(argv=None) -> None:
    formats = {
        ("po", extension): (extension, convertpo) for extension in ODF_EXTENSIONS
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.run(argv)


if __name__ == "__main__":
    main()
