from io import BytesIO

from translate.convert import php2po, test_convert
from translate.storage import po


class TestPhp2PO:
    @staticmethod
    def php2po(phpsource, phptemplate=None):
        """helper that converts .php source to po source without requiring files"""
        inputfile = BytesIO(phpsource.encode())
        output_file = BytesIO()
        templatefile = None
        if phptemplate:
            templatefile = BytesIO(phptemplate.encode())
        convertor = php2po.php2po(inputfile, output_file, templatefile)
        convertor.run()
        return convertor.target_store

    @staticmethod
    def convertphp(phpsource, template=None, expected=1):
        """call run_converter, return the outputfile"""
        inputfile = BytesIO(phpsource.encode())
        outputfile = BytesIO()
        templatefile = None
        if template:
            templatefile = BytesIO(template.encode())
        assert php2po.run_converter(inputfile, outputfile, templatefile) == expected
        return outputfile.getvalue()

    @staticmethod
    def singleelement(pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        print(pofile)
        return pofile.units[1]

    @staticmethod
    def countelements(pofile):
        """counts the number of non-header entries"""
        assert pofile.units[0].isheader()
        print(pofile)
        return len(pofile.units) - 1

    def test_simpleentry(self):
        """checks that a simple php entry converts properly to a po entry"""
        phpsource = """$_LANG['simple'] = 'entry';"""
        pofile = self.php2po(phpsource)
        pounit = self.singleelement(pofile)
        assert pounit.source == "entry"
        assert pounit.target == ""

    def test_convertphp(self):
        """checks that the convertphp function is working"""
        phpsource = """$_LANG['simple'] = 'entry';"""
        posource = self.convertphp(phpsource)
        pofile = po.pofile(BytesIO(posource))
        pounit = self.singleelement(pofile)
        assert pounit.source == "entry"
        assert pounit.target == ""

    def test_convertphptemplate(self):
        """checks that the convertphp function is working with template"""
        phpsource = """$_LANG['simple'] = 'entry';"""
        phptemplate = """$_LANG['simple'] = 'source';"""
        posource = self.convertphp(phpsource, phptemplate)
        pofile = po.pofile(BytesIO(posource))
        pounit = self.singleelement(pofile)
        assert pounit.source == "source"
        assert pounit.target == "entry"

    def test_convertphpmissing(self):
        """checks that the convertphp function is working with missing key"""
        phpsource = """$_LANG['simple'] = 'entry';"""
        phptemplate = """$_LANG['missing'] = 'source';"""
        posource = self.convertphp(phpsource, phptemplate)
        pofile = po.pofile(BytesIO(posource))
        pounit = self.singleelement(pofile)
        assert pounit.source == "source"
        assert pounit.target == ""

    def test_convertphpempty(self):
        """checks that the convertphp function is working with empty template"""
        phpsource = ""
        phptemplate = ""
        posource = self.convertphp(phpsource, phptemplate, 0)
        pofile = po.pofile(BytesIO(posource))
        assert len(pofile.units) == 0

    def test_unicode(self):
        """checks that unicode entries convert properly"""
        unistring = "Norsk bokm\u00E5l"
        phpsource = """$lang['nb'] = '%s';""" % unistring
        pofile = self.php2po(phpsource)
        pounit = self.singleelement(pofile)
        print(repr(pofile.units[0].target))
        print(repr(pounit.source))
        assert pounit.source == "Norsk bokm\u00E5l"

    def test_multiline(self):
        """checks that multiline enties can be parsed"""
        phpsource = r"""$lang['5093'] = 'Unable to connect to your IMAP server. You may have exceeded the maximum number
of connections to this server. If so, use the Advanced IMAP Server Settings dialog to
reduce the number of cached connections.';"""
        pofile = self.php2po(phpsource)
        print(repr(pofile.units[1].target))
        assert self.countelements(pofile) == 1

    def test_comments_before(self):
        """test to ensure that we take comments from .php and place them in .po"""
        phpsource = """/* Comment */
$lang['prefPanel-smime'] = 'Security';"""
        pofile = self.php2po(phpsource)
        pounit = self.singleelement(pofile)
        assert pounit.getnotes("developer") == "/* Comment */"
        # TODO write test for inline comments and check for // comments that precede an entry

    def test_emptyentry(self):
        """checks that empty definitions survives into po file"""
        phpsource = """/* comment */\n$lang['credit'] = '';"""
        pofile = self.php2po(phpsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["$lang['credit']"]
        assert pounit.getcontext() == "$lang['credit']"
        assert b"#. /* comment" in bytes(pofile)
        assert pounit.source == ""

    def test_hash_comment_with_equals(self):
        """Check that a # comment with = in it doesn't confuse us. Bug 1298."""
        phpsource = """# inside alt= stuffies\n$variable = 'stringy';"""
        pofile = self.php2po(phpsource)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["$variable"]
        assert b"#. # inside alt= stuffies" in bytes(pofile)
        assert pounit.source == "stringy"

    def test_emptyentry_translated(self):
        """checks that if we translate an empty definition it makes it into the PO"""
        phptemplate = """$lang['credit'] = '';"""
        phpsource = """$lang['credit'] = 'Translators Names';"""
        pofile = self.php2po(phpsource, phptemplate)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["$lang['credit']"]
        assert pounit.source == ""
        assert pounit.target == "Translators Names"

    def test_newlines_in_value(self):
        """check that we can carry newlines that appear in the entry value into the PO"""
        # Single quotes - \n is not a newline
        phpsource = r"""$lang['name'] = 'value1\nvalue2';"""
        pofile = self.php2po(phpsource)
        unit = self.singleelement(pofile)
        assert unit.source == r"value1\nvalue2"
        # Double quotes - \n is a newline
        phpsource = r"""$lang['name'] = "value1\nvalue2";"""
        pofile = self.php2po(phpsource)
        unit = self.singleelement(pofile)
        assert unit.source == "value1\nvalue2"

    def test_spaces_in_name(self):
        """checks that if we have spaces in the name we create a good PO with no spaces"""
        phptemplate = """$lang[ 'credit' ] = 'Something';"""
        phpsource = """$lang[ 'credit' ] = 'n Ding';"""
        pofile = self.php2po(phpsource, phptemplate)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["$lang[ 'credit' ]"]

    def test_named_array(self):
        phptemplate = """$strings = array(\n'id-1' => 'source-1',\n);"""
        phpsource = """$strings = array(\n'id-1' => 'target-1',\n);"""
        pofile = self.php2po(phpsource, phptemplate)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["$strings->'id-1'"]

    def test_unnamed_array(self):
        phptemplate = """return array(\n'id-1' => 'source-1',\n);"""
        phpsource = """return array(\n'id-1' => 'target-1',\n);"""
        pofile = self.php2po(phpsource, phptemplate)
        pounit = self.singleelement(pofile)
        assert pounit.getlocations() == ["return->'id-1'"]

    def test_named_nested_arrays(self):
        phptemplate = """$strings = array(
            'name1' => 'source1',
            'list1' => array(
                'l1' => 'source_l1_1',
                'l2' => 'source_l1_2',
                'l3' => 'source_l1_3',
            ),
            'list2' => array(
                'l1' => 'source_l2_1',
                'l2' => 'source_l2_2',
                'l3' => 'source_l2_3',
            ),
            'name2' => 'source2',
        );"""
        phpsource = """$strings = array(
            'name1' => 'target1',
            'list1' => array(
                'l1' => 'target_l1_1',
                'l2' => 'target_l1_2',
                'l3' => 'target_l1_3',
            ),
            'list2' => array(
                'l1' => 'target_l2_1',
                'l2' => 'target_l2_2',
                'l3' => 'target_l2_3',
            ),
            'name2' => 'target2',
        );"""
        pofile = self.php2po(phpsource, phptemplate)
        expected = {
            "$strings->'name1'": ("source1", "target1"),
            "$strings->'list1'->'l1'": ("source_l1_1", "target_l1_1"),
            "$strings->'list1'->'l2'": ("source_l1_2", "target_l1_2"),
            "$strings->'list1'->'l3'": ("source_l1_3", "target_l1_3"),
            "$strings->'list2'->'l1'": ("source_l2_1", "target_l2_1"),
            "$strings->'list2'->'l2'": ("source_l2_2", "target_l2_2"),
            "$strings->'list2'->'l3'": ("source_l2_3", "target_l2_3"),
            "$strings->'name2'": ("source2", "target2"),
        }
        for pounit in [x for x in pofile.units if x.source != ""]:
            assert (pounit.source, pounit.target) == expected.get(
                pounit.getlocations()[0]
            )

    def test_unnamed_nested_arrays(self):
        phptemplate = """return array(
            'name1' => 'source1',
            'list1' => array(
                'l1' => 'source_l1_1',
                'l2' => 'source_l1_2',
                'l3' => 'source_l1_3',
            ),
            'list2' => array(
                'l1' => 'source_l2_1',
                'l2' => 'source_l2_2',
                'l3' => 'source_l2_3',
            ),
            'name2' => 'source2',
        );"""
        phpsource = """return array  (
            'name1' => 'target1',
            'list1' => array(
                'l1' => 'target_l1_1',
                'l2' => 'target_l1_2',
                'l3' => 'target_l1_3',
            ),
            'list2' => array(
                'l1' => 'target_l2_1',
                'l2' => 'target_l2_2',
                'l3' => 'target_l2_3',
            ),
            'name2' => 'target2',
        );"""
        pofile = self.php2po(phpsource, phptemplate)
        expected = {
            "return->'name1'": ("source1", "target1"),
            "return->'list1'->'l1'": ("source_l1_1", "target_l1_1"),
            "return->'list1'->'l2'": ("source_l1_2", "target_l1_2"),
            "return->'list1'->'l3'": ("source_l1_3", "target_l1_3"),
            "return->'list2'->'l1'": ("source_l2_1", "target_l2_1"),
            "return->'list2'->'l2'": ("source_l2_2", "target_l2_2"),
            "return->'list2'->'l3'": ("source_l2_3", "target_l2_3"),
            "return->'name2'": ("source2", "target2"),
        }
        for pounit in [x for x in pofile.units if x.source != ""]:
            assert (pounit.source, pounit.target) == expected.get(
                pounit.getlocations()[0]
            )


class TestPhp2POCommand(test_convert.TestConvertCommand, TestPhp2PO):
    """Tests running actual php2po commands on files"""

    convertmodule = php2po
    defaultoptions = {"progress": "none"}

    expected_options = [
        "-P, --pot",
        "-t TEMPLATE, --template=TEMPLATE",
        "--duplicates=DUPLICATESTYLE",
    ]
