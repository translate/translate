#
# Copyright 2007 Zuza Software Foundation
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
import os
from os import path
from subprocess import call

import pytest
from lxml import etree


@pytest.fixture(autouse=True, scope="module")
def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield None
    os.chdir(request.config.invocation_params.dir)


@pytest.fixture(scope="module")
def xmllint():
    schema = etree.XMLSchema(etree.parse("xliff-core-1.1.xsd"))
    return lambda fullpath: schema.validate(etree.parse(fullpath))


def find_files(base, check_ext):
    for dirpath, _dirnames, filenames in os.walk(base):
        for filename in filenames:
            fullpath = path.join(dirpath, filename)
            _namepath, ext = path.splitext(fullpath)
            if check_ext == ext:
                yield fullpath


def test_open_office_to_xliff(xmllint):
    assert call(["oo2xliff", "en-US.sdf", "-l", "fr", "fr"]) == 0
    for filepath in find_files("fr", ".xlf"):
        assert xmllint(filepath)
    cleardir("fr")


def test_po_to_xliff(xmllint):
    OUTPUT = "af-pootle.xlf"
    assert call(["po2xliff", "af-pootle.po", OUTPUT]) == 0
    assert xmllint(OUTPUT)


def cleardir(testdir):
    """Removes the test directory."""
    if os.path.exists(testdir):
        for dirpath, subdirs, filenames in os.walk(testdir, topdown=False):
            for name in filenames:
                os.remove(os.path.join(dirpath, name))
            for name in subdirs:
                os.rmdir(os.path.join(dirpath, name))
    if os.path.exists(testdir):
        os.rmdir(testdir)
    assert not os.path.exists(testdir)
