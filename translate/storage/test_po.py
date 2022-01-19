from io import BytesIO

from pytest import mark, raises

from translate.misc.multistring import multistring
from translate.storage import po, pypo, test_base
from translate.storage.php import phpunit


def test_roundtrip_quoting():
    specials = [
        "Fish & chips",
        "five < six",
        "six > five",
        "Use &nbsp;",
        "Use &amp;nbsp;" 'A "solution"',
        "skop 'n bal",
        '"""',
        "'''",
        "\n",
        "\t",
        "\r",
        "\\n",
        "\\t",
        "\\r",
        '\\"',
        "\r\n",
        "\\r\\n",
        "\\",
    ]
    for special in specials:
        quoted_special = pypo.quoteforpo(special)
        unquoted_special = pypo.unquotefrompo(quoted_special)
        print(
            "special: %r\nquoted: %r\nunquoted: %r\n"
            % (special, quoted_special, unquoted_special)
        )
        assert special == unquoted_special


class TestPOUnit(test_base.TestTranslationUnit):
    UnitClass = po.pounit

    def test_istranslatable(self):
        """Tests for the correct behaviour of istranslatable()."""
        unit = self.UnitClass("Message")
        assert unit.istranslatable()

        unit.source = " "
        assert unit.istranslatable()

        unit.source = ""
        assert not unit.istranslatable()
        # simulate a header
        unit.target = "PO-Revision-Date: 2006-02-09 23:33+0200\n"
        assert unit.isheader()
        assert not unit.istranslatable()

        unit.source = "Message"
        unit.target = "Boodskap"
        unit.makeobsolete()
        assert not unit.istranslatable()

    def test_locations(self):
        """Tests that we can add and retrieve error messages for a unit."""

        def locations_helper(location):
            unit = self.UnitClass()
            assert len(unit.getlocations()) == 0
            unit.addlocation(location)
            assert len(unit.getlocations()) == 1
            assert unit.getlocations() == [location]

        locations_helper("key")
        locations_helper("file.c:100")
        locations_helper("I am a key")
        locations_helper("unicoḓe key")

    def test_nongettext_location(self):
        """test that we correctly handle a non-gettext (file:linenumber) location"""
        u = self.UnitClass("")
        u.addlocation("programming/C/programming.xml:44(para)")
        assert "programming/C/programming.xml:44(para)" in str(u)
        assert "programming/C/programming.xml:44(para)" in u.getlocations()

    def test_adding_empty_note(self):
        unit = self.UnitClass("bla")
        print(str(unit))
        assert "#" not in str(unit)
        for empty_string in ["", " ", "\t", "\n"]:
            unit.addnote(empty_string)
            assert "#" not in str(unit)

    def test_markreview(self):
        """Tests if we can mark the unit to need review."""
        unit = self.unit
        # We have to explicitly set the target to nothing, otherwise xliff
        # tests will fail.
        # Can we make it default behavior for the UnitClass?
        unit.target = ""

        unit.addnote("Test note 1", origin="translator")
        unit.addnote("Test note 2", origin="translator")
        original_notes = unit.getnotes(origin="translator")

        assert not unit.isreview()
        unit.markreviewneeded()
        print(unit.getnotes())
        assert unit.isreview()
        unit.markreviewneeded(False)
        assert not unit.isreview()
        assert unit.getnotes(origin="translator") == original_notes
        unit.markreviewneeded(explanation="Double check spelling.")
        assert unit.isreview()
        notes = unit.getnotes(origin="translator")
        assert notes.count("Double check spelling.") == 1

    def test_errors(self):
        """Tests that we can add and retrieve error messages for a unit."""
        unit = self.unit

        assert len(unit.geterrors()) == 0
        unit.adderror(errorname="test1", errortext="Test error message 1.")
        unit.adderror(errorname="test2", errortext="Test error message 2.")
        unit.adderror(errorname="test3", errortext="Test error message 3.")
        assert len(unit.geterrors()) == 3
        assert unit.geterrors()["test1"] == "Test error message 1."
        assert unit.geterrors()["test2"] == "Test error message 2."
        assert unit.geterrors()["test3"] == "Test error message 3."
        unit.adderror(errorname="test1", errortext="New error 1.")
        assert unit.geterrors()["test1"] == "New error 1."

    def test_no_plural_settarget(self):
        """tests that target handling of file with no plural is correct"""
        # plain text, no plural test
        unit = self.UnitClass("Tree")
        unit.target = "ki"
        assert not unit.hasplural()

        # plural test with multistring
        unit.source = ["Tree", "Trees"]
        assert unit.source.strings == ["Tree", "Trees"]
        assert unit.hasplural()
        unit.target = multistring(["ki", "ni ki"])
        assert unit.target.strings == ["ki", "ni ki"]

        # test of msgid with no plural and msgstr with plural
        unit = self.UnitClass("Tree")
        with raises(ValueError):
            unit.target = ["ki", "ni ki"]
        assert not unit.hasplural()

    def test_wrapping_bug(self):
        """This tests for a wrapping bug that existed at some stage."""
        unit = self.UnitClass("")
        message = 'Projeke ya Pootle ka boyona e ho <a href="http://translate.sourceforge.net/">translate.sourceforge.net</a> moo o ka fumanang dintlha ka source code, di mailing list jwalo jwalo.'
        unit.target = message
        print(unit.target)
        assert unit.target == message

    def test_extract_msgidcomments_from_text(self):
        """Test that KDE style comments are extracted correctly."""
        unit = self.UnitClass("test source")

        kdetext = "_: Simple comment\nsimple text"
        assert unit._extract_msgidcomments(kdetext) == "Simple comment"

    def test_isheader(self):
        """checks that we deal correctly with headers."""
        unit = self.UnitClass()
        unit.target = "PO-Revision-Date: 2006-02-09 23:33+0200\n"
        assert unit.isheader()
        unit.source = "Some English string"
        assert not unit.isheader()
        unit.source = "Goeiemôre"
        assert not unit.isheader()

    def test_buildfromunit(self):
        unit = self.UnitClass("test source")
        unit_copy = self.UnitClass.buildfromunit(unit)
        assert unit is not unit_copy
        assert unit == unit_copy

        # Test with a unit without copy() method (will call base.buildfromunit)
        unit = phpunit("$test_source")
        unit_copy = self.UnitClass.buildfromunit(unit)
        unit.setid(unit_copy.getid())
        assert unit.getid() == unit_copy.getid()
        assert unit is not unit_copy
        assert unit == unit_copy


