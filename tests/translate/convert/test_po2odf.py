import os

from translate.convert import po2odf

from . import test_convert


class TestPO2ODFCommand(test_convert.TestConvertCommand):
    """Tests running actual po2odf commands on files."""

    convertmodule = po2odf
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
    ]

    def test_convert(self):
        """Test basic PO to ODF conversion."""
        posource = """# Translation file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Hello, world!"
msgstr "Ahoj světe!"
"""
        self.create_testfile("simple.po", posource)
        self.run_command(
            i="simple.po",
            o="simple.odt",
            template=os.path.join(os.path.dirname(__file__), "test.odt"),
        )
        # Check that the output file was created
        assert os.path.exists(self.get_testfilename("simple.odt"))

    def test_convert_with_multiple_units(self):
        """Test PO to ODF conversion with multiple translation units."""
        posource = """# Translation file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "First"
msgstr "První"

msgid "Second"
msgstr "Druhý"

msgid "Third"
msgstr "Třetí"
"""
        self.create_testfile("multi.po", posource)
        self.run_command(
            i="multi.po",
            o="multi.odt",
            template=os.path.join(os.path.dirname(__file__), "test.odt"),
        )
        # Check that the output file was created
        assert os.path.exists(self.get_testfilename("multi.odt"))
