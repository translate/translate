from translate.storage import base
from translate.misc import textwrap

class TxtUnit(base.TranslationUnit):
    """This class represents a block of text from a text file"""
    def __init__(self, source=""):
        """Construct the txtunit"""
        self.source = source
        self.location = []

    def __str__(self):
        """Convert a txt unit to a string"""
        string = "".join(self.source)
        if isinstance(string, unicode):
            return string.encode(getattr(self, "encoding", "UTF-8"))
        return string

    # Note that source and target are equivalent for monolingual units
    def setsource(self, source):
        """Sets the definition to the quoted value of source"""
        self._source = source

    def getsource(self):
        """gets the unquoted source string"""
        return self._source
    source = property(getsource, setsource)

    def settarget(self, target):
        """Sets the definition to the quoted value of target"""
        self._source = target

    def gettarget(self):
        """gets the unquoted target string"""
        return self._source
    target = property(gettarget, settarget)

    def addlocation(self, location):
        self.location.append(location)

class TxtFile(base.TranslationStore):
    """This class represents a text file, made up of txtunits"""
    UnitClass = TxtUnit
    def __init__(self, inputfile=None):
        self.units = []
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
          txtsrc = inputfile.readlines()
          self.parse(txtsrc)

    def parse(self, lines):
        """Read in text lines and create txtunits from the blocks of text"""
        self.units = []
        block = []
        startline = 0
        for linenum in range(len(lines)):
            line = lines[linenum].rstrip("\n")
            isbreak = not line.strip()
            if isbreak and block:
                unit = self.addsourceunit("\n".join(block))
                unit.addlocation("%s:%d" % (self.filename, startline + 1))
                block = []
            elif not isbreak:
                if not block:
                    startline = linenum
                block.append(line)
        if block:
            unit = self.addsourceunit("\n".join(block))
            unit.addlocation("%s:%d" % (self.filename, startline + 1))

    def parsestring(self, lines):
        newtxtfile = TxtFile()
        newtxtfile.parse(lines.split("\n"))
        return newtxtfile
    parsestring = classmethod(parsestring)

    def __str__(self):
        source = self.getoutput()
        if isinstance(source, unicode):
            return source.encode(getattr(self, "encoding", "UTF-8"))
        return source

    def getoutput(self):
        """Convert the units back to blocks"""
        blocks = [str(unit) for unit in self.units]
        string = "\n\n".join(blocks)
        return string