#     def test_rich_source(self):
#         unit = self.unit
#         unit.rich_source = [['a', X('42'), 'c']]
#         assert unit.rich_source == [['a\ufffcc']]

#     def test_rich_target(self):
#         unit = self.unit
#         unit.rich_target = [['a', G('42', ['b']), 'c']]
#         assert unit.rich_target == [['abc']]


class TestPOFile(test_base.TestTranslationStore):
    StoreClass = po.pofile

    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = BytesIO(
            posource.encode() if isinstance(posource, str) else posource
        )
        pofile = self.StoreClass(dummyfile)
        return pofile

    def poregen(self, posource):
        """helper that converts po source to pofile object and back"""
        return bytes(self.poparse(posource))

    def pomerge(self, oldmessage, newmessage, authoritative):
        """helper that merges two messages"""
        oldpofile = self.poparse(oldmessage)
        oldunit = oldpofile.units[0]
        if newmessage:
            newpofile = self.poparse(newmessage)
            newunit = newpofile.units[0]
        else:
            newunit = oldpofile.UnitClass()
        oldunit.merge(newunit, authoritative=authoritative)
        print(oldunit)
        return str(oldunit)

    def poreflow(self, posource):
        """Helper to parse and reflow all text according to our code."""
        pofile = self.poparse(posource)
        for u in pofile.units:
            # force rewrapping:
            u.source = u.source
            u.target = u.target
        return bytes(pofile).decode("utf-8")

    def test_context_only(self):
        """Checks that an empty msgid with msgctxt is handled correctly."""
        posource = """msgctxt "CONTEXT"
msgid ""
msgstr ""
"""
        pofile = self.poparse(posource)
        assert pofile.units[0].istranslatable()
        assert not pofile.units[0].isheader()
        # we were not generating output for thse at some stage
        assert bytes(pofile)

    def test_simpleentry(self):
        """checks that a simple po entry is parsed correctly"""
        posource = '#: test.c:100 test.c:101\nmsgid "test"\nmsgstr "rest"\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        thepo = pofile.units[0]
        assert thepo.getlocations() == ["test.c:100", "test.c:101"]
        assert thepo.source == "test"
        assert thepo.target == "rest"

    def test_copy(self):
        """checks that we can copy all the needed PO fields"""
        posource = '''# TRANSLATOR-COMMENTS
#. AUTOMATIC-COMMENTS
#: REFERENCE...
#, fuzzy
msgctxt "CONTEXT"
msgid "UNTRANSLATED-STRING"
msgstr "TRANSLATED-STRING"'''
        pofile = self.poparse(posource)
        oldunit = pofile.units[0]
        newunit = oldunit.copy()
        assert newunit == oldunit

    def test_parse_source_string(self):
        """parse a string"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1

    def test_parse_file(self):
        """test parsing a real file"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1

    def test_unicode(self):
        """check that the po class can handle Unicode characters"""
        posource = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n#: test.c\nmsgid "test"\nmsgstr "rest\xe2\x80\xa6"\n'
        pofile = self.poparse(posource)
        print(pofile)
        assert len(pofile.units) == 2

    def test_plurals(self):
        posource = r"""msgid "Cow"
msgid_plural "Cows"
msgstr[0] "Koei"
msgstr[1] "Koeie"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert isinstance(unit.target, multistring)
        print(unit.target.strings)
        assert unit.target == "Koei"
        assert unit.target.strings == ["Koei", "Koeie"]

        posource = r"""msgid "Skaap"
