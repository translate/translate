from io import BytesIO

from pytest import mark, raises

from translate.misc.multistring import multistring
from translate.storage import pypo, test_po


class TestHelpers:
    @staticmethod
    def test_unescape():
        assert pypo.unescape(r"koei") == "koei"
        assert pypo.unescape(r"koei\n") == "koei\n"
        assert pypo.unescape(r"koei\\") == "koei\\"
        assert pypo.unescape(r"koei\"") == 'koei"'
        assert pypo.unescape(r"koei\r") == "koei\r"

        assert pypo.unescape(r"\nkoei\n") == "\nkoei\n"
        assert pypo.unescape(r"\\koei\\") == "\\koei\\"
        assert pypo.unescape(r"\"koei\"") == '"koei"'
        assert pypo.unescape(r"\rkoei\r") == "\rkoei\r"

        assert pypo.unescape(r"\n\nkoei\n") == "\n\nkoei\n"
        assert pypo.unescape(r"\\\nkoei\\\n") == "\\\nkoei\\\n"
        assert pypo.unescape(r"\"\\koei\"\\") == '"\\koei"\\'
        assert pypo.unescape(r"\\\rkoei\r\\") == "\\\rkoei\r\\"

    @staticmethod
    def test_quoteforpo():
        """Special escaping routine to manage newlines and linewrap in PO"""
        # Simple case
        assert pypo.quoteforpo("Some test") == ['"Some test"']
        # Newline handling
        assert pypo.quoteforpo("One\nTwo\n") == ['""', '"One\\n"', '"Two\\n"']
        # First line wrapping
        assert pypo.quoteforpo(
            "A very long sentence. A very long sentence. A very long sentence. A ver"
        ) == [
            '"A very long sentence. A very long sentence. A very long sentence. A ver"'
        ]
        assert pypo.quoteforpo(
            "A very long sentence. A very long sentence. A very long sentence. A very"
        ) == [
            '""',
            '"A very long sentence. A very long sentence. A very long sentence. A very"',
        ]
        # Long line with a newline
        assert pypo.quoteforpo(
            "A very long sentence. A very long sentence. A very long sentence. A very lon\n"
        ) == [
            '""',
            '"A very long sentence. A very long sentence. A very long sentence. A very "',
            '"lon\\n"',
        ]
        assert pypo.quoteforpo(
            "A very long sentence. A very long sentence. A very long sentence. A very 123\n"
        ) == [
            '""',
            '"A very long sentence. A very long sentence. A very long sentence. A very "',
            '"123\\n"',
        ]
        # Special 77 char failure.
        assert pypo.quoteforpo(
            "Ukuba uyayiqonda into eyenzekayo, \nungaxelela i-&brandShortName; ukuba iqalise ukuthemba ufaniso lwale sayithi. \n<b>Nokuba uyayithemba isayithi, le mposiso isenokuthetha ukuba   kukho umntu \nobhucabhuca ukudibanisa kwakho.</b>"
        ) == [
            '""',
            '"Ukuba uyayiqonda into eyenzekayo, \\n"',
            '"ungaxelela i-&brandShortName; ukuba iqalise ukuthemba ufaniso lwale sayithi. "',
            '"\\n"',
            '"<b>Nokuba uyayithemba isayithi, le mposiso isenokuthetha ukuba   kukho umntu "',
            '"\\n"',
            '"obhucabhuca ukudibanisa kwakho.</b>"',
        ]

    @staticmethod
    def test_quoteforpo_escaped_quotes():
        """Ensure that we don't break \" in two when wrapping

        See :issue:`3140`
        """
        assert pypo.quoteforpo(
            """You can get a copy of an recovery key by going to "My Recovery Key" under "Manage Account"."""
        ) == [
            '""',
            '"You can get a copy of an recovery key by going to \\"My Recovery Key\\" under "',
            '"\\"Manage Account\\"."',
        ]


