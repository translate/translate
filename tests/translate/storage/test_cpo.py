from io import BytesIO
from typing import cast

from pytest import importorskip, mark, raises

from translate.misc.multistring import multistring

from . import test_po

cpo = importorskip("translate.storage.cpo", exc_type=ImportError)


class TestCPOUnit(test_po.TestPOUnit):
    UnitClass = cpo.pounit

    def test_plurals(self) -> None:
        """Tests that plurals are handled correctly."""
        unit = self.UnitClass("Cow")
        unit.msgid_plural = ["Cows"]
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

    def test_plural_reduction(self) -> None:
        """Checks that reducing the number of plurals supplied works."""
        unit = self.UnitClass("Tree")
        unit.msgid_plural = ["Trees"]
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
        assert cast("multistring", unit.target).strings[0] == "Boom"
        unit.target = "Een Boom"
        assert cast("multistring", unit.target).strings == ["Een Boom"]

    def test_notes(self) -> None:
        """Tests that the generic notes API works."""
        unit = self.UnitClass("File")
        assert unit.getnotes() == ""
        unit.addnote("Which meaning of file?")
        assert unit.getnotes("translator") == "Which meaning of file?"
        assert unit.getnotes("developer") == ""
        unit.addnote("Verb", origin="programmer")
        assert unit.getnotes("developer") == "Verb"
        unit.addnote("Thank you", origin="translator")
        assert unit.getnotes("translator") == "Which meaning of file?\nThank you"
        assert unit.getnotes() == "Which meaning of file?\nThank you\nVerb"
        with raises(ValueError):
            unit.getnotes("devteam")

    def test_notes_withcomments(self) -> None:
        """Tests that when we add notes that look like comments that we treat them properly."""
        unit = self.UnitClass("File")
        unit.addnote("# Double commented comment")
        assert unit.getnotes() == "# Double commented comment"
        assert not unit.hastypecomment("c-format")