msgid_plural "Skape"
msgstr[0] "Sheep"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert isinstance(unit.target, multistring)
        print(unit.target.strings)
        assert unit.target == "Sheep"
        assert unit.target.strings == ["Sheep"]

    def test_plural_unicode(self):
        """tests that all parts of the multistring are unicode."""
        posource = r"""msgid "Ców"
msgid_plural "Cóws"
msgstr[0] "Kóei"
msgstr[1] "Kóeie"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        assert isinstance(unit.source, multistring)
        assert isinstance(unit.source.strings[1], str)

    def test_nongettext_location(self):
        """test that we correctly handle a non-gettext (file:linenumber) location"""
        posource = (
            '#: programming/C/programming.xml:44(para)\nmsgid "test"\nmsgstr "rest"\n'
        )
        pofile = self.poparse(posource)
        u = pofile.units[-1]

        locations = u.getlocations()
        print(locations)
        assert len(locations) == 1
        assert locations[0] == "programming/C/programming.xml:44(para)"
        assert isinstance(locations[0], str)

    def test_percent_location(self):
        """test that we correctly handle a location with percent chars"""
        posource = (
            '#: /foo/bar/%%var%%www%%about.html:44\nmsgid "test"\nmsgstr "rest"\n'
        )
        pofile = self.poparse(posource)
        u = pofile.units[-1]

        locations = u.getlocations()
        print(locations)
        assert len(locations) == 1
        assert locations[0] == "/foo/bar/%%var%%www%%about.html:44"

    @mark.xfail(reason="Not Implemented")
    def test_kde_plurals(self):
        """Tests kde-style plurals. (Bug: 191)"""
        posource = r"""msgid "_n Singular\n"
