import logging
from io import BytesIO

from translate.convert import csv2po
from translate.storage import csvl10n, po

from ..storage.test_base import first_translatable, headerless_len
from . import test_convert


def test_replacestrings() -> None:
    """Test the _replacestring function."""
    assert (
        csv2po.replacestrings("Test one two three", ("one", "een"), ("two", "twee"))
        == "Test een twee three"
    )


class TestCSV2PO:
    @staticmethod
    def csv2po(csvsource, template=None):
        """Helper that converts csv source to po source without requiring files."""
        inputfile = BytesIO(csvsource.encode())
        inputcsv = csvl10n.csvfile(inputfile)
        if template:
            templatefile = BytesIO(template.encode())
            inputpot = po.pofile(templatefile)
        else:
            inputpot = None
        convertor = csv2po.csv2po(templatepo=inputpot)
        return convertor.convertstore(inputcsv)

    @staticmethod
    def singleelement(storage):
        """Checks that the pofile contains a single non-header element, and returns it."""
        print(bytes(storage))
        assert headerless_len(storage.units) == 1
        return first_translatable(storage)

    def test_simpleentity(self) -> None:
        """Checks that a simple csv entry definition converts properly to a po entry."""
        csvheader = "location,source,target\n"
        csvsource = "intl.charset.default,ISO-8859-1,UTF-16"
        # Headerless
        pofile = self.csv2po(csvsource)
        pounit = self.singleelement(pofile)
        # With header
        pofile = self.csv2po(csvheader + csvsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["intl.charset.default"]
        assert pounit.source == "ISO-8859-1"
        assert pounit.target == "UTF-16"

    def test_simpleentity_with_template(self) -> None:
        """Checks that a simple csv entry definition converts properly to a po entry."""
        csvsource = """location,original,translation
intl.charset.default,ISO-8859-1,UTF-16"""
        potsource = """#: intl.charset.default
msgid "ISO-8859-1"
msgstr ""
"""
        pofile = self.csv2po(csvsource, potsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["intl.charset.default"]
        assert pounit.source == "ISO-8859-1"
        assert pounit.target == "UTF-16"

    def test_newlines(self) -> None:
        """Tests multiline po entries."""
        minicsv = r""""Random comment
with continuation","Original text","Langdradige teks
wat lank aanhou"
"""
        pofile = self.csv2po(minicsv)
        unit = self.singleelement(pofile)
        assert unit.getlocations() == ["Random comment\nwith continuation"]
        assert unit.source == "Original text"
        print(unit.target)
        assert unit.target == "Langdradige teks\nwat lank aanhou"

    def test_tabs(self) -> None:
        """Test the escaping of tabs."""
        minicsv = ',"First column\tSecond column","Twee kolomme gesky met \t"'
        pofile = self.csv2po(minicsv)
        unit = self.singleelement(pofile)
        print(unit.source)
        assert unit.source == "First column\tSecond column"
        assert (
            pofile.findunit("First column\tSecond column").target
            != "Twee kolomme gesky met \\t"
        )

    def test_quotes(self) -> None:
        """Test the escaping of quotes (and slash)."""
        minicsv = r''',"Hello ""Everyone""","Good day ""All"""
,"Use \"".","Gebruik \""."'''
        print(minicsv)
        csvfile = csvl10n.csvfile(BytesIO(minicsv.encode()))
        print(bytes(csvfile))
        pofile = self.csv2po(minicsv)
        unit = first_translatable(pofile)
        assert unit.source == 'Hello "Everyone"'
        assert pofile.findunit('Hello "Everyone"').target == 'Good day "All"'
        print(bytes(pofile))
        for unit in pofile.units:
            print(unit.source)
            print(unit.target)
            print()

    #        assert pofile.findunit('Use \\".').target == 'Gebruik \\".'

    def test_empties(self) -> None:
        """Tests that things keep working with empty entries."""
        minicsv = ",SomeSource,"
        pofile = self.csv2po(minicsv)
        assert pofile.findunit("SomeSource") is not None
        assert pofile.findunit("SomeSource").target == ""
        assert headerless_len(pofile.units) == 1

    def test_kdecomment(self) -> None:
        """Checks that we can merge into KDE comment entries."""
        csvsource = """location,source,target
simple.c,Source,Target"""
        potsource = r"""#: simple.c
msgid "_: KDE comment\n"
"Source"
msgstr ""
"""
        pofile = self.csv2po(csvsource, potsource)
        pounit = self.singleelement(pofile)
        assert pounit._extract_msgidcomments() == "KDE comment"
        assert pounit.source == "Source"
        assert pounit.target == "Target"

    def test_escaped_newlines(self) -> None:
        """Tests that things keep working with escaped newlines."""
        minicsv = '"source","target"\r\n"yellow pencil","żółty\\nołówek"'
        pofile = self.csv2po(minicsv)
        assert pofile.findunit("yellow pencil") is not None
        assert pofile.findunit("yellow pencil").target == "żółty\\nołówek"
        assert headerless_len(pofile.units) == 1

    def test_line_numbers_in_errors(self, caplog) -> None:
        """Tests that line numbers are included in error messages."""
        # CSV with entries that won't be found in the template
        csvsource = """location,source,target
not.found.location,NotFound1,Translation1
another.missing,NotFound2,Translation2
yet.another,NotFound3,Translation3"""

        # Template with different entries
        potsource = """#: different.location
msgid "Different"
msgstr ""
"""
        with caplog.at_level(logging.WARNING):
            self.csv2po(csvsource, potsource)

        # Check that line numbers appear in the warnings
        assert "line 2" in caplog.text
        assert "line 3" in caplog.text
        assert "line 4" in caplog.text
        assert "entry not found in pofile" in caplog.text


class TestCSV2POCommand(test_convert.TestConvertCommand, TestCSV2PO):
    """Tests running actual csv2po commands on files."""

    convertmodule = csv2po

    expected_options = [
        "-t TEMPLATE, --template=TEMPLATE",
        "-P, --pot",
        "--charset=CHARSET",
        "--columnorder=COLUMNORDER",
        "--duplicates=DUPLICATESTYLE",
    ]

    def test_columnorder(self) -> None:
        csvcontent = '"Target","Same"\n'
        self.create_testfile("test.csv", csvcontent)

        self.run_command("test.csv", "test.po")
        # Strip PO file header
        content = self.open_testfile("test.po", "r").read().split("\n\n")[1]
        assert (
            content
            == """#: Target
msgid "Same"
msgstr ""
"""
        )

        self.run_command("test.csv", "test.po", columnorder="target,source")
        content = self.open_testfile("test.po", "r").read().split("\n\n")[1]
        assert (
            content
            == """msgid "Same"
msgstr "Target"
"""
        )
