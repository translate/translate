#
# Copyright 2007 Zuza Software Foundation
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
from pathlib import Path
from subprocess import call

import pytest
from lxml import etree

from translate.misc.xml_helpers import parse_xml_file

TEST_DIR = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def xmllint():
    schema = etree.XMLSchema(parse_xml_file(TEST_DIR / "xliff-core-1.1.xsd"))
    return lambda fullpath: schema.validate(parse_xml_file(fullpath))


def test_open_office_to_xliff(xmllint, tmp_path: Path) -> None:
    output_dir = tmp_path / "fr"

    assert (
        call(["oo2xliff", str(TEST_DIR / "en-US.sdf"), "-l", "fr", str(output_dir)])
        == 0
    )

    xliff_files = list(output_dir.rglob("*.xliff"))
    assert xliff_files
    for filepath in xliff_files:
        assert xmllint(filepath)


def test_po_to_xliff(xmllint, tmp_path: Path) -> None:
    output = tmp_path / "af-pootle.xlf"

    assert call(["po2xliff", str(TEST_DIR / "af-pootle.po"), str(output)]) == 0
    assert xmllint(output)
