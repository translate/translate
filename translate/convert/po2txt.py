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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Convert Gettext PO localization files to plain text (.txt) files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/txt2po.html
for examples and usage instructions.
"""

import textwrap

from translate.convert import convert
from translate.storage import factory, txt


class po2txt:
    """
    po2txt can take a po file and generate txt.

    best to give it a template file otherwise will just concat msgstrs
    """

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        include_fuzzy=False,
        output_threshold=None,
        encoding="utf-8",
        wrap=None,
        flavour=None,
        no_segmentation=False,
    ) -> None:
        """Initialize the converter."""
        self.source_store = factory.getobject(input_file)

        self.should_output_store = convert.should_output_store(
            self.source_store, output_threshold
        )
        if self.should_output_store:
            self.include_fuzzy = include_fuzzy
            self.encoding = encoding
            self.wrap = wrap
            self.flavour = flavour
            self.no_segmentation = no_segmentation

            self.output_file = output_file
            self.template_file = template_file

    def wrapmessage(self, message):
        """Rewraps text as required."""
        if self.wrap is None:
            return message
        return "\n".join(
            textwrap.fill(line, self.wrap, replace_whitespace=False)
            for line in message.split("\n")
        )

    def convert_store(self):
        """Convert a source file to a target file."""
        txtresult = ""
        for unit in self.source_store.units:
            if not unit.istranslatable():
                continue
            if unit.istranslated() or (self.include_fuzzy and unit.isfuzzy()):
                txtresult += f"{self.wrapmessage(unit.target)}\n\n"
            else:
                txtresult += f"{self.wrapmessage(unit.source)}\n\n"
        return txtresult.rstrip()

    def merge_stores(self):
        """
        Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        # Parse the template file using TxtFile to segment it the same way txt2po does
        self.template_file.seek(0)  # ty:ignore[possibly-missing-attribute]
        template_store = txt.TxtFile(
            self.template_file,
            encoding=self.encoding,
            flavour=self.flavour,
            no_segmentation=self.no_segmentation,
        )

        # Create a lookup dictionary for translations
        translation_dict = {}
        for unit in self.source_store.units:
            if (
                unit.istranslatable()
                and unit.istranslated()
                and (not unit.isfuzzy() or self.include_fuzzy)
            ):
                translation_dict[unit.source] = self.wrapmessage(unit.target)

        # Build the result by going through each template unit
        result_parts = []
        for i, template_unit in enumerate(template_store.units):
            # Add double newline separator between units (except before first unit)
            if i > 0:
                result_parts.append("\n\n")

            # Look up the translation, or use the original text
            translated_text = translation_dict.get(
                template_unit.source, template_unit.source
            )

            # Reconstruct with pretext and posttext
            result_parts.append(
                f"{template_unit.pretext}{translated_text}{template_unit.posttext}"
            )

        return "".join(result_parts)

    def run(self) -> bool:
        """Run the converter."""
        if not self.should_output_store:
            return False

        if self.template_file is None:
            outputstring = self.convert_store()
        else:
            outputstring = self.merge_stores()

        self.output_file.write(outputstring.encode("utf-8"))
        return True


def run_converter(
    inputfile,
    outputfile,
    templatefile=None,
    wrap=None,
    includefuzzy=False,
    encoding="utf-8",
    outputthreshold=None,
    flavour=None,
    no_segmentation=False,
):
    """Wrapper around converter."""
    return po2txt(
        inputfile,
        outputfile,
        templatefile,
        include_fuzzy=includefuzzy,
        output_threshold=outputthreshold,
        encoding=encoding,
        wrap=wrap,
        flavour=flavour,
        no_segmentation=no_segmentation,
    ).run()


formats = {
    ("po", "txt"): ("txt", run_converter),
    ("po"): ("txt", run_converter),
    ("xlf", "txt"): ("txt", run_converter),
    ("xlf"): ("txt", run_converter),
    ("xliff", "txt"): ("txt", run_converter),
    ("xliff"): ("txt", run_converter),
}


def main(argv=None) -> None:
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_option(
        "",
        "--encoding",
        dest="encoding",
        default="utf-8",
        type="string",
        help="The encoding of the template file (default: UTF-8)",
    )
    parser.passthrough.append("encoding")
    parser.add_option(
        "-w",
        "--wrap",
        dest="wrap",
        default=None,
        type="int",
        help="set number of columns to wrap text at",
        metavar="WRAP",
    )
    parser.passthrough.append("wrap")
    parser.add_option(
        "",
        "--flavour",
        dest="flavour",
        default="plain",
        type="choice",
        choices=["plain", "dokuwiki", "mediawiki"],
        help=("The flavour of text file: plain (default), dokuwiki, mediawiki"),
        metavar="FLAVOUR",
    )
    parser.passthrough.append("flavour")
    parser.add_option(
        "",
        "--no-segmentation",
        dest="no_segmentation",
        default=False,
        action="store_true",
        help="Don't segment the file, treat it like a single message",
    )
    parser.passthrough.append("no_segmentation")
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
