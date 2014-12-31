#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert Gettext PO localisation files to .Net Resource (.resx) files."""

from translate.convert import convert
from translate.storage import factory


class po2resx:
    def __init__(self, templatefile, inputstore):
        from translate.storage import resx

        self.templatefile = templatefile
        self.templatestore = resx.RESXFile(templatefile)
        self.inputstore = inputstore

    def convertstore(self, includefuzzy=False):
        self.includefuzzy = includefuzzy
        self.inputstore.makeindex()
        for unit in self.templatestore.units:
            inputunit = self.inputstore.locationindex.get(unit.getid())
            if inputunit is not None:
                if inputunit.isfuzzy() and not self.includefuzzy:
                    unit.target = unit.source
                else:
                    unit.target = inputunit.target
            else:
                unit.target = unit.source

            if inputunit is not None:
                self.addcomments(inputunit, unit)

        return str(self.templatestore)

    def addcomments(self, inputunit, unit):
        comments = []

        # Handle #. automatic comments
        autocomment = inputunit.getnotes("developer")
        comments.append(autocomment)

        # Handle # comments
        transcomment = inputunit.getnotes("translator")
        if transcomment:
            comments.append("[Translator Comment: " + transcomment + "]")

        # Join automatic and translator comments with a newline as per convention
        combocomment = '\n'.join(comments)

        if combocomment:
            unit.addnote(combocomment)

def convertresx(inputfile, outputfile, templatefile, includefuzzy=False, outputthreshold=None):
    inputstore = factory.getobject(inputfile)

    if templatefile is None:
        raise ValueError("Must have template file for RESX files")
    else:
        convertor = po2resx(templatefile, inputstore)
    outputstring = convertor.convertstore(includefuzzy)
    outputfile.write(outputstring)
    return 1


def main(argv=None):
    # handle command line options
    formats = {
        ("po", "resx"): ("resx", convertresx),
    }
    parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
    parser.run(argv)


if __name__ == '__main__':
    main()