class TestPYPOUnit(test_po.TestPOUnit):
    UnitClass = pypo.pounit

    def test_plurals(self):
        """Tests that plurals are handled correctly."""
        unit = self.UnitClass("Cow")
        unit.msgid_plural = ['"Cows"']
        assert isinstance(unit.source, multistring)
        assert unit.source.strings == ["Cow", "Cows"]
        assert unit.source == "Cow"

        unit.target = ["Koei", "Koeie"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Koei", "Koeie"]
        assert unit.target == "Koei"

        unit.target = {0: "Koei", 3: "Koeie"}
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Koei", "Koeie"]
        assert unit.target == "Koei"

        unit.target = ["Sk\u00ear", "Sk\u00eare"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Sk\u00ear", "Sk\u00eare"]
        assert unit.target.strings == ["Sk\u00ear", "Sk\u00eare"]
        assert unit.target == "Sk\u00ear"

    def test_plural_reduction(self):
        """checks that reducing the number of plurals supplied works"""
        unit = self.UnitClass("Tree")
        unit.msgid_plural = ['"Trees"']
        assert isinstance(unit.source, multistring)
        assert unit.source.strings == ["Tree", "Trees"]
        unit.target = multistring(["Boom", "Bome", "Baie Bome"])
        assert isinstance(unit.source, multistring)
        assert unit.target.strings == ["Boom", "Bome", "Baie Bome"]
        unit.target = multistring(["Boom", "Bome"])
        assert unit.target.strings == ["Boom", "Bome"]
        unit.target = "Boom"
        # FIXME: currently assigning the target to the same as the first string won't change anything
        # we need to verify that this is the desired behaviour...
        assert unit.target.strings == ["Boom"]
        unit.target = "Een Boom"
        assert unit.target.strings == ["Een Boom"]

    def test_notes(self):
        """tests that the generic notes API works"""
        unit = self.UnitClass("File")
        unit.addnote("Which meaning of file?")
        assert str(unit) == '# Which meaning of file?\nmsgid "File"\nmsgstr ""\n'
        unit.addnote("Verb", origin="programmer")
        assert (
            str(unit) == '# Which meaning of file?\n#. Verb\nmsgid "File"\nmsgstr ""\n'
        )
        unit.addnote("Thank you", origin="translator")
        assert (
            str(unit)
            == '# Which meaning of file?\n# Thank you\n#. Verb\nmsgid "File"\nmsgstr ""\n'
        )

        assert unit.getnotes("developer") == "Verb"
        assert unit.getnotes("translator") == "Which meaning of file?\nThank you"
        assert unit.getnotes() == "Which meaning of file?\nThank you\nVerb"
        with raises(ValueError):
            unit.getnotes("devteam")

    def test_notes_withcomments(self):
        """tests that when we add notes that look like comments that we treat them properly"""
        unit = self.UnitClass("File")
        unit.addnote("# Double commented comment")
        assert str(unit) == '# # Double commented comment\nmsgid "File"\nmsgstr ""\n'
        assert unit.getnotes() == "# Double commented comment"

    def test_wrap_firstlines(self):
        """
        tests that we wrap the first line correctly a first line if longer then 71 chars
        as at 71 chars we should align the text on the left and preceed with with a msgid ""
        """
        # longest before we wrap text
        str_max = (
            "123456789 123456789 123456789 123456789 123456789 123456789 123456789 1"
        )
        unit = self.UnitClass(str_max)
        expected = 'msgid "%s"\nmsgstr ""\n' % str_max
        assert str(unit) == expected
        # at this length we wrap
        str_wrap = str_max + "2"
        unit = self.UnitClass(str_wrap)
        expected = 'msgid ""\n"%s"\nmsgstr ""\n' % str_wrap
        assert str(unit) == expected

    def test_wrap_on_newlines(self):
        """test that we wrap newlines on a real \n"""
        string = "123456789\n" * 3
        postring = ('"123456789\\n"\n' * 3)[:-1]
        unit = self.UnitClass(string)
        expected = 'msgid ""\n%s\nmsgstr ""\n' % postring
        assert str(unit) == expected

        # Now check for long newlines segments
        longstring = ("123456789 " * 10 + "\n") * 3
        expected = r"""msgid ""
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 "
"123456789 123456789 123456789 \n"
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 "
"123456789 123456789 123456789 \n"
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 "
"123456789 123456789 123456789 \n"
msgstr ""
"""
        unit = self.UnitClass(longstring)
        assert str(unit) == expected

    def test_wrap_on_max_line_length(self):
        """test that we wrap all lines on the maximum line length"""
        string = "1 3 5 7 N " * 11
        expected = (
            'msgid ""\n%s\nmsgstr ""\n'
            % '"1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 "\n"7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N "'
        )
        unit = self.UnitClass(string)
        assert str(unit) == expected

    def test_wrap_on_slash(self):
        """test that we wrap on /"""
        string = "1/3/5/7/N/" * 11
        expected = """msgid ""
"1/3/5/7/N/1/3/5/7/N/1/3/5/7/N/1/3/5/7/N/1/3/5/7/N/1/3/5/7/N/1/3/5/7/N/1/3/5/"
"7/N/1/3/5/7/N/1/3/5/7/N/1/3/5/7/N/"
msgstr ""
"""
        unit = self.UnitClass(string)
        assert str(unit) == expected

    def test_spacing_max_line(self):
        """Test that the spacing of text is done the same as msgcat."""
        idstring = "Creates a new document using an existing template iiiiiiiiiiiiiiiiiiiiiii or "
        idstring += "opens a sample document."
        expected = """msgid ""
"Creates a new document using an existing template iiiiiiiiiiiiiiiiiiiiiii or "
"opens a sample document."
msgstr ""
"""
        unit = self.UnitClass(idstring)
        assert str(unit) == expected


class TestPYPOFile(test_po.TestPOFile):
    StoreClass = pypo.pofile

    def test_combine_msgidcomments(self):
        """checks that we don't get duplicate msgid comments"""
        posource = 'msgid "test me"\nmsgstr ""'
        pofile = self.poparse(posource)
        thepo = pofile.units[0]
        thepo.msgidcomments.append('"_: first comment\\n"')
        thepo.msgidcomments.append('"_: second comment\\n"')
        regenposource = bytes(pofile).decode("utf-8")
        assert regenposource.count("_:") == 1

    def test_merge_duplicates_msgctxt(self):
        """checks that merging duplicates works for msgctxt"""
        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("msgctxt")
        print(pofile)
        assert len(pofile.units) == 2
        assert str(pofile.units[0]).count("source1") == 2
        assert str(pofile.units[1]).count("source2") == 2

    def test_merge_blanks(self):
        """checks that merging adds msgid_comments to blanks"""
        posource = (
            '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
        )
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("merge")
        assert len(pofile.units) == 2
        assert pypo.unquotefrompo(pofile.units[0].msgidcomments) == "_: source1\n"
        assert pypo.unquotefrompo(pofile.units[1].msgidcomments) == "_: source2\n"

    def test_output_str_unicode(self):
        """checks that we can str(element) which is in unicode"""
        posource = """#: nb\nmsgid "Norwegian Bokmål"\nmsgstr ""\n"""
        pofile = self.StoreClass(BytesIO(posource.encode("UTF-8")), encoding="UTF-8")
        assert len(pofile.units) == 1
        print(bytes(pofile))
        thepo = pofile.units[0]
        assert str(thepo) == posource
        # Now if we set the msgstr to Unicode
        # this is an escaped half character (1/2)
        halfstr = b"\xbd ...".decode("latin-1")
        thepo.target = halfstr
        assert halfstr in str(thepo)

    def test_posections(self):
        """checks the content of all the expected sections of a PO message"""
        posource = '# other comment\n#. automatic comment\n#: source comment\n#, fuzzy\nmsgid "One"\nmsgstr "Een"\n'
        pofile = self.poparse(posource)
        print(pofile)
        assert len(pofile.units) == 1
        assert bytes(pofile).decode("utf-8") == posource
        assert pofile.units[0].othercomments == ["# other comment\n"]
        assert pofile.units[0].automaticcomments == ["#. automatic comment\n"]
        assert pofile.units[0].sourcecomments == ["#: source comment\n"]
        assert pofile.units[0].typecomments == ["#, fuzzy\n"]

    def test_typecomments(self):
        """test typecomments handling"""
        posource = """#: 00-8C-41-10-00-00-31-10-12-05-42-44-00-2E
#, max-length:10
msgctxt "0"
msgid "Aurora"
msgstr ""
"""
        pofile = self.poparse(posource)
        print(pofile)
        assert len(pofile.units) == 1
        assert bytes(pofile).decode("utf-8") == posource
        unit = pofile.units[0]
        assert unit.typecomments == ["#, max-length:10\n"]
        assert unit.hastypecomment("max-length:10") is True
        unit.target = "Aurora"
        unit.markfuzzy()
        assert unit.typecomments == ["#, fuzzy, max-length:10\n"]
        assert unit.hastypecomment("max-length:10") is True

    def test_unassociated_comments(self):
        """tests behaviour of unassociated comments."""
        oldsource = '# old lonesome comment\n\nmsgid "one"\nmsgstr "een"\n'
        oldfile = self.poparse(oldsource)
        print(bytes(oldfile))
        assert len(oldfile.units) == 1

    def test_unicode_header(self):
        """checks that unicode header is parsed and saved correctly"""
        posource = r"""msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"
"Zkouška: něco\n"
""".encode()
        pofile = self.poparse(posource)
        assert pofile.parseheader() == {
            "Content-Transfer-Encoding": "8-bit",
            "Content-Type": "text/plain; charset=UTF-8",
            "MIME-Version": "1.0",
            "PO-Revision-Date": "2006-02-09 23:33+0200",
            "Zkouška": "něco",
        }
        update = {"zkouška": "else"}
        pofile.updateheader(add=True, **update)
        assert (
            pofile.units[0].target
            == """PO-Revision-Date: 2006-02-09 23:33+0200
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8-bit
Zkouška: else
"""
        )

    def test_prevmsgid_parse(self):
        """checks that prevmsgid (i.e. #|) is parsed and saved correctly"""
        posource = r"""msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

#, fuzzy
#| msgid "trea"
msgid "tree"
msgstr "boom"

#| msgid "trea"
#| msgid_plural "treas"
msgid "tree"
msgid_plural "trees"
msgstr[0] "boom"
msgstr[1] "bome"

#| msgctxt "context 1"
#| msgid "tast"
msgctxt "context 1a"
msgid "test"
msgstr "toets"

#| msgctxt "context 2"
#| msgid "tast"
#| msgid_plural "tasts"
msgctxt "context 2a"
msgid "test"
msgid_plural "tests"
msgstr[0] "toet"
msgstr[1] "toetse"
"""

        pofile = self.poparse(posource)

        assert pofile.units[1].prev_msgctxt == []
        assert pofile.units[1].prev_source == multistring(["trea"])

        assert pofile.units[2].prev_msgctxt == []
        assert pofile.units[2].prev_source == multistring(["trea", "treas"])

        assert pofile.units[3].prev_msgctxt == ['"context 1"']
        assert pofile.units[3].prev_source == multistring(["tast"])

        assert pofile.units[4].prev_msgctxt == ['"context 2"']
        assert pofile.units[4].prev_source == multistring(["tast", "tasts"])

        assert bytes(pofile).decode("utf-8") == posource

    def test_wrap(self):
        hello = " ".join(["Hello"] * 100)
        posource = 'msgid "{0}"\nmsgstr "{0}"\n'.format(hello).encode("utf-8")

        # Instance with no line wraps
        store = self.StoreClass(width=-1)
        store.parse(posource)
        assert bytes(store) == posource
        store.units[0].target = hello
        assert bytes(store) == posource

        # Instance with long line wraps
        store = self.StoreClass(width=1000)
        store.parse(posource)
        assert bytes(store) == posource
        store.units[0].target = hello
        assert bytes(store) == posource

        # Instance with default wraps (77)
        store = self.StoreClass()
        store.parse(posource)
        assert bytes(store) == posource
        store.units[0].target = "Hello " * 100
        # Should contain additional newlines now
        assert bytes(store) != posource

    def test_wrap_newlines(self):
        hello = "\n ".join(["Hello"] * 100)
        posource = 'msgid "{0}"\nmsgstr "{0}"\n'.format(
            hello.replace("\n", "\\n")
        ).encode("utf-8")

        # Instance with no line wraps
        store = self.StoreClass(width=-1)
        store.parse(posource)
        assert bytes(store) == posource
        store.units[0].target = hello
        assert bytes(store) == posource

        # Instance with default wraps (77)
        store = self.StoreClass()
        store.parse(posource)
        assert bytes(store) == posource
        store.units[0].target = "Hello " * 100
        # Should contain additional newlines now
        assert bytes(store) != posource

    def test_unix_newlines(self):
        """checks that unix newlines are properly parsed"""
        posource = b'msgid "test me"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        assert pofile.units[0].source == "test me"
        assert bytes(pofile) == posource

    def test_dos_newlines(self):
        """checks that dos newlines are properly parsed"""
        posource = b'#: File1\r\n#: File2\r\nmsgid "test me"\r\nmsgstr ""\r\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        assert pofile.units[0].source == "test me"
        assert pofile.units[0].getlocations() == ["File1", "File2"]
        assert bytes(pofile) == posource

    def test_mac_newlines(self):
        """checks that mac newlines are properly parsed"""
        posource = b'msgid "test me"\rmsgstr ""\r'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        assert pofile.units[0].source == "test me"
        assert bytes(pofile) == posource

    def test_mixed_newlines(self):
        """checks that mixed newlines are properly parsed"""
        posource = b"""#Comment
#: foo.c:124\r bar.c:124\r
msgid "test me"
msgstr ""
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        assert pofile.units[0].source == "test me"
        assert bytes(pofile) == posource

    def test_mixed_newlines_header(self):
        """checks that mixed newlines are properly parsed"""
        posource = b"""# Polish message file for YaST2 (@memory@).\r
# Copyright (C) 2005 SUSE Linux Products GmbH.\r
msgid ""
msgstr ""
"Project-Id-Version: YaST (@memory@)\\n"

#. Rich text title for FcoeClient in proposals
#: src/clients/fcoe-client_proposal.rb:82
msgid "FcoeClient"
msgstr "FcoeClient"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        assert pofile.units[0].source == ""
        assert pofile.units[1].source == "FcoeClient"
        print(repr(bytes(pofile)))
        assert bytes(pofile) == posource

    def test_mixed_newlines_comment(self):
        posource = b"""# scootergrisen: msgid "View your battery status and change power saving settings"\r
msgid "test me"
msgstr ""
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        assert pofile.units[0].source == "test me"
        assert bytes(pofile) == posource

    def test_bom(self):
        """checks that BOM is parsed"""
        posource = """msgid ""
msgstr ""
"Project-Id-Version: YaST (@memory@)\\n"

msgid "FcoeClient"
msgstr "FcoeClient"
""".encode(
            "utf-8-sig"
        )
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        assert pofile.units[0].source == ""
        assert pofile.units[1].source == "FcoeClient"
        assert bytes(pofile) == posource[3:]

    def test_long_msgidcomments(self):
        posource = """#: networkstatus/connectionmanager.cpp:148
msgid ""
"_: Message shown when a network connection failed.  The placeholder contains "
"the concrete description of the operation eg 'while performing this "
"operation\\n"
""
"A network connection failed %1.  Do you want to place the application in "
"offline mode?"
msgstr ""
"Připojení k síti se nezdařilo: %1. Chcete aplikaci přepnout do režimu "
"offline?"
"""
        pofile = self.poparse(posource.encode("utf-8"))
        assert len(pofile.units) == 1
        assert bytes(pofile).decode("utf-8") == posource
        posource_extra = """#: networkstatus/connectionmanager.cpp:148
msgid ""
""
"_: Message shown when a network connection failed.  The placeholder contains "
"the concrete description of the operation eg 'while performing this "
"operation\\n"
""
"A network connection failed %1.  Do you want to place the application in "
"offline mode?"
msgstr ""
"Připojení k síti se nezdařilo: %1. Chcete aplikaci přepnout do režimu "
"offline?"
"""
        pofile = self.poparse(posource_extra.encode("utf-8"))
        assert len(pofile.units) == 1
        assert bytes(pofile).decode("utf-8") == posource

    def test_incomplete(self):
        """checks that empty file raises error"""
        posource = b"""msgid ""
msgstr ""
"Project-Id-Version: YaST (@memory@)\\n"

EXTRA
"""
        with raises(ValueError):
            self.poparse(posource)

    def test_invalid(self):
        """checks that empty file raises error"""
        posource = b"""README

This is just a random text file.
"""
        with raises(ValueError):
            self.poparse(posource)

    def test_dos_newlines_write(self):
        """checks that mixed newlines are properly parsed"""
        posource = b"""msgid "test me"\r
msgstr ""\r
"""
        poexpected = b"""#, fuzzy\r
msgid "test me"\r
msgstr ""\r
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert unit.source == "test me"
        assert bytes(pofile) == posource
        unit.markfuzzy(True)
        assert bytes(pofile) == poexpected

    @mark.xfail(reason="Not sure if this can not be parsed gracefully")
    def test_mixed_newlines_typecomment(self):
        """checks that mixed newlines in typecomments are properly parsed"""
        # This was generated by translate-tookit prior to
        # issue that test_dos_newlines_write is covering was fixed.
        posource = b"""#, fuzzy
msgid "test me"\r
msgstr ""\r
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        assert pofile.units[0].source == "test me"
        assert bytes(pofile) == posource
