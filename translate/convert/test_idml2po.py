import os

from translate.convert import idml2po, test_convert


class TestIDML2POCommand(test_convert.TestConvertCommand):
    """Tests running actual idml2po commands on files"""

    convertmodule = idml2po

    def test_convert(self):
        self.run_command(
            o="simple.po",
            i=os.path.join(os.path.dirname(__file__), "test.idml"),
        )
        assert "THE HEADLINE HERE" in self.read_testfile("simple.po").decode()
