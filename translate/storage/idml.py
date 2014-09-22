#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Zuza Software Foundation
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

import zipfile


# Tags to be extracted as placeables (tags that are within translatable texts).
INLINE_ELEMENTS = []


# Skipping one of these tags doesn't imply nested acceptable tags are not
# extracted.
NO_TRANSLATE_ELEMENTS = [
    ('http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging', 'Story'),

    ('', 'Story'),  # This is a different Story tag than the one above.
]


def open_idml(filename):
    z = zipfile.ZipFile(filename, 'r')
    # Return a dictionary containing all the files inside the Stories
    # subdirectory, being the keys the filenames (for example
    # 'Stories/Story_u49f.xml' and the values the strings for those files.
    return dict((filename, z.read(filename))
                for filename in z.namelist() if filename.startswith('Stories/'))
