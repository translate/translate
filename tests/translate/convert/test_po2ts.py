from io import BytesIO

from translate.convert import po2ts, test_convert
from translate.storage import po


class TestPO2TS:
    @staticmethod
    def po2ts(posource):
        """helper that converts po source to ts source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        convertor = po2ts.po2ts()
        output = BytesIO()
        convertor.convertstore(inputpo, output)
        return output.getvalue().decode("utf-8")

    @staticmethod
    def singleelement(storage):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(storage.units) == 1
        return storage.units[0]

    def test_simpleunit(self):
        """checks that a simple po entry definition converts properly to a ts entry"""
        minipo = r'''#: term.cpp
msgid "Term"
msgstr "asdf"'''
        tsfile = self.po2ts(minipo)
        print(tsfile)
        assert "<name>term.cpp</name>" in tsfile
        assert "<source>Term</source>" in tsfile
        assert "<translation>asdf</translation>" in tsfile
        assert "<comment>" not in tsfile

    def test_simple_unicode_unit(self):
        """checks that a simple unit with unicode strings"""
        minipo = r'''#: unicode.cpp
msgid "ßource"
msgstr "†arget"'''
        tsfile = self.po2ts(minipo)
        print(tsfile)
        print(type(tsfile))
        assert "<name>unicode.cpp</name>" in tsfile
        assert "<source>ßource</source>" in tsfile
        assert "<translation>†arget</translation>" in tsfile

    def test_fullunit(self):
        """check that an entry with various settings is converted correctly"""
        posource = """# Translator comment
#. Automatic comment
#: location.cpp:100
msgid "Source"
msgstr "Target"
"""
        tsfile = self.po2ts(posource)
        print(tsfile)
        # The other section are a duplicate of test_simplentry
        # FIXME need to think about auto vs trans comments maybe in TS v1.1
        assert "<comment>Translator comment</comment>" in tsfile

    def test_fuzzyunit(self):
        """check that we handle fuzzy units correctly"""
        posource = '''#: term.cpp
#, fuzzy
msgid "Source"
msgstr "Target"'''
        tsfile = self.po2ts(posource)
        print(tsfile)
        assert """<translation type="unfinished">Target</translation>""" in tsfile

    def test_obsolete(self):
        """test that we can take back obsolete messages"""
        posource = '''#. (obsolete)
#: term.cpp
msgid "Source"
msgstr "Target"'''
        tsfile = self.po2ts(posource)
        print(tsfile)
        assert """<translation type="obsolete">Target</translation>""" in tsfile

    def test_duplicates(self):
        """test that we can handle duplicates in the same context block"""
        posource = """#: @@@#1
msgid "English"
msgstr "a"

#: @@@#3
msgid "English"
msgstr "b"
"""
        tsfile = self.po2ts(posource)
        print(tsfile)
        assert tsfile.find("English") != tsfile.rfind("English")

    def test_linebreak(self):
        """test that we can handle linebreaks"""
        minipo = r'''#: linebreak.cpp
msgid "Line 1\n"
"Line 2"
msgstr "Linea 1\n"
"Linea 2"'''
        tsfile = self.po2ts(minipo)
        print(tsfile)
        print(type(tsfile))
        assert "<name>linebreak.cpp</name>" in tsfile
        assert (
            r"""<source>Line 1
Line 2</source>"""
            in tsfile
        )
        assert (
            r"""<translation>Linea 1
Linea 2</translation>"""
            in tsfile
        )

    def test_linebreak_consecutive(self):
        """test that we can handle consecutive linebreaks"""
        minipo = r'''#: linebreak.cpp
msgid "Line 1\n"
"\n"
"Line 3"
msgstr "Linea 1\n"
"\n"
"Linea 3"'''
        tsfile = self.po2ts(minipo)
        print(tsfile)
        print(type(tsfile))
        assert "<name>linebreak.cpp</name>" in tsfile
        assert (
            r"""<source>Line 1

Line 3</source>"""
            in tsfile
        )
        assert (
            r"""<translation>Linea 1

Linea 3</translation>"""
            in tsfile
        )


class TestPO2TSCommand(test_convert.TestConvertCommand, TestPO2TS):
    """Tests running actual po2ts commands on files"""

    convertmodule = po2ts

    expected_options = [
        "-c CONTEXT, --context=CONTEXT",
        "-t TEMPLATE, --template=TEMPLATE",
    ]
