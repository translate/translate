#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.convert import oo2po
from translate.convert import po2oo
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import oo
import os

class TestOO2PO:
    def oo2po(self, oosource, sourcelanguage='en-US', targetlanguage='af-ZA'):
        """helper that converts oo source to po source without requiring files"""
        inputoo = oo.oofile(oosource)
        convertor = oo2po.oo2po(sourcelanguage, targetlanguage)
        outputpo = convertor.convertfile(inputoo)
        return outputpo

    def singleelement(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        return pofile.units[1]

    def roundtripstring(self, entitystring):
        """Convert the supplied string as part of an OpenOffice.org GSI file to po and back.
        
        Return the string once it has been through all the conversions."""

        oointro = r'helpcontent2	source\text\shared\01\02100001.xhp	0	help	par_id3150670 35				0	en-US	'
        oooutro = r'				2002-02-02 02:02:02' + '\r\n'

        oosource = oointro + entitystring + oooutro
        ooinputfile = wStringIO.StringIO(oosource)
        ootemplatefile = wStringIO.StringIO(oosource)
        pooutputfile = wStringIO.StringIO()

        oo2po.convertoo(ooinputfile, pooutputfile, ootemplatefile, targetlanguage='en-US')
        posource = pooutputfile.getvalue()

        poinputfile = wStringIO.StringIO(posource)
        ootemplatefile = wStringIO.StringIO(oosource)
        oooutputfile = wStringIO.StringIO()
        po2oo.convertoo(poinputfile, oooutputfile, ootemplatefile, targetlanguage="en-US")
        ooresult = oooutputfile.getvalue()
        print "original oo:\n", oosource, "po version:\n", posource, "output oo:\n", ooresult
        assert ooresult.startswith(oointro) and ooresult.endswith(oooutro)
        return ooresult[len(oointro):-len(oooutro)]

    def check_roundtrip(self, text):
        """Checks that the text converted to po and back is the same as the original."""
        assert self.roundtripstring(text) == text

    def test_simpleentity(self):
        """checks that a simple oo entry converts properly to a po entry"""
        oosource = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        pofile = self.oo2po(oosource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "Character"
        assert pounit.target == ""

    def test_escapes(self):
        """checks that a simple oo entry converts escapes properly to a po entry"""
        oosource = r"wizards	source\formwizard\dbwizres.src	0	string	RID_DB_FORM_WIZARD_START + 19				0	en-US	Newline \n Newline Tab \t Tab CR \r CR				20050924 09:13:58"
        pofile = self.oo2po(oosource)
        pounit = self.singleelement(pofile)
        poelementsrc = str(pounit)
        print poelementsrc
        assert "Newline \n Newline" in pounit.source 
        assert "Tab \t Tab" in pounit.source 
        assert "CR \r CR" in pounit.source 

    def test_roundtrip_escape(self):
        self.check_roundtrip(r'\\\\<')
        self.check_roundtrip(r'\\\<')
        self.check_roundtrip(r'\\<')
        self.check_roundtrip(r'\<')

    def test_double_escapes(self):
        oosource = r"helpcontent2	source\text\shared\01\02100001.xhp	0	help	par_id3150670 35				0	en-US	\\<				2002-02-02 02:02:02"
        pofile = self.oo2po(oosource)
        pounit = self.singleelement(pofile)
        poelementsrc = str(pounit)
        print poelementsrc
        assert pounit.source == r"\\<"

    def test_escapes_helpcontent2(self):
        """checks that a helpcontent2 entry converts escapes properly to a po entry"""
        oosource = r"helpcontent2	source\text\smath\guide\parentheses.xhp	0	help	par_id3150344	4			0	en-US	size *2 \\langle x \\rangle				2002-02-02 02:02:02"
        pofile = self.oo2po(oosource)
        pounit = self.singleelement(pofile)
        poelementsrc = str(pounit)
        print poelementsrc
        assert pounit.source == r'size *2 \\langle x \\rangle'

    def test_msgid_bug_error_address(self):
        """tests the we have the correct url for reporting msgid bugs"""
        oosource = r"wizards	source\formwizard\dbwizres.src	0	string	RID_DB_FORM_WIZARD_START + 19				0	en-US	Newline \n Newline Tab \t Tab CR \r CR				20050924 09:13:58"
        bug_url = '''http://qa.openoffice.org/issues/enter_bug.cgi''' + ('''?subcomponent=ui&comment=&short_desc=Localization issue in file: &component=l10n&form_name=enter_issue''').replace(" ", "%20").replace(":", "%3A")
        pofile = self.oo2po(oosource)
        assert pofile.units[0].isheader()
        assert pofile.parseheader()["Report-Msgid-Bugs-To"] == bug_url

    def test_x_comment_inclusion(self):
        """test that we can merge x-comment language entries into comment sections of the PO file"""
        en_USsource = r"wizards	source\formwizard\dbwizres.src	0	string	RID_DB_FORM_WIZARD_START + 19				0	en-US	Text		Quickhelp	Title	20050924 09:13:58"
        xcommentsource = r"wizards	source\formwizard\dbwizres.src	0	string	RID_DB_FORM_WIZARD_START + 19				0	x-comment	%s		%s	%s	20050924 09:13:58"
        # Real comment
        comment = "Comment"
        expected = comment + "\n"
        commentsource = en_USsource + '\n' + xcommentsource % (comment, comment, comment)
        pofile = self.oo2po(commentsource)
        textunit = pofile.units[1]
        assert textunit.source == "Text"
        assert '#. %s' % expected in textunit.automaticcomments
        quickhelpunit = pofile.units[2]
        assert quickhelpunit.source == "Quickhelp"
        assert '#. %s' % expected in quickhelpunit.automaticcomments
        titleunit = pofile.units[3]
        assert titleunit.source == "Title"
        assert '#. %s' % expected in titleunit.automaticcomments
        # Whitespace and blank
        for comment in ("   ", ""):
          commentsource = en_USsource + '\n' + xcommentsource % (comment, comment, comment)
          pofile = self.oo2po(commentsource)
          textunit = pofile.units[1]
          assert textunit.source == "Text"
          assert textunit.automaticcomments == []
          quickhelpunit = pofile.units[2]
          assert quickhelpunit.source == "Quickhelp"
          assert quickhelpunit.automaticcomments == []
          titleunit = pofile.units[3]
          assert titleunit.source == "Title"
          assert titleunit.automaticcomments == []

class TestOO2POCommand(test_convert.TestConvertCommand, TestOO2PO):
    """Tests running actual oo2po commands on files"""
    convertmodule = oo2po

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "--source-language=LANG")
        options = self.help_check(options, "--language=LANG")
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "--duplicates=DUPLICATESTYLE")
        options = self.help_check(options, "--multifile=MULTIFILESTYLE")
        options = self.help_check(options, "--nonrecursiveinput", last=True)

    def test_preserve_filename(self):
        """Ensures that the filename is preserved."""
        oosource = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        self.create_testfile("snippet.sdf", oosource)
        oofile = oo.oofile(self.open_testfile("snippet.sdf"))
        assert oofile.filename.endswith("snippet.sdf")
        oofile.parse(oosource)
        assert oofile.filename.endswith("snippet.sdf")

    def test_simple_pot(self):
        """tests the simplest possible conversion to a pot file"""
        oosource = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        self.create_testfile("simple.oo", oosource)
        self.run_command("simple.oo", "simple.pot", pot=True, nonrecursiveinput=True)
        pofile = po.pofile(self.open_testfile("simple.pot"))
        poelement = self.singleelement(pofile)
        assert poelement.source == "Character"
        assert poelement.target == ""

    def test_simple_po(self):
        """tests the simplest possible conversion to a po file"""
        oosource1 = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        oosource2 = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	ku	Karakter				20050924 09:13:58'
        self.create_testfile("simple.oo", oosource1 + "\n" + oosource2)
        self.run_command("simple.oo", "simple.po", lang="ku", nonrecursiveinput=True)
        pofile = po.pofile(self.open_testfile("simple.po"))
        poelement = self.singleelement(pofile)
        assert poelement.source == "Character"
        assert poelement.target == "Karakter"

    def test_onefile_nonrecursive(self):
        """tests the --multifile=onefile option and make sure it doesn't produce a directory"""
        oosource = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        self.create_testfile("simple.oo", oosource)
        self.run_command("simple.oo", "simple.pot", pot=True, multifile="onefile")
        assert os.path.isfile(self.get_testfilename("simple.pot"))

    def test_remove_duplicates(self):
        """test that removing of duplicates works correctly (bug 171)"""
        oosource = r'''
sd	source\ui\animations\SlideTransitionPane.src	0	checkbox	DLG_SLIDE_TRANSITION_PANE	CB_AUTO_PREVIEW	HID_SD_SLIDETRANSITIONPANE_CB_AUTO_PREVIEW		1	en-US	Automatic preview				20060725 03:26:42
sd	source\ui\animations\AnimationSchemesPane.src	0	checkbox	DLG_ANIMATION_SCHEMES_PANE	CB_AUTO_PREVIEW	HID_SD_ANIMATIONSCHEMESPANE_CB_AUTO_PREVIEW		1	en-US	Automatic preview				20060725 03:26:42
sd	source\ui\animations\CustomAnimationCreateDialog.src	0	checkbox	RID_TP_CUSTOMANIMATION_ENTRANCE	CBX_PREVIEW			143	en-US	Automatic preview				20060725 03:26:42
sd	source\ui\animations\CustomAnimationCreateDialog.src	0	checkbox	RID_TP_CUSTOMANIMATION_ENTRANCE	CBX_PREVIEW			143	fr	Aperçu automatique				20060725 03:26:42
sd	source\ui\animations\CustomAnimationSchemesPane.src	0	checkbox	DLG_CUSTOMANIMATION_SCHEMES_PANE	4			0	en-US	Automatic preview				20060725 03:26:42
sd	source\ui\animations\CustomAnimationSchemesPane.src	0	checkbox	DLG_CUSTOMANIMATION_SCHEMES_PANE	4			0	fr	Aperçu automatique				20060725 03:26:42
'''
        self.create_testfile("simple.oo", oosource)
        self.run_command("simple.oo", "simple.po", language="fr", multifile="onefile", error="traceback")
        pofile = po.pofile(self.open_testfile("simple.po"))
        assert len(pofile.units) == 2
        assert pofile.units[1].target == u"Aperçu automatique"

