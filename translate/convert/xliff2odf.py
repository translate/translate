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

"""convert OpenDocument (ODF) files to Gettext PO localization files"""

import cStringIO
import zipfile
import re

import lxml.etree as etree

from translate.storage import factory
from translate.storage.xml_extract import unit_tree
from translate.storage.xml_extract import extract
from translate.storage.xml_extract import generate
from translate.storage import odf_shared

def first_child(unit_node):
    return unit_node.children.values()[0]

def translate_odf(template, input_file):
    def open_odf(filename):
        z = zipfile.ZipFile(filename, 'r')
        return {'content.xml': z.read("content.xml")}
  
    def load_dom_trees(template):
        odf_data = open_odf(template)
        return dict((filename, etree.parse(cStringIO.StringIO(data))) for filename, data in odf_data.iteritems())
    
    def load_unit_tree(input_file):
        store = factory.getobject(input_file)
        return {'content.xml': unit_tree.build_unit_tree(store)}
    
    def translate_dom_trees(unit_trees, dom_trees):
        make_parse_state = lambda: extract.ParseState(odf_shared.no_translate_content_elements, odf_shared.inline_elements)
        for filename, dom_tree in dom_trees.iteritems():
            file_unit_tree = unit_trees[filename]
            generate.apply_translations(dom_tree.getroot(), file_unit_tree.children.values()[0], generate.replace_dom_text(make_parse_state))
        return dom_trees

    dom_trees = load_dom_trees(template)
    unit_trees = load_unit_tree(input_file)
    return translate_dom_trees(unit_trees, dom_trees)

def write_odf(template, output_file, dom_trees):
    def copy_odf(input_file, output_file, exclusion_list):
        input_zip  = zipfile.ZipFile(input_file,  'r')
        output_zip = zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED)
        for name in [name for name in input_zip.namelist() if name not in exclusion_list]:
            output_zip.writestr(name, input_zip.read(name))
        return output_zip

    def write_content_to_odf(output_zip, dom_trees):
        for filename, dom_tree in dom_trees.iteritems():
            output_zip.writestr(filename, etree.tostring(dom_tree))

    output_zip = copy_odf(template, output_file, dom_trees.keys())
    write_content_to_odf(output_zip, dom_trees)

def convertxliff(input_file, output_file, template):
    """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
    dom_trees = translate_odf(template, input_file)
    write_odf(template, output_file, dom_trees)
    return True

def main(argv=None):
    from translate.convert import convert
    formats = {"xlf": ("odt", convertxliff)}
    parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
    parser.run(argv)

if __name__ == '__main__':
    main()
