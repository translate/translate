import os
from io import BytesIO

from pytest import mark

from translate.convert import oo2po, po2oo, test_convert
from translate.storage import po


class TestPO2OO:
    @staticmethod
    def convertoo(posource, ootemplate, language="en-US"):
        """helper to exercise the command line function"""
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        templatefile = BytesIO(ootemplate.encode())
        assert po2oo.convertoo(
            inputfile, outputfile, templatefile, targetlanguage=language, timestamp=0
        )
        return outputfile.getvalue()

    @staticmethod
    def roundtripstring(entitystring):
        oointro, oooutro = (
            r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	",
            "				2002-02-02 02:02:02" + "\r\n",
        )
        oosource = oointro + entitystring + oooutro
        ooinputfile = BytesIO(oosource.encode())
        ooinputfile2 = BytesIO(oosource.encode())
        pooutputfile = BytesIO()
        oo2po.convertoo(ooinputfile, pooutputfile, ooinputfile2, targetlanguage="en-US")
        posource = pooutputfile.getvalue()
        poinputfile = BytesIO(posource)
        ootemplatefile = BytesIO(oosource.encode())
        oooutputfile = BytesIO()
        po2oo.convertoo(
            poinputfile, oooutputfile, ootemplatefile, targetlanguage="en-US"
        )
        ooresult = oooutputfile.getvalue().decode("utf-8")
        print(
            "original oo:\n",
            oosource,
            "po version:\n",
            posource,
            "output oo:\n",
            ooresult,
        )
        assert ooresult.startswith(oointro) and ooresult.endswith(oooutro)
        return ooresult[len(oointro) : -len(oooutro)]

    def check_roundtrip(self, oosource):
        """Checks that the round-tripped string is the same as the original"""
        assert self.roundtripstring(oosource) == oosource

    @mark.skipif(os.name == "nt", reason="test or storage broken on Windows")
    def test_convertoo(self):
        """checks that the convertoo function is working"""
        oobase = (
            r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	%s	%s				20050924 09:13:58"
            + "\r\n"
        )
        posource = """#: numpages.src#RID_SVXPAGE_NUM_OPTIONS.STR_BULLET.string.text\nmsgid "Simple String"\nmsgstr "Dimpled Ring"\n"""
        ootemplate = oobase % ("en-US", "Simple String")
        ooexpected = oobase % ("zu", "Dimpled Ring")
        newoo = self.convertoo(posource, ootemplate, language="zu")
        assert newoo.decode("utf-8") == ootemplate + ooexpected

    @staticmethod
    def test_pofilter():
        """Tests integration with pofilter"""
        # Some bad po with a few errors:
        posource = b'#: sourcefile.bla#ID_NUMBER.txet.gnirts\nmsgid "<tag cow=\\"3\\">Mistake."\nmsgstr "  <etiket koei=\\"3\\">(fout) "'
        filter = po2oo.filter
        pofile = po.pofile()
        pofile.parse(posource)
        assert not filter.validelement(pofile.units[0], "dummyname.po", "exclude-all")

    def test_roundtrip_simple(self):
        """checks that simple strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip("Hello")
        self.check_roundtrip('"Hello"')
        self.check_roundtrip('"Hello Everybody"')

    def test_roundtrip_escape(self):
        """checks that escapes in strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip(r'"Simple Escape \ \n \\ \: \t \r "')
        self.check_roundtrip(r'"More escapes \\n \\t \\r \\: "')
        self.check_roundtrip(r'"More escapes \\\n \\\t \\\r \\\: "')
        self.check_roundtrip(r'"More escapes \\\\n \\\\t \\\\r \\\\: "')
        self.check_roundtrip(r'"End Line Escape \"')
        self.check_roundtrip(r'"\\rangle \\langle')
        self.check_roundtrip(r"\\\\<")
        self.check_roundtrip(r"\\\<")
        self.check_roundtrip(r"\\<")
        self.check_roundtrip(r"\<")

    def test_roundtrip_quotes(self):
        """checks that (escaped) quotes in strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip(r"""'Quote Escape "" '""")
        self.check_roundtrip(r'''"Single-Quote ' "''')
        self.check_roundtrip(r'''"Single-Quote Escape \' "''')
        self.check_roundtrip(r"""'Both Quotes "" '' '""")

    def test_roundtrip_spaces(self):
        # FIXME: this test fails because the resultant PO file returns as po.isempty since .isblank returns true
        # which is caused by isblankmsgtr returning True.  Its a complete mess which would mean unravelling lots
        # of yuch in pypo.  Until we have time to do that unravelling we're diabling this test.  You can reenable
        # once we've fixed that.
        """checks that (escaped) quotes in strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip(" ")
        self.check_roundtrip("\u00a0")

    @staticmethod
    def test_default_timestamp():
        """test to ensure that we revert to the default timestamp"""
        oointro, oooutro = (
            r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Text				",
            "\r\n",
        )
        posource = """#: numpages.src#RID_SVXPAGE_NUM_OPTIONS.STR_BULLET.string.text\nmsgid "Text"\nmsgstr "Text"\n"""
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        templatefile = BytesIO((oointro + "20050924 09:13:58" + oooutro).encode())
        assert po2oo.convertoo(
            inputfile, outputfile, templatefile, targetlanguage="en-US"
        )
        assert (
            outputfile.getvalue().decode("utf-8")
            == oointro + "2002-02-02 02:02:02" + oooutro
        )

    @staticmethod
    def test_escape_conversion():
        """test to ensure that we convert escapes correctly"""
        oosource = (
            r"svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Column1\tColumn2\r\n				2002-02-02 02:02:02"
            + "\r\n"
        )
        posource = """#: numpages.src#RID_SVXPAGE_NUM_OPTIONS.STR_BULLET.string.text\nmsgid "Column1\\tColumn2\\r\\n"\nmsgstr "Kolom1\\tKolom2\\r\\n"\n"""
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        templatefile = BytesIO(oosource.encode())
        assert po2oo.convertoo(
            inputfile, outputfile, templatefile, targetlanguage="af-ZA"
        )
        assert b"\tKolom1\\tKolom2\\r\\n\t" in outputfile.getvalue()

    @staticmethod
    def test_helpcontent_escapes():
        """test to ensure that we convert helpcontent escapes correctly"""
        # Note how this test specifically uses incorrect spacing in the
        # translation. The extra space before 'hid' and an extra space before
        # the closing tag should not confuse us.
        oosource = (
            r"helpcontent2	source\text\shared\3dsettings_toolbar.xhp	0	help	par_idN1056A				0	en-US	\<ahelp hid=\".\"\>The 3D-Settings toolbar controls properties of selected 3D objects.\</ahelp\>				2002-02-02 02:02:02"
            + "\r\n"
        )
        posource = r"""#: 3dsettings_toolbar.xhp#par_idN1056A.help.text
msgid ""
"<ahelp hid=\".\">The 3D-Settings toolbar controls properties of selected 3D "
"ob jects.</ahelp>"
msgstr ""
"<ahelp  hid=\".\" >Zeee 3DDDD-Settings toolbar controls properties of selected 3D "
"objects.</ahelp>"
"""
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        templatefile = BytesIO(oosource.encode())
        assert po2oo.convertoo(
            inputfile, outputfile, templatefile, targetlanguage="af-ZA"
        )
        assert (
            rb"\<ahelp  hid=\".\" \>Zeee 3DDDD-Settings toolbar controls properties of selected 3D objects.\</ahelp\>"
            in outputfile.getvalue()
        )

    @staticmethod
    def test_helpcontent_escapes2():
        """test to ensure that we convert helpcontent escapes correctly"""
        oosource = (
            r"helpcontent2	source\text\scalc\05\empty_cells.xhp	0	help	par_id2629474				0	en-US	A1: <empty>				2002-02-02 02:02:02"
            + "\r\n"
        )
        posource = r"""#: empty_cells.xhp#par_id2629474.help.text
msgid "A1: <empty>"
msgstr "Aa1: <empty>"
"""
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        templatefile = BytesIO(oosource.encode())
        assert po2oo.convertoo(
            inputfile, outputfile, templatefile, targetlanguage="af-ZA"
        )
        assert b"Aa1: <empty>" in outputfile.getvalue()


class TestPO2OOCommand(test_convert.TestConvertCommand, TestPO2OO):
    """Tests running actual po2oo commands on files"""

    convertmodule = po2oo
    expected_options = [
        "--source-language=LANG",
        "-l LANG, --language=LANG",
        "-T, --keeptimestamp",
        "--nonrecursiveoutput",
        "--nonrecursivetemplate",
        "--filteraction",
        "--skipsource",
        "--threshold=PERCENT",
        "--fuzzy",
        "--nofuzzy",
        "-t TEMPLATE, --template=TEMPLATE",
        "--multifile=MULTIFILESTYLE",
    ]

    def convertoo(self, posource, ootemplate, language="en-US"):
        """helper to exercise the command line function"""
        self.create_testfile(
            os.path.join("input", "svx", "source", "dialog.po"), posource
        )
        self.create_testfile("input.oo", ootemplate)
        self.run_command(
            "input",
            "output.oo",
            template="input.oo",
            language=language,
            keeptimestamp=True,
        )
        return self.read_testfile("output.oo")
