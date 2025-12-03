#
# Copyright 2005-2008,2010 Zuza Software Foundation
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
Conflict finder for Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/poconflicts.html
for examples and usage instructions.
"""

import os
import sys

from translate.misc import optrecurse
from translate.storage import factory, po


class ConflictOptionParser(optrecurse.RecursiveOptionParser):
    """a specialized Option Parser for the conflict tool..."""

    def setformats(self, formats, usetemplates):
        """Sets the formats and customizes the input/output option help text."""
        super().setformats(formats, usetemplates)
        # Override the input/output option help text to be more descriptive
        inputoption = optrecurse.optparse.Option(
            "-i",
            "--input",
            dest="input",
            action="append",
            default=None,
            metavar="INPUT",
            help="read from INPUT (directory or file(s)) in po format",
        )
        inputoption.optionalswitch = True
        inputoption.required = True
        self.define_option(inputoption)
        outputoption = optrecurse.optparse.Option(
            "-o",
            "--output",
            dest="output",
            default=None,
            metavar="OUTPUT",
            help="write to OUTPUT (directory) in po format",
        )
        outputoption.optionalswitch = True
        outputoption.required = True
        self.define_option(outputoption)

    def parse_args(self, args=None, values=None):
        """Parses the command line options, handling implicit input/output args."""
        (options, args) = optrecurse.optparse.OptionParser.parse_args(
            self, args, values
        )
        # some intelligence as to what reasonable people might give on the command line
        if args and not options.input:
            if not options.output:
                options.input = args[:-1]
                args = args[-1:]
            else:
                options.input = args
                args = []
        if args and not options.output:
            options.output = args[-1]
            args = args[:-1]
        if not options.output:
            self.error("output file is required")
        if args:
            self.error(
                "You have used an invalid combination of --input, --output and freestanding args"
            )
        if isinstance(options.input, list) and len(options.input) == 1:
            options.input = options.input[0]
        return (options, args)

    def set_usage(self, usage=None):
        """Sets the usage string - if usage not given, uses getusagestring for each option."""
        if usage is None:
            self.usage = (
                "%prog "
                + " ".join(self.getusagestring(option) for option in self.option_list)
                + "\n  %prog [options] <po-directory> <output-directory>"
                + "\n  %prog [options] <po-file(s)>... <output-directory>"
                + "\n\n"
                + "Input is searched for PO files, output directory will contain PO files named after conflicting strings.\n"
                + "Both -i/--input and -o/--output are optional when using positional arguments."
            )
        else:
            super().set_usage(usage)

    def recursiveprocess(self, options):
        """Recurse through directories and process files."""
        if self.isrecursive(options.input, "input") and getattr(
            options, "allowrecursiveinput", True
        ):
            if not self.isrecursive(options.output, "output"):
                self.warning("Output directory does not exist. Attempting to create")
                try:
                    os.mkdir(options.output)
                except Exception:
                    self.error(
                        optrecurse.optparse.OptionValueError(
                            "Output directory does not exist, attempt to create failed"
                        )
                    )
            if isinstance(options.input, list):
                inputfiles = self.recurseinputfilelist(options)
            else:
                inputfiles = self.recurseinputfiles(options)
        elif options.input:
            inputfiles = [os.path.basename(options.input)]
            options.input = os.path.dirname(options.input)
        else:
            inputfiles = [options.input]
        self.textmap = {}
        progress_bar = optrecurse.ProgressBar(options.progress, inputfiles)
        for inputpath in inputfiles:
            fullinputpath = self.getfullinputpath(options, inputpath)
            try:
                success = self.processfile(None, options, fullinputpath)
            except Exception:
                self.warning(
                    f"Error processing: input {fullinputpath}",
                    options,
                    sys.exc_info(),
                )
                success = False
            progress_bar.report_progress(inputpath, success)
        self.buildconflictmap()
        self.outputconflicts(options)

    @staticmethod
    def clean(string, options):
        """Returns the cleaned string that contains the text to be matched."""
        if options.ignorecase:
            string = string.lower()
        for accelerator in options.accelchars:
            string = string.replace(accelerator, "")
        return string.strip()

    def processfile(self, fileprocessor, options, fullinputpath):
        """Process an individual file."""
        inputfile = self.openinputfile(options, fullinputpath)
        inputfile = factory.getobject(inputfile)
        for unit in inputfile.units:
            if unit.isheader() or not unit.istranslated():
                continue
            if unit.hasplural():
                continue
            if not options.invert:
                source = self.clean(unit.source, options)
                target = self.clean(unit.target, options)
            else:
                target = self.clean(unit.source, options)
                source = self.clean(unit.target, options)
            self.textmap.setdefault(source, []).append((target, unit, fullinputpath))
        return True

    @staticmethod
    def flatten(text, joinchar):
        """Flattens text to just be words."""
        flattext = ""
        for c in text:
            if c.isalnum():
                flattext += c
            elif flattext[-1:].isalnum():
                flattext += joinchar
        return flattext.rstrip(joinchar)

    def buildconflictmap(self):
        """Work out which strings are conflicting."""
        self.conflictmap = {}
        for source, translations in self.textmap.items():
            source = self.flatten(source, " ")
            if len(source) <= 1:
                continue
            if len(translations) > 1:
                uniquetranslations = dict.fromkeys(
                    [target for target, unit, filename in translations]
                )
                if len(uniquetranslations) > 1:
                    self.conflictmap[source] = translations

    def outputconflicts(self, options):
        """Saves the result of the conflict match."""
        print(
            f"{len(self.conflictmap)}/{len(self.textmap)} different strings have conflicts"
        )
        reducedmap = {}

        def str_len(x):
            return len(x)

        for source, translations in self.conflictmap.items():
            words = source.split()
            words.sort(key=str_len)
            reducedmap.setdefault(words[-1], []).extend(translations)
        # reduce plurals
        plurals = {}
        for word in reducedmap:
            if word + "s" in reducedmap:
                plurals[word] = word + "s"
        for word, pluralword in plurals.items():
            reducedmap[word].extend(reducedmap.pop(pluralword))
        for source, translations in reducedmap.items():
            flatsource = self.flatten(source, "-")
            fulloutputpath = os.path.join(options.output, flatsource + os.extsep + "po")
            conflictfile = po.pofile()
            for _target, unit, filename in translations:
                unit.othercomments.append(f"# (poconflicts) {filename}\n")
                conflictfile.units.append(unit)
            with open(fulloutputpath, "wb") as fh:
                conflictfile.serialize(fh)


def main():
    formats = {"po": ("po", None), None: ("po", None)}
    parser = ConflictOptionParser(formats)
    parser.add_option(
        "-I",
        "--ignore-case",
        dest="ignorecase",
        action="store_true",
        default=False,
        help="ignore case distinctions",
    )
    parser.add_option(
        "-v",
        "--invert",
        dest="invert",
        action="store_true",
        default=False,
        help="invert the conflicts thus extracting conflicting destination words",
    )
    parser.add_option(
        "",
        "--accelerator",
        dest="accelchars",
        default="",
        metavar="ACCELERATORS",
        help="ignores the given accelerator characters when matching",
    )
    parser.set_usage()
    parser.description = __doc__
    parser.run()


if __name__ == "__main__":
    main()