"Plural"
msgstr "Een\n"
"Twee\n"
"Drie"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert unit.hasplural()
        assert isinstance(unit.source, multistring)
        print(unit.source.strings)
        assert unit.source == "Singular"
        assert unit.source.strings == ["Singular", "Plural"]
        assert isinstance(unit.target, multistring)
        print(unit.target.strings)
        assert unit.target == "Een"
        assert unit.target.strings == ["Een", "Twee", "Drie"]

    def test_empty_lines_notes(self):
        """Tests that empty comment lines are preserved"""
        posource = r"""# License name
#
# license line 1
# license line 2
# license line 3
msgid ""
msgstr "POT-Creation-Date: 2006-03-08 17:30+0200\n"
"""
        pofile = self.poparse(posource)
        assert bytes(pofile).decode("utf-8") == posource

    def test_fuzzy(self):
        """checks that fuzzy functionality works as expected"""
        posource = '#, fuzzy\nmsgid "ball"\nmsgstr "bal"\n'
        expectednonfuzzy = 'msgid "ball"\nmsgstr "bal"\n'
        pofile = self.poparse(posource)
        print(pofile)
        assert pofile.units[0].isfuzzy()
        pofile.units[0].markfuzzy(False)
        assert not pofile.units[0].isfuzzy()
        assert bytes(pofile).decode("utf-8") == expectednonfuzzy

        posource = '#, fuzzy, python-format\nmsgid "ball"\nmsgstr "bal"\n'
        expectednonfuzzy = '#, python-format\nmsgid "ball"\nmsgstr "bal"\n'
        expectedfuzzyagain = (
            '#, fuzzy, python-format\nmsgid "ball"\nmsgstr "bal"\n'  # must be sorted
        )
        pofile = self.poparse(posource)
        print(pofile)
        assert pofile.units[0].isfuzzy()
        pofile.units[0].markfuzzy(False)
        assert not pofile.units[0].isfuzzy()
        assert bytes(pofile).decode("utf-8") == expectednonfuzzy
        pofile.units[0].markfuzzy()
        print(bytes(pofile))
        assert bytes(pofile).decode("utf-8") == expectedfuzzyagain

        # test the same, but with flags in a different order
        posource = '#, python-format, fuzzy\nmsgid "ball"\nmsgstr "bal"\n'
        expectednonfuzzy = '#, python-format\nmsgid "ball"\nmsgstr "bal"\n'
        expectedfuzzyagain = (
            '#, fuzzy, python-format\nmsgid "ball"\nmsgstr "bal"\n'  # must be sorted
        )
        pofile = self.poparse(posource)
        print(pofile)
        assert pofile.units[0].isfuzzy()
        pofile.units[0].markfuzzy(False)
        assert not pofile.units[0].isfuzzy()
        print(bytes(pofile))
        assert bytes(pofile).decode("utf-8") == expectednonfuzzy
        pofile.units[0].markfuzzy()
        print(bytes(pofile))
        assert bytes(pofile).decode("utf-8") == expectedfuzzyagain

    @mark.xfail(reason="Check differing behaviours between pypo and cpo")
    def test_makeobsolete_untranslated(self):
        """Tests making an untranslated unit obsolete"""
        posource = '#. The automatic one\n#: test.c\nmsgid "test"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        print(bytes(pofile))
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert str(unit) == ""
        # a better way might be for pomerge/pot2po to remove the unit

    def test_merging_automaticcomments(self):
        """checks that new automatic comments override old ones"""
        oldsource = '#. old comment\n#: line:10\nmsgid "One"\nmsgstr "Een"\n'
        newsource = '#. new comment\n#: line:10\nmsgid "One"\nmsgstr ""\n'
        expected = '#. new comment\n#: line:10\nmsgid "One"\nmsgstr "Een"\n'
        assert self.pomerge(newsource, oldsource, authoritative=True) == expected

    def test_malformed_units(self):
        """Test that we handle malformed units reasonably."""
        posource = (
            'msgid "thing\nmsgstr "ding"\nmsgid "Second thing"\nmsgstr "Tweede ding"\n'
        )
        with raises(ValueError):
            self.poparse(posource)

    def test_malformed_obsolete_units(self):
        """Test that we handle malformed obsolete units reasonably."""
        posource = """msgid "thing"
msgstr "ding"

#~ msgid "Second thing"
#~ msgstr "Tweede ding"
#~ msgid "Third thing"
#~ msgstr "Derde ding"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 3

    def test_uniforum_po(self):
        """Test that we handle Uniforum PO files."""
        posource = """# File: ../somefile.cpp, line: 33
msgid "thing"
msgstr "ding"
#
# File: anotherfile.cpp, line: 34
msgid "second"
msgstr "tweede"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        # FIXME we still need to handle this correctly for proper Uniforum support if required
        # assert pofile.units[0].getlocations() == "File: somefile, line: 300"
        # assert pofile.units[1].getlocations() == "File: anotherfile, line: 200"

    def test_obsolete(self):
        """Tests that obsolete messages work"""
        posource = '#~ msgid "Old thing"\n#~ msgstr "Ou ding"\n'
        pofile = self.poparse(posource)
        assert pofile.isempty()
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert unit.isobsolete()
        assert bytes(pofile).decode("utf-8") == posource

        posource = """msgid "one"
msgstr "een"

#, fuzzy
#~ msgid "File not found."
#~ msgid_plural "Files not found."
#~ msgstr[0] "Leer(s) nie gevind nie."
#~ msgstr[1] "Leer(s) nie gevind nie."
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        unit = pofile.units[1]
        assert unit.isobsolete()

        print(bytes(pofile))
        # Doesn't work with CPO if obsolete units are mixed with non-obsolete units
        assert bytes(pofile).decode("utf-8") == posource
        unit.resurrect()
        assert unit.hasplural()

    def test_obsolete_with_prev_msgid(self):
        """Tests that obsolete messages work"""
        # Bug 1429
        posource = r"""msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "one"
