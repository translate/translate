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
Convert XLIFF translation files to OpenDocument (ODF) files.

See: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/odf2xliff.html
for examples and usage instructions.
"""

from io import BytesIO

from lxml import etree

from translate.convert import convert
from translate.misc.xml_helpers import parse_xml_file
from translate.storage import factory, xliff
from translate.storage.odf_io import ODFPackage, open_odf
from translate.storage.odf_shared import (
    ODF_EXTENSIONS,
    inline_elements,
    no_translate_content_elements,
)
from translate.storage.xml_extract import misc
from translate.storage.xml_extract.extract import ParseState, compact_tag, reverse_map
from translate.storage.xml_extract.generate import (
    apply_translations,
    get_xliff_source_target_doms,
    replace_dom_text,
)
from translate.storage.xml_extract.unit_tree import XPathTree, build_unit_tree


def translate_odf(
    template,
    input_file,
    dom_retriever=get_xliff_source_target_doms,
    *,
    include_fuzzy: bool = True,
):
    def load_dom_trees(template):
        """
        Return a dict with translatable files in the template ODF package.

        The keys are the filenames inside the ODF package, and the values are
        the etrees for each of those translatable files.
        """
        odf_data = open_odf(template)
        return {
            filename: parse_xml_file(BytesIO(data), collect_ids=False)
            for filename, data in odf_data.items()
        }

    def root_name(dom_tree):
        root = dom_tree.getroot()
        namespace, tag = misc.parse_tag(root.tag)
        return compact_tag(reverse_map(root.nsmap), namespace, tag)

    def load_unit_trees(input_file, dom_trees):
        """
        Return a dict with the translations grouped by files ODF package.

        The keys are the filenames inside the template ODF package, and the
        values are XPathTree instances for each of those files.
        """
        store = factory.getobject(input_file)
        is_xliff = isinstance(store, xliff.xlifffile)
        store_filenames = set(store.getfilenames()) if is_xliff else set()
        has_member_files = bool(store_filenames.intersection(dom_trees))
        shared_tree = None
        if is_xliff and not has_member_files:
            # Older odf2xliff releases stored every XML member in one <file>.
            shared_tree = build_unit_tree(
                store,
                require_target=True,
                include_fuzzy=include_fuzzy,
            )

        result = {}
        for filename, dom_tree in dom_trees.items():
            tree = shared_tree or build_unit_tree(
                store,
                filename,
                require_target=True,
                include_fuzzy=include_fuzzy,
            )
            result[filename] = tree.children.get(
                (root_name(dom_tree), 0),
                XPathTree(),
            )
        return result

    def translate_dom_trees(unit_trees, dom_trees):
        """
        Return a dict with the translated files for the ODF package.

        The keys are the filenames for the translatable files inside the
        template ODF package, and the values are etree ElementTree instances
        for each of those files.
        """

        def make_parse_state():
            return ParseState(no_translate_content_elements, inline_elements)

        for filename, dom_tree in dom_trees.items():
            file_unit_tree = unit_trees[filename]
            apply_translations(
                dom_tree.getroot(),
                file_unit_tree,
                replace_dom_text(make_parse_state, dom_retriever=dom_retriever),
            )
        return dom_trees

    dom_trees = load_dom_trees(template)
    unit_trees = load_unit_trees(input_file, dom_trees)
    return translate_dom_trees(unit_trees, dom_trees)


def write_odf(template, output_file, dom_trees) -> None:
    """
    Write the translated ODF package.

    The resulting ODF package is a copy of the template ODF package, with the
    translatable files replaced by their translated versions.
    """
    replacements = {
        filename: etree.tostring(
            dom_tree,
            encoding="UTF-8",
            xml_declaration=True,
        )
        for filename, dom_tree in dom_trees.items()
    }
    with ODFPackage(template) as package:
        package.write(output_file, replacements)


def convertxliff(input_file, output_file, template) -> bool:
    """Create a translated ODF using an ODF template and a XLIFF file."""
    dom_trees = translate_odf(template, input_file)
    write_odf(template, output_file, dom_trees)
    output_file.close()
    return True


def main(argv=None) -> None:
    formats = {
        ("xlf", extension): (extension, convertxliff) for extension in ODF_EXTENSIONS
    }
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.run(argv)


if __name__ == "__main__":
    main()
