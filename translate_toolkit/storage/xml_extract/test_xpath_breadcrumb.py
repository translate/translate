#
# Copyright 2002-2006 Zuza Software Foundation
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
#

from . import xpath_breadcrumb


def test_breadcrumb():
    xb = xpath_breadcrumb.XPathBreadcrumb()
    assert xb.xpath == ""

    xb.start_tag("a")
    assert xb.xpath == "a[0]"

    xb.start_tag("b")
    assert xb.xpath == "a[0]/b[0]"
    xb.end_tag()

    assert xb.xpath == "a[0]"

    xb.start_tag("b")
    assert xb.xpath == "a[0]/b[1]"
    xb.end_tag()

    assert xb.xpath == "a[0]"
    xb.end_tag()

    assert xb.xpath == ""

    xb.start_tag("a")
    assert xb.xpath == "a[1]"
