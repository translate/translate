#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import po
from translate.storage import test_base
from translate.misc.multistring import multistring
from translate.misc import wStringIO
from py.test import raises

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

        assert unit.getnotes("developer") == "Verb"
        assert unit.getnotes("translator") == "Which meaning of file?\nThank you"
        assert unit.getnotes() == "Which meaning of file?\nThank you\nVerb"
        assert raises(ValueError, unit.getnotes, "devteam")

    def test_notes_withcomments(self):
        """tests that when we add notes that look like comments that we treat them properly"""
        unit = self.UnitClass("File")
        unit.addnote("# Double commented comment")
        assert str(unit) == '# # Double commented comment\nmsgid "File"\nmsgstr ""\n'
        assert unit.getnotes() == "# Double commented comment"

    def test_adding_empty_note(self):
        unit = self.UnitClass("bla")
        assert not '#' in str(unit)
        unit.addnote("")
        assert not '#' in str(unit)
        
    def test_no_plural_settarget(self):
	"""tests that target handling of file with no plural is correct"""
	# plain text, no plural test
	unit = self.UnitClass("Tree")
	unit.target = "ki"
	assert unit.target.strings == ["ki"]
	assert unit.source.strings == ["Tree"]
	assert unit.hasplural() == False

	# plural test with multistring
	unit.setsource(["Tree", "Trees"])
	assert unit.source.strings == ["Tree", "Trees"]
	assert unit.hasplural()
	unit.target = multistring(["ki", "ni ki"])
	assert unit.target.strings == ["ki", "ni ki"]

	# test of msgid with no plural and msgstr with plural
	unit = self.UnitClass("Tree")
	assert raises(ValueError, unit.settarget, [u"ki", u"ni ki"])
	assert unit.hasplural() == False

    def test_wrap_firstlines(self):
        '''tests that we wrap the first line correctly a first line if longer then 71 chars
        as at 71 chars we should align the text on the left and preceed with with a msgid ""'''
        # longest before we wrap text
        str_max = "123456789 123456789 123456789 123456789 123456789 123456789 123456789 1"
        unit = self.UnitClass(str_max)
        expected = 'msgid "%s"\nmsgstr ""\n' % str_max
        print expected, str(unit)
        assert str(unit) == expected
        # at this length we wrap
        str_wrap = str_max + '2'
        unit = self.UnitClass(str_wrap)
        expected = 'msgid ""\n"%s"\nmsgstr ""\n' % str_wrap
        print expected, str(unit)
        assert str(unit) == expected

    def test_wrap_on_newlines(self):
        """test that we wrap newlines on a real \n"""
        string = "123456789\n" * 3
        postring = ('"123456789\\n"\n' * 3)[:-1]
        unit = self.UnitClass(string)
        expected = 'msgid ""\n%s\nmsgstr ""\n' % postring
        print expected, str(unit)
        assert str(unit) == expected

        # Now check for long newlines segments
        longstring = ("123456789 " * 10 + "\n") * 3
        expected = r'''msgid ""
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 "
"123456789 123456789 123456789 \n"
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 "
"123456789 123456789 123456789 \n"
"123456789 123456789 123456789 123456789 123456789 123456789 123456789 "
"123456789 123456789 123456789 \n"
msgstr ""
'''
        unit = self.UnitClass(longstring)
        print expected, str(unit)
        assert str(unit) == expected

    def test_wrap_on_max_line_length(self):
        """test that we wrap all lines on the maximum line length"""
        string = "1 3 5 7 N " * 11
        expected = 'msgid ""\n%s\nmsgstr ""\n' % '"1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 "\n"7 N 1 3 5 7 N 1 3 5 7 N 1 3 5 7 N "'
        unit = self.UnitClass(string)
        print expected, str(unit)
        assert str(unit) == expected

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

    def pomerge(self, oldmessage, newmessage, authoritative):
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
        oldunit.merge(newunit, authoritative=authoritative)
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

    def test_merge_duplicates_msgctxt(self):
        """checks that merging duplicates works for msgctxt"""
        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        assert len(pofile.units) == 2
        pofile.removeduplicates("msgctxt")
        print pofile
        assert len(pofile.units) == 2
        assert str(pofile.units[0]).count("source1") == 2
        assert str(pofile.units[1]).count("source2") == 2
  
    def test_parse_context(self):
        """Tests that msgctxt is parsed correctly and that it is accessible via the api methods."""
        posource = '''# Test comment
#: source1
msgctxt "noun"
msgid "convert"
msgstr "bekeerling"

# Test comment 2
#: source2
msgctxt "verb"
msgid "convert"
msgstr "omskakel"
'''
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == 'noun'
        assert unit.getnotes() == 'Test comment'

        unit = pofile.units[1]
        assert unit.getcontext() == 'verb'
        assert unit.getnotes() == 'Test comment 2'


    def test_parse_advanced_context(self):
        """Tests that some weird possible msgctxt scenarios are parsed correctly."""
        posource = r'''# Test multiline context
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
'''
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == 'Noun. A person that changes his or her ways.'
        assert unit.getnotes() == 'Test multiline context'

        unit = pofile.units[1]
        assert unit.getcontext() == 'Verb. Converting from "something" to "something else".'
        assert unit.getnotes() == 'Test quotes'
        
        unit = pofile.units[2]
        assert unit.getcontext() == 'Verb.\nConverting from "something" to "something else".'
        assert unit.getnotes() == 'Test quotes, newlines and multiline.'
 
    def test_kde_context(self):
        """Tests that kde-style msgid comments can be retrieved via getcontext()."""
        posource = '''# Test comment
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
'''
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == 'Noun'
        assert unit.getnotes() == 'Test comment'

        unit = pofile.units[1]
        assert unit.getcontext() == 'Verb. _: The action of changing.'
        assert unit.getnotes() == 'Test comment 2'

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

    def test_empty_lines_notes(self):
        """Tests that empty comment lines are preserved"""
        posource = r'''# License name
#
# license line 1
# license line 2
# license line 3
msgid ""
msgstr "POT-Creation-Date: 2006-03-08 17:30+0200\n"
'''
        pofile = self.poparse(posource)
        assert str(pofile) == posource

    def test_fuzzy(self):
        """checks that fuzzy functionality works as expected"""
        posource = '#, fuzzy\nmsgid "ball"\nmsgstr "bal"\n'
        expectednonfuzzy = 'msgid "ball"\nmsgstr "bal"\n'
        pofile = self.poparse(posource)
        print pofile
        assert pofile.units[0].isfuzzy()
        pofile.units[0].markfuzzy(False)
        assert not pofile.units[0].isfuzzy()
        assert str(pofile) == expectednonfuzzy

        posource = '#, fuzzy, python-format\nmsgid "ball"\nmsgstr "bal"\n'
        expectednonfuzzy = '#, python-format\nmsgid "ball"\nmsgstr "bal"\n'
        pofile = self.poparse(posource)
        print pofile
        assert pofile.units[0].isfuzzy()
        pofile.units[0].markfuzzy(False)
        assert not pofile.units[0].isfuzzy()
        assert str(pofile) == expectednonfuzzy

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
        
    def test_makeobsolete_plural(self):
        """Tests making a plural unit obsolete"""
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

    def test_makeobsolete_msgctxt(self):
        """Tests making a unit with msgctxt obsolete"""
        posource = '#: test.c\nmsgctxt "Context"\nmsgid "test"\nmsgstr "rest"\n'
        poexpected = '#~ msgctxt "Context"\n#~ msgid "test"\n#~ msgstr "rest"\n'
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

    def xtest_makeobsolete_untranslated(self):
        """Tests making an untranslated unit obsolete"""
        posource = '#. The automatic one\n#: test.c\nmsgid "test"\nmsgstr ""\n'
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert str(unit) == ""
        # a better way might be for pomerge/pot2po to remove the unit

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
        assert self.pomerge(newsource, oldsource, authoritative=True) == expected

    def test_unassociated_comments(self):
        """tests behaviour of unassociated comments."""
        oldsource = '# old lonesome comment\n\nmsgid "one"\nmsgstr "een"\n'
        oldfile = self.poparse(oldsource)
        print "__str__", str(oldfile)
        assert len(oldfile.units) == 2
        assert str(oldfile).find("# old lonesome comment\n\n") >= 0
