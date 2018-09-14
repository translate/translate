from translate.convert import convert
from translate.storage import xliff, ts2

"""Convert XLIFF files to TS localization files.
"""


class Xliff2TS(object):
    def convertunit(self, inputunit):
        """
        :type inputunit: xliff.xliffunit
        """
        unit = ts2.tsunit(inputunit.getsource())
        unit.target = inputunit.gettarget()
        if inputunit.target:
            unit.markfuzzy(inputunit.isfuzzy())
        else:
            unit.markapproved(False)

        locations_ctx_names = [
            "reference",
            "ts-reference",
        ]

        for ctx_name in locations_ctx_names:
            for context in inputunit.getcontextgroups(ctx_name):
                k, v = context
                if k[0] == "sourcefile" and v[0] == "linenumber":
                    unit.addlocation("%s:%s" % (k[1], v[1]))

        # Handle #. automatic comments
        comment = inputunit.getnotes("developer")
        if comment:
            unit.addnote(comment, origin="developer")
        comment = inputunit.getnotes("translator")
        if comment:
            unit.addnote(comment, origin="translator")
        return unit

    def convertfile(self, inputfile):
        """converts a .xliff file to .ts format"""
        src = xliff.xlifffile.parsestring(inputfile)
        thetargetfile = ts2.tsfile()
        thetargetfile.header.set('sourcelanguage', src.getsourcelanguage())
        thetargetfile.settargetlanguage(src.gettargetlanguage())
        for srcunit in src.units:
            unit = self.convertunit(srcunit)

            thetargetfile.addunit(unit, contextname="Global")
        return thetargetfile


def convertxliff(inputfile, outputfile, *args, **kwargs):
    convertor = Xliff2TS()
    target = convertor.convertfile(inputfile)
    target.serialize(outputfile)
    return 1


def main(argv=None):
    formats = {
        "xliff": ("ts", convertxliff),
        "xlf": ("ts", convertxliff),
    }
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    parser.run(argv)


if __name__ == '__main__':
    main()
