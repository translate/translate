#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import po
from translate.storage import test_base
from translate.misc.multistring import multistring
from translate.misc import wStringIO

def test_roundtrip_quoting():
    specials = ['Fish & chips', 'five < six', 'six > five', 
                'Use &nbsp;', 'Use &amp;nbsp;' 
                'A "solution"', "skop 'n bal", '"""', "'''", 
                '\n', '\t', '\r', 
                '\\n', '\\t', '\\r', '\\"', '\r\n', '\\r\\n', '\\']
    for special in specials:
        quoted_special = po.quoteforpo(special)
        unquoted_special = po.unquotefrompo(quoted_special)
        print "special: %r\nquoted: %r\nunquoted: %r\n" % (special, quoted_special, unquoted_special)
        assert special == unquoted_special

class TestPOUnit(test_base.TestTranslationUnit):
    UnitClass = po.pounit

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

        unit.target = {0:"Koei", 3:"Koeie"}
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Koei", "Koeie"]
        assert unit.target == "Koei"

        unit.target = [u"Sk\u00ear", u"Sk\u00eare"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == [u"Sk\u00ear", u"Sk\u00eare"]
        assert unit.target.strings == [u"Sk\u00ear", u"Sk\u00eare"]
        assert unit.target == u"Sk\u00ear"

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
        assert unit.target.strings == ["Boom", "Bome"]
        unit.target = "Een Boom"
        assert unit.target.strings == ["Een Boom"]

    def test_notes(self):
        """tests that the generic notes API works"""
        unit = self.UnitClass("File")
        unit.addnote("Which meaning of file?")
        assert str(unit) == '# Which meaning of file?\nmsgid "File"\nmsgstr ""\n'
        unit.addnote("Verb", origin="programmer")
        assert str(unit) == '# Which meaning of file?\n#. Verb\nmsgid "File"\nmsgstr ""\n'
        unit.addnote("Thank you", origin="translator")
        assert str(unit) == '# Which meaning of file?\n# Thank you\n#. Verb\nmsgid "File"\nmsgstr ""\n'

        assert unit.getnotes() == "Which meaning of file?\nThank you\nVerb"

    def test_notes_withcomments(self):
        """tests that when we add notes that look like comments that we treat them properly"""
        unit = self.UnitClass("File")
        unit.addnote("# Double commented comment")
        assert str(unit) == '# # Double commented comment\nmsgid "File"\nmsgstr ""\n'
        assert unit.getnotes() == "# Double commented comment"
        
class TestPO(test_base.TestTranslationStore):
    StoreClass = po.pofile
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        pofile = po.pofile(dummyfile)
        return pofile

    def poregen(self, posource):
        """helper that converts po source to pofile object and back"""
        return str(self.poparse(posource))

    def pomerge(self, oldmessage, newmessage):
        """helper that merges two messages"""
        dummyfile = wStringIO.StringIO(oldmessage)
        oldpofile = po.pofile(dummyfile)
        oldunit = oldpofile.units[0]
        dummyfile2 = wStringIO.StringIO(newmessage)
        if newmessage:
          newpofile = po.pofile(dummyfile2)
          newunit = newpofile.units[0]
        else:
          newunit = po.pounit()
        oldunit.merge(newunit)
        print oldunit
        return str(oldunit)

    def test_simpleentry(self):
        """checks that a simple po entry is parsed correctly"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 1
        thepo = pofile.units[0]
        assert thepo.getlocations() == ["test.c"]
        assert thepo.source == "test"
        assert thepo.target == "rest"

    def test_combine_msgidcomments(self):
        """checks that we don't get duplicate msgid comments"""
        posource = 'msgid "test me"\nmsgstr ""'
        pofile = self.poparse(posource)
        thepo = pofile.units[0]
        thepo.msgidcomments.append('"_: first comment\\n"')
        thepo.msgidcomments.append('"_: second comment\\n"')
        regenposource = str(pofile)
        assert regenposource.count("_:") == 1

    def test_merge_duplicates(self):
        """checks that merging duplicates works"""
        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("merge")
        assert len(pofile.units) == 1
        assert pofile.units[0].getlocations() == ["source1", "source2"]

    def test_merge_mixed_sources(self):
        """checks that merging works with different source location styles"""
        posource = '''
#: source1
#: source2
msgid "test"
msgstr ""

#: source1 source2
msgid "test"
msgstr ""
'''
        pofile = self.poparse(posource)
        print str(pofile)
        assert len(pofile.units) == 2
        pofile.removeduplicates("merge")
        print str(pofile)
        assert len(pofile.units) == 1
        assert pofile.units[0].getlocations() == ["source1", "source2"]

    def test_merge_blanks(self):
        """checks that merging adds msgid_comments to blanks"""
        posource = '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("merge")
        assert len(pofile.units) == 2
        print pofile.units[0].msgidcomments
        print pofile.units[1].msgidcomments
        assert po.unquotefrompo(pofile.units[0].msgidcomments) == "_: source1\n"
        assert po.unquotefrompo(pofile.units[1].msgidcomments) == "_: source2\n"

    def test_msgid_comment(self):
        """checks that when adding msgid_comments we place them on a newline"""
        posource = '#: source0\nmsgid "Same"\nmsgstr ""\n\n#: source1\nmsgid "Same"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("msgid_comment")
        assert len(pofile.units) == 2
        assert po.unquotefrompo(pofile.units[0].msgidcomments) == "_: source0\n"
        assert po.unquotefrompo(pofile.units[1].msgidcomments) == "_: source1\n"
        # Now lets check for formating
        for i in (0, 1):
          expected = '''#: source%d\nmsgid ""\n"_: source%d\\n"\n"Same"\nmsgstr ""\n''' % (i, i)
          assert pofile.units[i].__str__() == expected

    def test_keep_blanks(self):
        """checks that keeping keeps blanks and doesn't add msgid_comments"""
        posource = '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("keep")
        assert len(pofile.units) == 2
        # check we don't add msgidcomments
        assert po.unquotefrompo(pofile.units[0].msgidcomments) == ""
        assert po.unquotefrompo(pofile.units[1].msgidcomments) == ""

    def test_parse_source_string(self):
        """parse a string"""
        posource = '#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        pofile = po.pofile(posource)
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
        print pofile
        assert len(pofile.units) == 2

    def test_output_str_unicode(self):
        """checks that we can str(element) which is in unicode"""
        posource = u'''#: nb\nmsgid "Norwegian Bokm\xe5l"\nmsgstr ""\n'''
        pofile = po.pofile(wStringIO.StringIO(posource.encode("UTF-8")), encoding="UTF-8")
        assert len(pofile.units) == 1
        print str(pofile)
        thepo = pofile.units[0]
        assert str(thepo) == posource.encode("UTF-8")
        # extra test: what if we set the msgid to a unicode? this happens in prop2po etc
        thepo.source = u"Norwegian Bokm\xe5l"
        assert str(thepo) == posource.encode("UTF-8")
        # Now if we set the msgstr to Unicode
        # this is an escaped half character (1/2)
        halfstr = "\xbd ...".decode("latin-1")
        thepo.target = halfstr
        assert halfstr in str(thepo).decode("UTF-8")
        thepo.target = halfstr.encode("UTF-8")
        assert halfstr.encode("UTF-8") in thepo.getoutput()

    def test_plurals(self):
        posource = r'''msgid "Cow"
msgid_plural "Cows"
msgstr[0] "Koei"
msgstr[1] "Koeie"
'''
        pofile = po.pofile(wStringIO.StringIO(posource))
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert isinstance(unit.target, multistring)
        print unit.target.strings
        assert unit.target == "Koei"
        assert unit.target.strings == ["Koei", "Koeie"]

        posource = r'''msgid "Skaap"
msgid_plural "Skape"
msgstr[0] "Sheep"
'''
        pofile = po.pofile(wStringIO.StringIO(posource))
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert isinstance(unit.target, multistring)
        print unit.target.strings
        assert unit.target == "Sheep"
        assert unit.target.strings == ["Sheep"]

    def test_posections(self):
        """checks the content of all the expected sections of a PO message"""
        posource = '# other comment\n#. automatic comment\n#: source comment\n#, fuzzy\nmsgid "One"\nmsgstr "Een"\n'
        pofile = self.poparse(posource)
        print pofile
        assert len(pofile.units) == 1
        assert str(pofile) == posource
        assert pofile.units[0].othercomments == ["# other comment\n"]
        assert pofile.units[0].automaticcomments == ["#. automatic comment\n"]
        assert pofile.units[0].sourcecomments == ["#: source comment\n"]
        assert pofile.units[0].typecomments == ["#, fuzzy\n"]

    def test_obsolete(self):
        """Tests that obsolete messages work"""
        posource = '#~ msgid "Old thing"\n#~ msgstr "Ou ding"\n'
        pofile = self.poparse(posource)
        assert pofile.isempty()
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert unit.isobsolete()
        assert str(pofile) == posource

    def test_makeobsolete(self):
        """Tests making a unit obsolete"""
        posource = '#. The automatic one\n#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poexpected = '#~ msgid "test"\n#~ msgstr "rest"\n'
        pofile = self.poparse(posource)
        print pofile
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print pofile
        assert str(unit) == poexpected
        
        posource = r'''msgid "Cow"
msgid_plural "Cows"
msgstr[0] "Koei"
msgstr[1] "Koeie"
'''
        poexpected = '''#~ msgid "Cow"
#~ msgid_plural "Cows"
#~ msgstr[0] "Koei"
#~ msgstr[1] "Koeie"
'''
        pofile = self.poparse(posource)
        print pofile
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print pofile
        assert str(unit) == poexpected

    def test_makeobsolete_msgidcomments(self):
        """Tests making a unit with msgidcomments obsolete"""
        posource = '#: first.c\nmsgid ""\n"_: first.c\\n"\n"test"\nmsgstr "rest"\n\n#: second.c\nmsgid ""\n"_: second.c\\n"\n"test"\nmsgstr "rest"'
        poexpected = '#~ msgid ""\n#~ "_: first.c\\n"\n#~ "test"\n#~ msgstr "rest"\n'
        print "Source:\n%s" % posource
        print "Expected:\n%s" % poexpected
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print "Result:\n%s" % pofile
        assert str(unit) == poexpected

    def test_multiline_obsolete(self):
        """Tests for correct output of mulitline obsolete messages"""
        posource = '#~ msgid "Old thing\\n"\n#~ "Second old thing"\n#~ msgstr "Ou ding\\n"\n#~ "Tweede ou ding"\n'
        pofile = self.poparse(posource)
        assert pofile.isempty()
        assert len(pofile.units) == 1
        unit = pofile.units[0]
        assert unit.isobsolete()
        print str(pofile)
        print posource
        assert str(pofile) == posource

    def test_merging_automaticcomments(self):
        """checks that new automatic comments override old ones"""
        oldsource = '#. old comment\n#: line:10\nmsgid "One"\nmsgstr "Een"\n'
        newsource = '#. new comment\n#: line:10\nmsgid "One"\nmsgstr ""\n'
        expected = '#. new comment\n#: line:10\nmsgid "One"\nmsgstr "Een"\n'
        assert self.pomerge(newsource, oldsource) == expected

    def test_unassociated_comments(self):
        """tests behaviour of unassociated comments."""
        oldsource = '# old lonesome comment\n\nmsgid "one"\nmsgstr "een"\n'
        oldfile = self.poparse(oldsource)
        print "__str__", str(oldfile)
        assert len(oldfile.units) == 2
        assert str(oldfile).find("# old lonesome comment\n\n") >= 0

    def test_header_blank(self):
        """test header functionality"""
        posource = r'''# other comment\n
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-03-08 17:30+0200\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;\n"
'''
        pofile = self.poparse(posource)
        print pofile
        assert len(pofile.units) == 1
        header = pofile.units[0]
        assert header.isheader()
        assert not header.isblank()

        headeritems = pofile.parseheader()
        assert headeritems["Project-Id-Version"] == "PACKAGE VERSION"
        assert headeritems["Report-Msgid-Bugs-To"] == ""
        #assert headeritems["POT-Creation-Date"] == ""
        assert headeritems["PO-Revision-Date"] == "YEAR-MO-DA HO:MI+ZONE"
        assert headeritems["Last-Translator"] == "FULL NAME <EMAIL@ADDRESS>"
        assert headeritems["Language-Team"] == "LANGUAGE <LL@li.org>"
        assert headeritems["MIME-Version"] == "1.0"
        assert headeritems["Content-Type"] == "text/plain; charset=UTF-8"
        assert headeritems["Content-Transfer-Encoding"] == "8bit"
        assert headeritems["Plural-Forms"] == "nplurals=INTEGER; plural=EXPRESSION;"
        
    def test_plural_equation(self):
        """test that we work with the equation even is the last semicolon is left out, since gettext
        tools don't seem to mind"""
        posource = r'''msgid ""
msgstr ""
"Plural-Forms: nplurals=2; plural=(n != 1)%s\n"
'''
        for colon in ("", ";"):
          pofile = self.poparse(posource % colon)
          print pofile
          assert len(pofile.units) == 1
          header = pofile.units[0]
          assert header.isheader()
          assert not header.isblank()

          headeritems = pofile.parseheader()
          nplural, plural = pofile.getheaderplural()
          assert nplural == "2"
          assert plural == "(n != 1)"

    def test_plural_equation_across_lines(self):
        """test that we work if the plural equation spans more than one line"""
        posource = r'''msgid ""
msgstr ""
"Plural-Forms:  nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%"
"10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);\n"
'''
        pofile = self.poparse(posource)
        print pofile
        assert len(pofile.units) == 1
        header = pofile.units[0]
        assert header.isheader()
        assert not header.isblank()

        headeritems = pofile.parseheader()
        nplural, plural = pofile.getheaderplural()
        assert nplural == "3"
        assert plural == "(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)"