class TestCPOFile(test_po.TestPOFile):
    StoreClass = cpo.pofile

    @mark.skip(reason="Native gettext doesn't handle \\r\\r\\n line endings")
    def test_unusual_line_endings(self) -> None:
        r"""Skip this test for CPO as native gettext doesn't support \r\r\n."""

    def test_msgidcomments(self) -> None:
        """Checks that we handle msgid comments."""
        posource = 'msgid "test me"\nmsgstr ""'
        pofile = self.poparse(posource)
        thepo = pofile.units[0]
        thepo.msgidcomment = "first comment"
        print(pofile)
        print("Blah", thepo.source)
        assert thepo.source == "test me"
        thepo.msgidcomment = "second comment"
        assert bytes(pofile).count(b"_:") == 1

    @mark.xfail(reason="Were disabled during port of Pypo to cPO - they might work")
    def test_merge_duplicates_msgctxt(self) -> None:
        """Checks that merging duplicates works for msgctxt."""
        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("msgctxt")
        print(pofile)
        assert len(pofile.units) == 2
        assert str(pofile.units[0]).count("source1") == 2
        assert str(pofile.units[1]).count("source2") == 2

    @mark.xfail(reason="Were disabled during port of Pypo to cPO - they might work")
    def test_merge_blanks(self) -> None:
        """Checks that merging adds msgid_comments to blanks."""
        posource = (
            '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
        )
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("merge")
        assert len(pofile.units) == 2
        print(pofile.units[0].msgidcomments)
        print(pofile.units[1].msgidcomments)
        assert cpo.unquotefrompo(pofile.units[0].msgidcomments) == "_: source1\n"
        assert cpo.unquotefrompo(pofile.units[1].msgidcomments) == "_: source2\n"

    @mark.xfail(reason="Were disabled during port of Pypo to cPO - they might work")
    def test_msgid_comment(self) -> None:
        """Checks that when adding msgid_comments we place them on a newline."""
        posource = '#: source0\nmsgid "Same"\nmsgstr ""\n\n#: source1\nmsgid "Same"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("msgid_comment")
        assert len(pofile.units) == 2
        assert cpo.unquotefrompo(pofile.units[0].msgidcomments) == "_: source0\n"
        assert cpo.unquotefrompo(pofile.units[1].msgidcomments) == "_: source1\n"
        # Now lets check for formatting
        for i in (0, 1):
            expected = (
                f"""#: source{i}\nmsgid ""\n"_: source{i}\\n"\n"Same"\nmsgstr ""\n"""
            )
            assert (str(pofile.units[i])) == expected

    @mark.xfail(reason="Were disabled during port of Pypo to cPO - they might work")
    def test_keep_blanks(self) -> None:
        """Checks that keeping keeps blanks and doesn't add msgid_comments."""
        posource = (
            '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
        )
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("keep")
        assert len(pofile.units) == 2
        # check we don't add msgidcomments
        assert cpo.unquotefrompo(pofile.units[0].msgidcomments) == ""
        assert cpo.unquotefrompo(pofile.units[1].msgidcomments) == ""

    def test_output_str_unicode(self) -> None:
        """Checks that we can serialize pofile, unit content is in unicode."""
        posource = """#: nb\nmsgid "Norwegian Bokmål"\nmsgstr ""\n"""
        pofile = self.StoreClass(BytesIO(posource.encode("UTF-8")), encoding="UTF-8")
        assert len(pofile.units) == 1
        print(bytes(pofile))
        thepo = pofile.units[0]
        #        assert bytes(pofile) == posource.encode("UTF-8")
        # extra test: what if we set the msgid to a unicode? this happens in prop2po etc
        thepo.source = "Norwegian Bokm\xe5l"
        #        assert str(thepo) == posource.encode("UTF-8")
        # Now if we set the msgstr to Unicode
        # this is an escaped half character (1/2)
        halfstr = b"\xbd ...".decode("latin-1")
        thepo.target = halfstr
        #        assert halfstr in bytes(pofile).decode("UTF-8")
        thepo.target = halfstr.encode("UTF-8")

    #        assert halfstr.encode("UTF-8") in bytes(pofile)

    def test_posections(self) -> None:
        """Checks the content of all the expected sections of a PO message."""
        posource = '# other comment\n#. automatic comment\n#: source comment\n#, fuzzy\nmsgid "One"\nmsgstr "Een"\n'
        pofile = self.poparse(posource)
        print(pofile)
        assert len(pofile.units) == 1
        assert bytes(pofile).decode("utf-8") == posource

    def test_multiline_obsolete(self) -> None:
        """Tests for correct output of multiline obsolete messages."""
        posource = '#~ msgid ""\n#~ "Old thing\\n"\n#~ "Second old thing"\n#~ msgstr ""\n#~ "Ou ding\\n"\n#~ "Tweede ou ding"\n'
        pofile = self.poparse(posource)
        print(f"Source:\n{posource}")
        print(f"Output:\n{bytes(pofile)}")
        assert len(pofile.units) == 1
        assert pofile.units[0].isobsolete()
        assert not pofile.units[0].istranslatable()
        assert bytes(pofile).decode("utf-8") == posource

    def test_unassociated_comments(self) -> None:
        """Tests behaviour of unassociated comments."""
        oldsource = '# old lonesome comment\n\nmsgid "one"\nmsgstr "een"\n'
        oldfile = self.poparse(oldsource)
        print("serialize", bytes(oldfile))
        assert len(oldfile.units) == 1
        assert "# old lonesome comment\nmsgid" in bytes(oldfile).decode("utf-8")

    @mark.xfail(reason="removal not working in cPO")
    def test_remove(self) -> None:
        super().test_remove()

    @mark.skip(reason="Native gettext emits warning here")
    def test_parse_corrupt_header(self) -> None:
        pass