msgstr "een"

#, fuzzy
#~| msgid ""
#~| "You cannot read anything except web pages with\n"
#~| "this plugin, sorry."
#~ msgid "You cannot read anything except web pages with this plugin, sorry."
#~ msgstr ""
#~ "Mit diesem Modul können leider ausschließlich Webseiten vorgelesen werden."
"""
        pofile = self.poparse(posource.encode())
        assert len(pofile.units) == 3
        unit = pofile.units[2]
        print(str(unit))
        assert unit.isobsolete()
        assert unit.isfuzzy()
        assert not unit.istranslatable()

        print(posource)
        print(bytes(pofile))
        assert bytes(pofile).decode("utf-8") == posource

    def test_header_escapes(self):
        pofile = self.StoreClass()
        pofile.updateheader(
            add=True,
            **{
                "Report-Msgid-Bugs-To": r"http://qa.openoffice.org/issues/enter_bug.cgi?subcomponent=ui&comment=&short_desc=Localization%20issue%20in%20file%3A%20dbaccess\source\core\resource.oo&component=l10n&form_name=enter_issue"
            }
        )
        filecontents = bytes(pofile).decode("utf-8")
        print(filecontents)
        # We need to make sure that the \r didn't get misrepresented as a
        # carriage return, but as a slash (escaped) followed by a normal 'r'
        assert r"\source\core\resource" in pofile.header().target
        assert r"re\\resource" in filecontents

    def test_makeobsolete(self):
        """Tests making a unit obsolete"""
        posource = '#. The automatic one\n#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poexpected = '#~ msgid "test"\n#~ msgstr "rest"\n'
        pofile = self.poparse(posource)
        print(pofile)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print(pofile)
        assert str(unit) == poexpected

    def test_makeobsolete_plural(self):
        """Tests making a plural unit obsolete"""
        posource = r"""msgid "Cow"
msgid_plural "Cows"
msgstr[0] "Koei"
msgstr[1] "Koeie"
"""
        poexpected = """#~ msgid "Cow"
#~ msgid_plural "Cows"
#~ msgstr[0] "Koei"
#~ msgstr[1] "Koeie"
"""
        pofile = self.poparse(posource)
        print(pofile)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print(pofile)
        assert str(unit) == poexpected

    def test_makeobsolete_msgctxt(self):
        """Tests making a unit with msgctxt obsolete"""
        posource = '#: test.c\nmsgctxt "Context"\nmsgid "test"\nmsgstr "rest"\n'
        poexpected = '#~ msgctxt "Context"\n#~ msgid "test"\n#~ msgstr "rest"\n'
        pofile = self.poparse(posource)
        print(pofile)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        assert unit.istranslatable()
        unit.makeobsolete()
        assert unit.isobsolete()
        assert not unit.istranslatable()
        print(pofile)
        assert str(unit) == poexpected

    def test_makeobsolete_msgidcomments(self):
        """Tests making a unit with msgidcomments obsolete"""
        posource = '#: first.c\nmsgid ""\n"_: first.c\\n"\n"test"\nmsgstr "rest"\n\n#: second.c\nmsgid ""\n"_: second.c\\n"\n"test"\nmsgstr "rest"'
        poexpected = '#~ msgid ""\n#~ "_: first.c\\n"\n#~ "test"\n#~ msgstr "rest"\n'
        print("Source:\n%s" % posource)
        print("Expected:\n%s" % poexpected)
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print("Result:\n%s" % pofile)
        assert str(unit) == poexpected

    def test_multiline_obsolete(self):
        """Tests for correct output of mulitline obsolete messages"""
        posource = '#~ msgid ""\n#~ "Old thing\\n"\n#~ "Second old thing"\n#~ msgstr ""\n#~ "Ou ding\\n"\n#~ "Tweede ou ding"\n'
        pofile = self.poparse(posource)
        assert pofile.isempty()
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert unit.isobsolete()
        print(bytes(pofile))
        print(posource)
        assert bytes(pofile).decode("utf-8") == posource

    def test_merge_duplicates(self):
        """checks that merging duplicates works"""
        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        pofile.removeduplicates("merge")
        assert len(pofile.units) == 1
        assert pofile.units[0].getlocations() == ["source1", "source2"]
        print(pofile)

    def test_merge_mixed_sources(self):
        """checks that merging works with different source location styles"""
        posource = """
