import os
from tempfile import TemporaryFile

from translate.misc import optrecurse


class TestRecursiveOptionParser:

    def test_splitext(self):
        """test the ``optrecurse.splitext`` function"""
        self.parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        name = "name"
        extension = "ext"
        filename = name + os.extsep + extension
        dirname = os.path.join("some", "path", "to")
        fullpath = os.path.join(dirname, filename)
        root = os.path.join(dirname, name)
        print(fullpath)
        assert self.parser.splitext(fullpath) == (root, extension)

    def test_outputfile_receives_bytes(self, capsys):
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})

        temp_file = TemporaryFile()
        with TemporaryFile() as tempfile:
            out = parser.openoutputfile(None, temp_file.name)
            out.write(b'binary suff')

        out = parser.openoutputfile(None, None)  # To sys.stdout
        out.write(b'binary suff')
