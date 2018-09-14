from translate.convert import convert
from translate.storage import xliff, ts2

"""Convert TS files to XLIFF localization files.
"""


class TS2Xliff(object):
    def convertunit(self, inputunit):
        """
        :type tsunit: ts2.tsunit
        """
        unit = xliff.xliffunit(inputunit.getsource())
        unit.target = inputunit.gettarget()
        if inputunit.target:
            unit.markfuzzy(inputunit.isfuzzy())
        else:
            unit.markapproved(False)

        # Handle #: location comments
        for location in inputunit.getlocations():
            unit.createcontextgroup("ts-reference", self.contextlist(location), purpose="location")

        # Handle #. automatic comments
        comment = inputunit.getnotes("developer")
        if comment:
            unit.createcontextgroup("ts-entry", [("x-ts-autocomment", comment)], purpose="information")
            unit.addnote(comment, origin="developer")
        comment = inputunit.getnotes("translator")
        if comment:
            unit.createcontextgroup("ts-entry", [("x-ts-trancomment", comment)], purpose="information")
            unit.addnote(comment, origin="translator")
        return unit

    def contextlist(self, location):
        contexts = []
        if ":" in location:
            sourcefile, linenumber = location.split(":", 1)
        else:
            sourcefile, linenumber = location, None
        contexts.append(("sourcefile", sourcefile))
        if linenumber:
            contexts.append(("linenumber", linenumber))
        return contexts

    def convertfile(self, inputfile):
        """converts a .ts file to .xliff format"""
        src = ts2.tsfile(inputfile)
        thetargetfile = xliff.xlifffile()
        thetargetfile.setsourcelanguage(src.sourcelanguage)
        thetargetfile.settargetlanguage(src.targetlanguage)

        for srcunit in src.unit_iter():
            unit = self.convertunit(srcunit)
            thetargetfile.addunit(unit)
        return thetargetfile


def convertts(inputfile, outputfile, *args, **kwargs):
    convertor = TS2Xliff()
    target = convertor.convertfile(inputfile)
    target.serialize(outputfile)
    return 1


def main(argv=None):
    formats = {
        "ts": ("xliff", convertts),
    }
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == '__main__':
    main()
