import os

from translate.convert import odf2po

from . import test_convert


class TestODF2POCommand(test_convert.TestConvertCommand):
    """Tests running actual odf2po commands on files."""

    convertmodule = odf2po

    def test_convert(self) -> None:
        self.run_command(
            o="simple.po",
            i=os.path.join(os.path.dirname(__file__), "test.odt"),
        )
        output = self.read_testfile("simple.po")
        assert b'content.xml\nmsgid "Hello, world!"' in output
        assert b'<g id=\\"0\\">weblate.org</g>' in output