#: source1
#: source2
msgid "test"
msgstr ""

#: source1 source2
msgid "test"
msgstr ""
"""
        pofile = self.poparse(posource)
        print(bytes(pofile))
        pofile.removeduplicates("merge")
        print(bytes(pofile))
        assert len(pofile.units) == 1
        assert pofile.units[0].getlocations() == ["source1", "source2"]

    def test_parse_context(self):
        """Tests that msgctxt is parsed correctly and that it is accessible via the api methods."""
        posource = """# Test comment
#: source1
msgctxt "noun"
msgid "convert"
msgstr "bekeerling"

# Test comment 2
#: source2
msgctxt "verb"
msgid "convert"
msgstr "omskakel"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == "noun"
        assert unit.getnotes() == "Test comment"

        unit = pofile.units[1]
        assert unit.getcontext() == "verb"
        assert unit.getnotes() == "Test comment 2"

    def test_parse_advanced_context(self):
        """Tests that some weird possible msgctxt scenarios are parsed correctly."""
        posource = r"""# Test multiline context
#: source1
msgctxt "Noun."
" A person that changes his or her ways."
msgid "convert"
msgstr "bekeerling"

# Test quotes
#: source2
msgctxt "Verb. Converting from \"something\" to \"something else\"."
msgid "convert"
msgstr "omskakel"

# Test quotes, newlines and multiline.
#: source3
msgctxt "Verb.\nConverting from \"something\""
" to \"something else\"."
msgid "convert"
msgstr "omskakel"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == "Noun. A person that changes his or her ways."
        assert unit.getnotes() == "Test multiline context"

        unit = pofile.units[1]
        assert (
            unit.getcontext()
            == 'Verb. Converting from "something" to "something else".'
        )
        assert unit.getnotes() == "Test quotes"

        unit = pofile.units[2]
        assert (
            unit.getcontext()
            == 'Verb.\nConverting from "something" to "something else".'
        )
        assert unit.getnotes() == "Test quotes, newlines and multiline."

    def test_kde_context(self):
        """Tests that kde-style msgid comments can be retrieved via getcontext()."""
        posource = r"""# Test comment
#: source1
msgid ""
"_: Noun\n"
"convert"
msgstr "bekeerling"

