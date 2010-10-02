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
    #assert html.strip_html("<b>You</b> are <a>Something</a>") == "<b>You</b> are <a>Something</a>"
    assert html.strip_html('<strong><font class="headingwhite">Projects</font></strong>') == "Projects"
    assert html.strip_html("<strong>Something</strong> else.") == "<strong>Something</strong> else."
    assert html.strip_html("<h1><strong>Something</strong> else.</h1>") == "<strong>Something</strong> else."
    assert html.strip_html('<h1 id="moral"><strong>We believe</strong> that the internet should be public, open and accessible.</h1>') == "<strong>We believe</strong> that the internet should be public, open and accessible."
    #assert html.strip_html('<h3><a href="http://www.firefox.com/" class="producttitle"><img src="../images/product-firefox-50.png" width="50" height="50" alt="" class="featured" style="display: block; margin-bottom: 30px;" /><strong>Firefox for Desktop</strong></a></h3>') == 'Firefox for Desktop'

def test_strip_html_with_pi():
    h = html.htmlfile()
    assert html.strip_html(h.pi_escape('<a href="<?$var?>">Something</a>')) == "Something"
    assert html.strip_html(h.pi_escape('<a href="<?=($a < $b ? $foo : ($b > c ? $bar : $cat))?>">Something</a>')) == "Something"

def test_normalize_html():
    assert html.normalize_html("<p>Simple  double  spaced</p>") == "<p>Simple double spaced</p>"

def test_pi_escaping():
    h = html.htmlfile()
    assert h.pi_escape('<a href="<?=($a < $b ? $foo : ($b > c ? $bar : $cat))?>">') == '<a href="<?=($a %lt; $b ? $foo : ($b %gt; c ? $bar : $cat))?>">'
