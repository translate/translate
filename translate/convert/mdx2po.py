#
# Copyright 2024 Zuza Software Foundation
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

"""
Convert MDX files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/mdx2po.html
for examples and usage instructions.
"""

from __future__ import annotations

import functools

from translate.convert import convert
from translate.storage import mdxfile, po


class MDX2POOptionParser(convert.ConvertOptionParser, convert.DocpathMerger):
    def __init__(self) -> None:
        formats = {
            "mdx": ("po", self._extract_translation_units),
            None: ("po", self._extract_translation_units),
        }
        super().__init__(formats, usetemplates=True, usepots=True, description=__doc__)
        self.add_duplicates_option()
        self.add_multifile_option()
        self.add_option(
            "",
            "--no-code-blocks",
            action="store_false",
            dest="extract_code_blocks",
            default=True,
            help="do not extract code blocks for translation",
        )
        self.passthrough.append("extract_code_blocks")
        self.add_option(
            "",
            "--no-frontmatter",
            action="store_false",
            dest="extract_frontmatter",
            default=True,
            help="do not extract front matter for translation",
        )
        self.passthrough.append("extract_frontmatter")
        self.add_option(
            "",
            "--no-placeholders",
            action="store_true",
            dest="no_placeholders",
            default=False,
            help=(
                "render inline elements (links, images, autolinks, HTML spans) "
                "verbatim in translation units instead of replacing them with "
                "{n} placeholder markers"
            ),
        )
        self.passthrough.append("no_placeholders")

    def _extract_translation_units(
        self,
        inputfile,
        outputfile,
        templatefile,
        duplicatestyle: str,
        multifilestyle: str,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
        no_placeholders: bool = False,
    ) -> int:
        if hasattr(self, "outputstore"):
            if templatefile is None:
                self._parse_and_extract(
                    inputfile,
                    self.outputstore,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                    no_placeholders=no_placeholders,
                )
            else:
                self._merge_with_template(
                    inputfile,
                    templatefile,
                    self.outputstore,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                    no_placeholders=no_placeholders,
                )
        else:
            store = po.pofile()
            if templatefile is None:
                self._parse_and_extract(
                    inputfile,
                    store,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                    no_placeholders=no_placeholders,
                )
            else:
                self._merge_with_template(
                    inputfile,
                    templatefile,
                    store,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                    no_placeholders=no_placeholders,
                )
            store.removeduplicates(duplicatestyle)
            store.serialize(outputfile)
        return 1

    @staticmethod
    def _parse_and_extract(
        inputfile,
        outputstore: po.pofile,
        *,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
        no_placeholders: bool = False,
    ) -> None:
        """Extract translation units from an MDX file."""
        parser = mdxfile.MDXFile(
            inputfile=inputfile,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
            no_placeholders=no_placeholders,
        )
        for tu in parser.units:
            storeunit = outputstore.addsourceunit(tu.source)
            storeunit.addlocations(tu.getlocations())

    def _merge_with_template(
        self,
        inputfile,
        templatefile,
        outputstore: po.pofile,
        *,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
        no_placeholders: bool = False,
    ) -> None:
        """Merge translation from inputfile with source from templatefile."""
        store_class = functools.partial(
            mdxfile.MDXFile,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
            no_placeholders=no_placeholders,
        )
        self.merge_stores_by_docpath(
            inputfile,
            templatefile,
            outputstore,
            store_class,
            filter_header=True,
        )

    def recursiveprocess(self, options) -> None:
        """Recurse through directories and process files. (override)."""
        if options.multifilestyle == "onefile":
            self.outputstore = po.pofile()
            super().recursiveprocess(options)
            if not self.outputstore.isempty():
                outputfile = super().openoutputfile(options, options.output)
                self.outputstore.removeduplicates(options.duplicatestyle)
                self.outputstore.serialize(outputfile)
                if options.output:
                    outputfile.close()
        else:
            super().recursiveprocess(options)

    def isrecursive(self, fileoption, filepurpose="input"):
        """Check if fileoption is a recursive file. (override)."""
        if hasattr(self, "outputstore") and filepurpose == "output":
            return True
        return super().isrecursive(fileoption, filepurpose=filepurpose)

    def checkoutputsubdir(self, options, subdir) -> None:
        """Check if subdir needs to be created. (override)."""
        if hasattr(self, "outputstore"):
            return
        super().checkoutputsubdir(options, subdir)

    def openoutputfile(self, options, fulloutputpath):
        """Open the output file. (override)."""
        if hasattr(self, "outputstore"):
            return None
        return super().openoutputfile(options, fulloutputpath)


def main(argv=None) -> None:
    parser = MDX2POOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
