import os
from zipfile import ZipFile

from translate.convert import odf2po, po2odf
from translate.storage import po

from . import test_convert


class TestPO2ODFCommand(test_convert.TestConvertCommand):
    """Tests running actual po2odf commands on files."""

    convertmodule = po2odf
    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
    ]

    def test_convert(self) -> None:
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

    def test_convert_with_multiple_units(self) -> None:
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

    def test_odf2po_roundtrip_with_inline_placeable(self) -> None:
        template = os.path.join(os.path.dirname(__file__), "test.odt")
        po_path = self.get_testfilename("roundtrip.po")
        odf2po.main([template, po_path, "--progress=none"])
        with open(po_path, "rb") as po_file:
            store = po.pofile(po_file)
        unit = next(
            unit for unit in store.units if unit.source.startswith("Try Weblate")
        )
        unit.sourcecomments.reverse()
        assert unit.getlocations()[0] == "content.xml"
        unit.target = 'Vyzkoušejte <g id="0">weblate.org</g>!'
        store.save()

        self.run_command(
            i="roundtrip.po",
            o="roundtrip.odt",
            template=template,
        )

        with ZipFile(self.get_testfilename("roundtrip.odt")) as archive:
            assert "Vyzkoušejte" in archive.read("content.xml").decode()
