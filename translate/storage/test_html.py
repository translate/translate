#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Tests for the HTML classes"""

from translate.storage import html

def test_guess_encoding():
    """Read an encoding header to guess the encoding correctly"""
    h = html.htmlfile()
    h.guess_encoding('''<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=UTF-8">''') == "UTF-8"

def test_strip_html():
    assert html.strip_html("<a>Something</a>") == "Something"
    assert html.strip_html("You are <a>Something</a>") == "You are <a>Something</a>"
