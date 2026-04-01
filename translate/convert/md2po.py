#
# Copyright 2023 Zuza Software Foundation & Anders Kaplan
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
Convert Markdown files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/md2po.html
for examples and usage instructions.
"""

from __future__ import annotations

import functools

from translate.convert import convert
from translate.storage import markdown, po


class MD2POOptionParser(convert.ConvertOptionParser, convert.DocpathMerger):
    def __init__(self) -> None:
        formats = {
            "md": ("po", self._extract_translation_units),
            "markdown": ("po", self._extract_translation_units),
            "txt": ("po", self._extract_translation_units),
            "text": ("po", self._extract_translation_units),
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

    def _extract_translation_units(
        self,
        inputfile,
        outputfile,
        templatefile,
        duplicatestyle: str,
        multifilestyle: str,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
    ) -> int:
        if hasattr(self, "outputstore"):
            if templatefile is None:
                self._parse_and_extract(
                    inputfile,
                    self.outputstore,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                )
            else:
                self._merge_with_template(
                    inputfile,
                    templatefile,
                    self.outputstore,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                )
        else:
            store = po.pofile()
            if templatefile is None:
                self._parse_and_extract(
                    inputfile,
                    store,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
                )
            else:
                self._merge_with_template(
                    inputfile,
                    templatefile,
                    store,
                    extract_code_blocks=extract_code_blocks,
                    extract_frontmatter=extract_frontmatter,
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
    ) -> None:
        """Extract translation units from a markdown file and add them to an existing message store (pofile object) without any further processing."""
        parser = markdown.MarkdownFile(
            inputfile=inputfile,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
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
    ) -> None:
        """Merge translation from inputfile with source from templatefile using docpath matching."""
        store_class = functools.partial(
            markdown.MarkdownFile,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
        )
        self.merge_stores_by_docpath(
            inputfile,
            templatefile,
            outputstore,
            store_class,
            filter_header=True,
        )

    _txt_extensions = {"txt", "text"}

    def isvalidinputname(self, inputname):
        """Checks if this is a valid input filename (override)."""
        _inputbase, inputext = self.splitinputext(inputname)
        if inputext in self._txt_extensions:
            return False
        return super().isvalidinputname(inputname)

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
        """
        Check if subdir under options.output needs to be created, and
        create if necessary. Do nothing if in single-output-file mode. (override).
        """
        if hasattr(self, "outputstore"):
            return
        super().checkoutputsubdir(options, subdir)

    def openoutputfile(self, options, fulloutputpath):
        """Open the output file, or do nothing if in single-output-file mode. (override)."""
        if hasattr(self, "outputstore"):
            return None
        return super().openoutputfile(options, fulloutputpath)


def main(argv=None) -> None:
    parser = MD2POOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