# Test comment 2
#: source2
msgid ""
"_: Verb. _: "
"The action of changing.\n"
"convert"
msgstr "omskakel"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == "Noun"
        assert unit.getnotes() == "Test comment"

        unit = pofile.units[1]
        assert unit.getcontext() == "Verb. _: The action of changing."
        assert unit.getnotes() == "Test comment 2"

    def test_broken_kde_context(self):
        posource = """msgid "Broken _: here"
msgstr "Broken _: here"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        assert unit.source == "Broken _: here"
        assert unit.target == "Broken _: here"

    def test_id(self):
        """checks that ids work correctly"""
        posource = r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "plant"
msgstr ""

msgid ""
"_: Noun\n"
"convert"
msgstr "bekeerling"

msgctxt "verb"
msgid ""
"convert"
msgstr "omskakel"

msgid "tree"
msgid_plural "trees"
msgstr[0] ""
"""
        pofile = self.poparse(posource)
        assert pofile.units[0].getid() == ""
        assert pofile.units[1].getid() == "plant"
        assert pofile.units[2].getid() == "_: Noun\nconvert"
        assert pofile.units[3].getid() == "verb\04convert"
        # Gettext does not consider the plural to determine duplicates, only
        # the msgid. For generation of .mo files, we might want to use this
        # code to generate the entry for the hash table, but for now, it is
        # commented out for conformance to gettext.

    #        assert pofile.units[4].getid() == "tree\0trees"

    def test_non_ascii_header_comments(self):
        posource = r"""
# Tëśt þis.
# Hé Há Hó.
#. Lêkkør.
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "a"
msgstr "b"
"""
        pofile = self.poparse(posource)
        for line in pofile.units[0].getnotes():
            assert isinstance(line, str)

    def test_non_ascii_header_comments_2(self):
        posource = r"""
# Copyright bla.
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Last-Translator: Tránslátór\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "a"
msgstr "b"
"""
        pofile = self.poparse(posource)
        assert "Tránslátór" in pofile.units[0].target
        header_dict = pofile.parseheader()
        assert "Last-Translator" in header_dict
        assert header_dict["Last-Translator"] == "Tránslátór"

        # let's test the same with latin-1:
        posource = r"""
# Copyright bla.
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Last-Translator: Tránslátór\n"
"Content-Type: text/plain; charset=ISO-8859-1\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "a"
msgstr "b"
""".encode(
            "ISO-8859-1"
        )

        pofile = self.poparse(posource)
        assert "Tránslátór" in pofile.units[0].target
        header_dict = pofile.parseheader()
        assert "Last-Translator" in header_dict
        assert header_dict["Last-Translator"] == "Tránslátór"

    def test_final_slash(self):
        """Test that \\ as last character is correcly interpreted (bug 960)."""
        posource = r"""
msgid ""
msgstr ""
"Content-Type: text/plain; charset=utf-8\n"

#: System-Support,Project>>decideAboutCreatingBlank:
msgid "I cannot locate the project\\"
msgstr "プロジェクトが見つかりませんでした"
"""
        pofile1 = self.poparse(posource)
        print(pofile1.units[1].source)
        assert pofile1.units[1].source == "I cannot locate the project\\"
        pofile2 = self.poparse(bytes(pofile1))
        print(bytes(pofile2))
        assert bytes(pofile1) == bytes(pofile2)

    def test_unfinished_lines(self):
        """Test that we reasonably handle lines with a single quote."""
        posource = r"""
msgid ""
msgstr ""
"Content-Type: text/plain; charset=utf-8\n"

msgid "I cannot locate the project\\"
msgstr "start thing dingis fish"
"
"
"""
        with raises(ValueError):
            self.poparse(posource)

    def test_encoding_change(self):
        posource = r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=ISO-8859-1\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "a"
