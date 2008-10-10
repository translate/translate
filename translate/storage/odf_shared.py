#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
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
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import xml_extract

def make_tag(uri, raw_tag):
    return u"{%s}%s" % (uri, raw_tag)

# From itools
# This information is derived from Itaapy's itools and can be seen at
# http://git.hforge.org/?p=itools.git;a=blob;f=odf/schema.py;h=1e2b2e145b55a1b73e4fd22d7610acaed3a88c38;hb=HEAD
text_uri = u'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
office_uri = u'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
style_uri = u'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
table_uri = u'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
draw_uri = u'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
fo_uri = u'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
meta_uri = u'urn:oasis:names:tc:opendocument:xmlns:meta:1.0'
svg_uri = u'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'
dr3d_uri = u'urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0'
form_uri = u'urn:oasis:names:tc:opendocument:xmlns:form:1.0'
script_uri = u'urn:oasis:names:tc:opendocument:xmlns:script:1.0'
ooo_uri = u'http://openoffice.org/2004/office'
ooow_uri = u'http://openoffice.org/2004/writer'
oooc_uri = u'http://openoffice.org/2004/calc'
number_uri = u'urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0'
anim_uri = u'urn:oasis:names:tc:opendocument:xmlns:animation:1.0'
chart_uri = u'urn:oasis:names:tc:opendocument:xmlns:chart:1.0'
config_uri = u'urn:oasis:names:tc:opendocument:xmlns:config:1.0'
manifest_uri = u'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'
presentation_uri = u'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0'
smil_uri = u'urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0'

odf_namespace_table = set([
    make_tag(text_uri, u'p'), 
    make_tag(text_uri, u'h'),
    make_tag(text_uri, u'span')
])

odf_inline_placeables_table = {
    make_tag(text_uri, u'span'): u'span'
}

odf_placables_table = {
    make_tag(text_uri, u'note'): u'footnote',
    make_tag(draw_uri, u'frame'): u'frame',
}

