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

"""Convert Markdown files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/md2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import markdown, po


class md2po:
    """Extract translatable content from a Markdown file to a PO file"""

    def convertfile(self, inputfile, duplicatestyle="msgctxt"):
        """Extract translation units from a markdown file and remove duplicates. Returns a message store (pofile object)."""
        store = po.pofile()
        self.convertfile_inner(inputfile, store)
        store.removeduplicates(duplicatestyle)
        return store

    def convertfile_inner(self, inputfile, outputstore):
        """Extract translation units from a markdown file and add them to an existing message store (pofile object) without any further processing."""
        parser = markdown.MarkdownFile(inputfile=inputfile)
        for tu in parser.units:
            storeunit = outputstore.addsourceunit(tu.source)
            storeunit.addlocations(tu.getlocations())


class MD2POOptionParser(convert.ConvertOptionParser):
    def __init__(self):
        formats = {
            "md": ("po", self.convert),
            "markdown": ("po", self.convert),
            "txt": ("po", self.convert),
            "text": ("po", self.convert),
            None: ("po", self.convert),
        }
        super().__init__(formats, usetemplates=False, usepots=True, description=__doc__)
        self.add_duplicates_option()
        self.add_multifile_option()
        self.passthrough.append("pot")

    def convert(
        self,
        inputfile,
        outputfile,
        templates,
        pot=False,
        duplicatestyle="msgctxt",
        multifilestyle="single",
    ):
        """Extract translation units from one markdown file."""
        convertor = md2po()
        if hasattr(self, "outputstore"):
            convertor.convertfile_inner(inputfile, self.outputstore)
        else:
            outputstore = convertor.convertfile(
                inputfile,
                duplicatestyle=duplicatestyle,
            )
            outputstore.serialize(outputfile)
        return 1

    def recursiveprocess(self, options):
        """Recurse through directories and process files. (override)"""
        if options.multifilestyle == "onefile":
            self.outputstore = po.pofile()
            super().recursiveprocess(options)
            if not self.outputstore.isempty():
                self.outputstore.removeduplicates(options.duplicatestyle)
                outputfile = super().openoutputfile(options, options.output)
                self.outputstore.serialize(outputfile)
                if options.output:
                    outputfile.close()
        else:
            super().recursiveprocess(options)

    def isrecursive(self, fileoption, filepurpose="input"):
        """Check if fileoption is a recursive file. (override)"""
        if hasattr(self, "outputstore") and filepurpose == "output":
            return True
        return super().isrecursive(fileoption, filepurpose=filepurpose)

    def checkoutputsubdir(self, options, subdir):
        """Check if subdir under options.output needs to be created, and
        create if neccessary. Do nothing if in single-output-file mode. (override)
        """
        if hasattr(self, "outputstore"):
            return
        super().checkoutputsubdir(options, subdir)

    def openoutputfile(self, options, fulloutputpath):
        """Open the output file, or do nothing if in single-output-file mode. (override)"""
        if hasattr(self, "outputstore"):
            return None
        return super().openoutputfile(options, fulloutputpath)


def main(argv=None):
    parser = MD2POOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
