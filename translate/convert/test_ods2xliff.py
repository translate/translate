import os

from translate.convert import odf2xliff, test_convert


class TestODF2XLIFFCommand(test_convert.TestConvertCommand):
    """Tests running actual odf2xliff commands on files"""

    convertmodule = odf2xliff

    def test_convert(self):
        self.run_command(
            o="simple.xlf",
            i=os.path.join(os.path.dirname(__file__), "test.odt"),
        )
        assert b"Hello, world!" in self.read_testfile("simple.xlf")