msgstr "d"
"""
        posource = posource.encode("utf-8")
        pofile = self.poparse(posource)
        unit = pofile.units[1]
        unit.target = "ḓ"
        contents = bytes(pofile)
        assert b'msgstr "\xe1\xb8\x93"' in contents
        assert b"charset=UTF-8" in contents

    def test_istranslated(self):
        """checks that istranslated works ok."""
        posource = r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=ISO-8859-1\n"
"Content-Transfer-Encoding: 8-bit\n"

msgid "a"
msgid_plural "aa"
msgstr[0] ""
"""
        pofile = self.poparse(posource)
        unit = pofile.units[1]
        print(str(unit))
        assert "msgid_plural" in str(unit)
        assert not unit.istranslated()
        assert unit.get_state_n() == 0

    def test_wrapping(self):
        """This tests that we wrap like gettext."""
        posource = r"""#: file.h:1
msgid "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345"
msgstr "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345"
"""
        # should be unchanged:
        assert self.poreflow(posource) == posource

        posource = r"""#: 2
msgid "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
msgstr "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
"""
        posource_wanted = r"""#: 2
msgid ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
msgstr ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
"""
        assert self.poreflow(posource) == posource_wanted

        posource = r"""#: 7
msgid "bla\t12345 12345 12345 12345 12345 12 12345 12345 12345 12345 12345 12345 123"
msgstr "bla\t12345 12345 12345 12345 12345 15 12345 12345 12345 12345 12345 12345 123"
"""
        posource_wanted = r"""#: 7
msgid ""
"bla\t12345 12345 12345 12345 12345 12 12345 12345 12345 12345 12345 12345 123"
msgstr ""
"bla\t12345 12345 12345 12345 12345 15 12345 12345 12345 12345 12345 12345 123"
"""
        assert self.poreflow(posource) == posource_wanted

        posource = r"""#: 7
msgid "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
msgstr "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
"""
        posource_wanted = r"""#: 7
msgid ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 "
"1"
msgstr ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 "
"1"
"""
        assert self.poreflow(posource) == posource_wanted

        posource = r"""#: 8
msgid "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1234\n1234"
msgstr "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1234\n1234"

#: 9
msgid "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345\n12345"
msgstr "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345\n12345"
"""
        posource_wanted = r"""#: 8
msgid ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1234\n"
"1234"
msgstr ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1234\n"
"1234"

#: 9
msgid ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 "
"12345\n"
"12345"
msgstr ""
"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 "
"12345\n"
"12345"
"""
        assert self.poreflow(posource) == posource_wanted

        posource = r"""#: 10
msgid "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
msgstr "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
"""
        posource_wanted = r"""#: 10
msgid ""
"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
"\\"
msgstr ""
"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
"\\"
"""
        assert self.poreflow(posource) == posource_wanted

    def test_wrapping_cjk(self):
        posource = r"""msgid ""
msgstr "Content-Type: text/plain; charset=utf-8\n"

msgid "test"
msgstr ""
"効率的なバグの報告はPostGISの開発を助ける本質的な方法です。最も効率的なバグ報"
"告は、PostGIS開発者がそれを再現できるようにすることで、それの引き金となったス"
"""
        assert self.poreflow(posource) == posource

    def test_wrap_gettext(self):
        posource = r"""# Test
msgid ""
msgstr ""
"Project-Id-Version: kmail\n"
"POT-Creation-Date: 2020-05-11 04:03+0200\n"
"PO-Revision-Date: 2020-05-12 14:13+0000\n"
"Last-Translator: Roman Savochenko <roman@oscada.org>\n"
"Language-Team: Ukrainian <https://mirror.git.trinitydesktop.org/weblate/"
"projects/tdepim/kmail/uk/>\n"
"Language: uk\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2 && n"
"%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;\n"
"X-Generator: Weblate 4.0.4\n"

#: configuredialog.cpp:4580
msgid ""
"x: to be continued with \"do not loop\", \"loop in current folder\", and "
"\"loop in all folders\".\n"
"When trying to find unread messages:"
msgstr "При спробі знайти не прочитані повідомлення:"

msgid ""
"You can get a copy of your Recovery Key by going to &syncBrand.shortName."
"label; Options on your other device, and selecting  \"My Recovery Key\" "
"under \"Manage Account\"."
msgstr ""
"""
        assert self.poreflow(posource) == posource

    def test_msgidcomments(self):
        posource = r"""
msgid ""
msgstr ""
"PO-Revision-Date: 2006-02-09 23:33+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=ISO-8859-1\n"
"Content-Transfer-Encoding: 8-bit\n"

# the one in the msgid should be "swallowed", but not in msgstr
msgid ""
"_: An archaic KDE context comment\n"
"The actual source text"
msgstr ""
"_: I'll be clever and translate in a text editor and duplicate the KDE comment"
"""
        pofile = self.poparse(posource)
        unit = pofile.units[1]
        assert unit.source == "The actual source text"
        assert unit.target.startswith("_: ")

    def test_unicode_ids(self):
        posource = b"""
msgid ""
msgstr ""
"Content-Type: application/x-publican; charset=UTF-8\\n"

msgid "Rapha\xc3\xabl"
msgstr ""

msgid "Rapha\xc3\xabl2"
msgstr ""
"""
        pofile = self.poparse(posource)
        unit = pofile.units[2]
        assert unit.source == "Raphaël2"
        unit = pofile.units[1]
        assert unit.source == "Raphaël"

    def test_syntax_error(self):
        posource = b"""
#| identified as a comment
#|raise an infinite loop bug!
msgid "text"
msgstr "texte"
"""
        with raises(ValueError):
            self.poparse(posource)

    def test_invalid(self):
        posource = b"""
msg
"""
        with raises(ValueError):
            self.poparse(posource)

    def test_wrapped_msgid(self):
        posource = b"""
#| msgid "some"
#|"old text"
msgid "text"
msgstr "texte"
"""
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        if not hasattr(pofile, "_gpo_memory_file"):
            assert unit.prev_source == "someold text"
        assert unit.source == "text"

    def test_missing_plural(self):
        posource = b"""
msgid "text"
msgid_plural "texts"
msgstr "texte"
"""
        with raises(ValueError):
            self.poparse(posource)
