#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005, 2006 Zuza Software Foundation
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

"""Restructure Gettxt PO files produced by
:doc:`poconflicts </commands/poconflicts>` into the original directory tree
for merging using :doc:`pomerge </commands/pomerge>`.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pomerge.html
for examples and usage instructions.
"""

import os
import sys

from translate.misc import optrecurse
from translate.storage import po


class SplitOptionParser(optrecurse.RecursiveOptionParser):
    """a specialized Option Parser for posplit"""

    def parse_args(self, args=None, values=None):
        """parses the command line options, handling implicit input/output args"""
        args = optrecurse.RecursiveOptionParser.parse_args(self, args, values)
        if not args.output:
            self.error("Output file is rquired")
        return args

    def recursiveprocess(self, options):
        """recurse through directories and process files"""
        if not self.isrecursive(options.output, 'output'):
            try:
                self.warning("Output directory does not exist. Attempting to create")
                # TODO: maybe we should only allow it to be created, otherwise
                # we mess up an existing tree.
                os.mkdir(options.output)
            except:
                    self.error(optrecurse.argparse.ArgumentError("Output directory does not exist, attempt to create failed"))
        if self.isrecursive(options.input, 'input') and getattr(options, "allowrecursiveinput", True):
            if isinstance(options.input, list):
                inputfiles = self.recurseinputfilelist(options)
            else:
                inputfiles = self.recurseinputfiles(options)
        else:
            if options.input:
                inputfiles = [os.path.basename(options.input)]
                options.input = os.path.dirname(options.input)
            else:
                inputfiles = [options.input]
        self.textmap = {}
        self.initprogressbar(inputfiles, options)
        for inputpath in inputfiles:
            fullinputpath = self.getfullinputpath(options, inputpath)
            try:
                success = self.processfile(options, fullinputpath)
            except Exception as error:
                if isinstance(error, KeyboardInterrupt):
                    raise self.warning("Error processing: input %s" % (fullinputpath), options, sys.exc_info())
                success = False
            self.reportprogress(inputpath, success)
        del self.progressbar

    def processfile(self, options, fullinputpath):
        """process an individual file"""
        inputfile = self.openinputfile(options, fullinputpath)
        inputpofile = po.pofile(inputfile)
        for pounit in inputpofile.units:
            if not (pounit.isheader() or pounit.hasplural()):  # XXX
                if pounit.hasmarkedcomment("poconflicts"):
                    for comment in pounit.othercomments:
                        if comment.find("# (poconflicts)") == 0:
                            pounit.othercomments.remove(comment)
                            break
                    # TODO: refactor writing out
                    outputpath = comment[comment.find(")") + 2:].strip()
                    self.checkoutputsubdir(options, os.path.dirname(outputpath))
                    fulloutputpath = os.path.join(options.output, outputpath)
                    if os.path.isfile(fulloutputpath):
                        outputfile = open(fulloutputpath, 'r')
                        outputpofile = po.pofile(outputfile)
                    else:
                        outputpofile = po.pofile()
                    outputpofile.units.append(pounit)   # TODO:perhaps check to see if it's already there...
                    outputfile = open(fulloutputpath, 'w')
                    outputfile.write(str(outputpofile))


def main():
    # outputfile extentions will actually be determined by the comments in the
    # po files
    pooutput = ("po", None)
    formats = {(None, None): pooutput, ("po", "po"): pooutput, "po": pooutput}
    parser = SplitOptionParser(formats, description=__doc__)
    parser.run()


if __name__ == '__main__':
    main()
