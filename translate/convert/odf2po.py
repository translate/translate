#
# Copyright 2026 Zuza Software Foundation
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

"""Convert OpenDocument (ODF) files to Gettext PO localization files."""

from io import BytesIO

from translate.convert import convert
from translate.storage import factory, po
from translate.storage.odf_io import open_odf
from translate.storage.odf_shared import (
    ODF_INPUT_EXTENSIONS,
    inline_elements,
    no_translate_content_elements,
)
from translate.storage.xml_extract.extract import (
    IdMaker,
    ParseState,
    build_store,
    make_postore_adder,
)


def convertodf(inputfile, outputfile, templates) -> bool:
    """Convert an ODF package to PO."""
    store = factory.getobject(outputfile)
    if not isinstance(store, po.pofile):
        raise TypeError("ODF extraction requires a PO output store")
    id_maker = IdMaker()

    for filename, data in open_odf(inputfile).items():
        parse_state = ParseState(no_translate_content_elements, inline_elements)
        build_store(
            BytesIO(data),
            store,
            parse_state,
            store_adder=make_postore_adder(store, id_maker, filename),
            collect_ids=False,
        )

    store.removeduplicates("msgctxt")
    store.save()
    return True


def main(argv=None) -> None:
    formats = dict.fromkeys(ODF_INPUT_EXTENSIONS, ("po", convertodf))
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == "__main__":
    main()
