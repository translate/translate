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

"""Translate MDX files using Gettext PO localization files."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from translate.convert import convert
from translate.misc.optrecurse import ProgressBar
from translate.storage import mdxfile, po

if TYPE_CHECKING:
    from translate.storage.base import TranslationStore

DEFAULT_MAX_LINE_LENGTH = 80


class MDXTranslator:
    def __init__(
        self,
        inputstore: TranslationStore,
        includefuzzy: bool,
        outputthreshold: int | None,
        maxlength: int,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
        no_placeholders: bool = False,
    ) -> None:
        self.inputstore = inputstore
        self.inputstore.require_index()
        self.includefuzzy = includefuzzy
        self.outputthreshold = outputthreshold
        self.maxlength = maxlength
        self.extract_code_blocks = extract_code_blocks
        self.extract_frontmatter = extract_frontmatter
        self.no_placeholders = no_placeholders

    def translate(self, templatefile, outputfile) -> int:
        if not convert.should_output_store(self.inputstore, self.outputthreshold):
            return False
        outputstore = mdxfile.MDXFile(
            inputfile=templatefile,
            callback=self._lookup,
            max_line_length=self.maxlength if self.maxlength > 0 else None,
            extract_code_blocks=self.extract_code_blocks,
            extract_frontmatter=self.extract_frontmatter,
            no_placeholders=self.no_placeholders,
        )
        outputfile.write(outputstore.filesrc.encode("utf-8"))
        return 1

    def _lookup(self, string: str) -> str:
        unit = self.inputstore.sourceindex.get(string, None)
        if unit is None:
            return string
        unit = unit[0]
        if unit.istranslated():
            return unit.target
        if self.includefuzzy and unit.isfuzzy():
            return unit.target
        return unit.source


class PO2MDXOptionParser(convert.ConvertOptionParser):
    def __init__(self) -> None:
        formats = {
            ("po", "mdx"): ("mdx", self._translate_mdx_file),
        }
        super().__init__(formats, usetemplates=True, description=__doc__)
        self.add_option(
            "-m",
            "--maxlinelength",
            type="int",
            dest="maxlength",
            default=DEFAULT_MAX_LINE_LENGTH,
            help="reflow (word wrap) the output to the given maximum line length. set to 0 to disable",
        )
        self.passthrough.append("maxlength")
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
                "look up translation units by their full inline markdown "
                "(links, images, autolinks, HTML spans rendered verbatim) "
                "instead of {n} placeholder markers; use together with "
                "mdx2po --no-placeholders"
            ),
        )
        self.passthrough.append("no_placeholders")
        self.add_threshold_option()
        self.add_fuzzy_option()

    @staticmethod
    def _translate_mdx_file(
        inputfile,
        outputfile,
        templatefile,
        includefuzzy: bool,
        outputthreshold: int | None,
        maxlength: int,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
        no_placeholders: bool = False,
    ):
        inputstore = po.pofile(inputfile)
        translator = MDXTranslator(
            inputstore,
            includefuzzy,
            outputthreshold,
            maxlength,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
            no_placeholders=no_placeholders,
        )
        return translator.translate(templatefile, outputfile)

    def recursiveprocess(self, options) -> None:
        if (
            self.isrecursive(options.template, "template")
            and not self.isrecursive(options.input, "input")
            and self.can_be_recursive(options.output, "output")
        ):
            self.recursiveprocess_by_templates(options)
        else:
            super().recursiveprocess(options)

    def can_be_recursive(self, fileoption, filepurpose):
        return fileoption is not None and not os.path.isfile(fileoption)

    def recursiveprocess_by_templates(self, options) -> None:
        """Recurse through directories and process files, by templates."""
        inputfile = self.openinputfile(options, options.input)
        self.inputstore = po.pofile(inputfile)
        templatefiles = self.recurse_template_files(options)
        self.ensurerecursiveoutputdirexists(options)
        progress_bar = ProgressBar(options.progress, templatefiles)
        for templatepath in templatefiles:
            fulltemplatepath = os.path.join(options.template, templatepath)
            outputpath = templatepath
            fulloutputpath = os.path.join(options.output, outputpath)
            self.checkoutputsubdir(options, os.path.dirname(outputpath))
            try:
                success = self.processfile(
                    self.process_file_with_fixed_inputstore,
                    options,
                    None,
                    fulloutputpath,
                    fulltemplatepath,
                )
            except Exception:
                self.warning(
                    f"Error processing: input {options.input}, output {fulloutputpath}, template {fulltemplatepath}",
                    options,
                    sys.exc_info(),
                )
                success = False
            progress_bar.report_progress(templatepath, success)
        del progress_bar

    def process_file_with_fixed_inputstore(
        self,
        inputfile,
        outputfile,
        templatefile,
        includefuzzy: bool,
        outputthreshold: int | None,
        maxlength: int,
        extract_code_blocks: bool = True,
        extract_frontmatter: bool = True,
        no_placeholders: bool = False,
    ):
        translator = MDXTranslator(
            self.inputstore,
            includefuzzy,
            outputthreshold,
            maxlength,
            extract_code_blocks=extract_code_blocks,
            extract_frontmatter=extract_frontmatter,
            no_placeholders=no_placeholders,
        )
        return translator.translate(templatefile, outputfile)

    def recurse_template_files(self, options):
        """Recurse through directories and return files to be processed."""
        dirstack = [""]
        join = os.path.join
        templatefiles = []
        while dirstack:
            top = dirstack.pop(-1)
            names = os.listdir(join(options.template, top))
            dirs = []
            for name in names:
                filepath = join(top, name)
                fullfilepath = join(options.template, filepath)
                if os.path.isdir(fullfilepath):
                    dirs.append(filepath)
                elif os.path.isfile(fullfilepath):
                    if not self.isvalidtemplatename(name):
                        continue
                    templatefiles.append(filepath)
            dirs.reverse()
            dirstack.extend(dirs)
        return templatefiles

    def isvalidtemplatename(self, filename):
        """Checks if this is a valid template/output filename."""
        _, ext = self.splitext(filename)
        return any(ext == templateformat for _, templateformat in self.outputoptions)


def main(argv=None) -> None:
    parser = PO2MDXOptionParser()
    parser.run(argv)


if __name__ == "__main__":
    main()
