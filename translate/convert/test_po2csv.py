from io import BytesIO

from translate.convert import csv2po, po2csv, test_convert
from translate.storage import csvl10n, po
from translate.storage.test_base import first_translatable, headerless_len


class TestPO2CSV:
    @staticmethod
    def po2csv(posource):
        """helper that converts po source to csv source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        convertor = po2csv.po2csv()
        return convertor.convertstore(inputpo)

    @staticmethod
    def csv2po(csvsource, template=None):
        """helper that converts csv source to po source without requiring files"""
        inputfile = BytesIO(csvsource)
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
        """checks that the pofile contains a single non-header element, and returns it"""
        assert headerless_len(storage.units) == 1
        return first_translatable(storage)

    def test_simpleentity(self):
        """checks that a simple csv entry definition converts properly to a po entry"""
        minipo = r'''#: term.cpp
msgid "Term"
msgstr "asdf"'''
        csvfile = self.po2csv(minipo)
        unit = self.singleelement(csvfile)
        assert unit.location == "term.cpp"
        assert unit.source == "Term"
        assert unit.target == "asdf"

    def test_multiline(self):
        """tests multiline po entries"""
        minipo = r'''msgid "First part "
"and extra"
msgstr "Eerste deel "
"en ekstra"'''
        csvfile = self.po2csv(minipo)
        unit = self.singleelement(csvfile)
        assert unit.source == "First part and extra"
        assert unit.target == "Eerste deel en ekstra"

    def test_escapednewlines(self):
        """Test the escaping of newlines"""
        minipo = r"""msgid "First line\nSecond line"
msgstr "Eerste lyn\nTweede lyn"
"""
        csvfile = self.po2csv(minipo)
        unit = self.singleelement(csvfile)
        assert unit.source == "First line\nSecond line"
        assert unit.target == "Eerste lyn\nTweede lyn"
        pofile = self.csv2po(bytes(csvfile))
        unit = self.singleelement(pofile)
        assert unit.source == "First line\nSecond line"
        assert unit.target == "Eerste lyn\nTweede lyn"

    def test_escapedtabs(self):
        """Test the escaping of tabs"""
        minipo = r"""msgid "First column\tSecond column"
msgstr "Eerste kolom\tTweede kolom"
"""
        csvfile = self.po2csv(minipo)
        unit = self.singleelement(csvfile)
        assert unit.source == "First column\tSecond column"
        assert unit.target == "Eerste kolom\tTweede kolom"
        assert (
            csvfile.findunit("First column\tSecond column").target
            == "Eerste kolom\tTweede kolom"
        )

    def test_escapedquotes(self):
        """Test the escaping of quotes (and slash)"""
        minipo = r"""msgid "Hello \"Everyone\""
msgstr "Good day \"All\""

msgid "Use \\\"."
msgstr "Gebruik \\\"."
"""
        csvfile = self.po2csv(minipo)
        assert csvfile.findunit('Hello "Everyone"').target == 'Good day "All"'
        assert csvfile.findunit('Use \\".').target == 'Gebruik \\".'

    def test_escapedescape(self):
        """Test the escaping of pure escapes is unaffected"""
        minipo = r"""msgid "Find\\Options"
msgstr "Vind\\Opsies"
"""
        csvfile = self.po2csv(minipo)
        print(minipo)
        print(csvfile)
        assert csvfile.findunit(r"Find\Options").target == r"Vind\Opsies"

    def test_singlequotes(self):
        """Tests that single quotes are preserved correctly"""
        minipo = """msgid "source 'source'"\nmsgstr "target 'target'"\n"""
        csvfile = self.po2csv(minipo)
        print(bytes(csvfile))
        assert csvfile.findunit("source 'source'").target == "target 'target'"
        # Make sure we don't mess with start quotes until writing
        minipo = """msgid "'source'"\nmsgstr "'target'"\n"""
        csvfile = self.po2csv(minipo)
        print(bytes(csvfile))
        assert csvfile.findunit(r"'source'").target == r"'target'"
        # TODO check that we escape on writing not in the internal representation

    def test_empties(self):
        """Tests that things keep working with empty entries"""
        minipo = 'msgid "Source"\nmsgstr ""\n\nmsgid ""\nmsgstr ""'
        csvfile = self.po2csv(minipo)
        assert csvfile.findunit("Source") is not None
        assert csvfile.findunit("Source").target == ""
        assert headerless_len(csvfile.units) == 1

    def test_kdecomments(self):
        """test that we don't carry KDE comments to CSV"""
        minipo = '#: simple.c\nmsgid "_: KDE comment\\n"\n"Same"\nmsgstr "Same"\n'
        csvfile = self.po2csv(minipo)
        unit = self.singleelement(csvfile)
        assert unit.source == "Same"
        assert unit.target == "Same"


class TestPO2CSVCommand(test_convert.TestConvertCommand, TestPO2CSV):
    """Tests running actual po2csv commands on files"""

    convertmodule = po2csv

    expected_options = [
        "--columnorder=COLUMNORDER",
    ]

    def test_columnorder(self):
        pocontent = '#: simple.c\nmsgid "Same"\nmsgstr "Target"\n'
        self.create_testfile("test.po", pocontent)

        self.run_command("test.po", "test.csv")
        content = self.open_testfile("test.csv", "r").read()
        assert (
            content
            == """"location","source","target"
"simple.c","Same","Target"
"""
        )

        self.run_command("test.po", "test.csv", columnorder="target,source")
        content = self.open_testfile("test.csv", "r").read()
        assert (
            content
            == """"target","source"
"Target","Same"
"""
        )
