from io import BytesIO

from pytest import mark, raises

from translate.convert import po2php, test_convert
from translate.storage import po


class TestPO2Php:
    def po2php(self, posource):
        """helper that converts po source to .php source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        convertor = po2php.po2php()
        return convertor.convertstore(inputpo)

    def merge2php(self, phpsource, posource):
        """helper that merges po translations to .php source without requiring files"""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        templatefile = BytesIO(phpsource.encode())
        # templatephp = php.phpfile(templatefile)
        convertor = po2php.rephp(templatefile, inputpo)
        outputphp = [line.decode("utf-8") for line in convertor.convertstore()]
        print(outputphp)
        return outputphp

    def test_convertphp(self):
        """test convertphp helper"""
        posource = """#: $lang['name']
msgid "value"
msgstr "waarde"
"""
        phptemplate = """$lang['name'] = 'value';
"""
        phpexpected = b"""$lang['name'] = 'waarde';
"""
        inputfile = BytesIO(posource.encode())
        templatefile = BytesIO(phptemplate.encode())
        outputfile = BytesIO()
        assert po2php.convertphp(inputfile, outputfile, templatefile) == 1
        assert outputfile.getvalue() == phpexpected

    def test_convertphp_notemplate(self):
        """test convertphp helper without template"""
        posource = """#: $lang['name']
msgid "value"
msgstr "waarde"
"""
        inputfile = BytesIO(posource.encode())
        outputfile = BytesIO()
        with raises(ValueError):
            po2php.convertphp(inputfile, outputfile, None)

    def test_convertphp_empty_template(self):
        """test convertphp helper with empty translation"""
        posource = """#: $lang['name']
msgid "value"
msgstr ""
"""
        inputfile = BytesIO(posource.encode())
        templatefile = BytesIO(b"")
        outputfile = BytesIO()
        assert (
            po2php.convertphp(inputfile, outputfile, templatefile, False, 100) is False
        )
        assert outputfile.getvalue() == b""

    def test_merging_simple(self):
        """check the simplest case of merging a translation"""
        posource = """#: $lang['name']\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang['name'] = 'value';\n"""
        phpexpected = """$lang['name'] = 'waarde';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_space_preservation(self):
        """check that we preserve any spacing in php files when merging"""
        posource = """#: $lang['name']\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang['name']  =  'value';\n"""
        phpexpected = """$lang['name']  =  'waarde';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_preserve_unused_statement(self):
        """check that we preserve any unused statements in php files when merging"""
        posource = """#: $lang['name']
msgid "value"
msgstr "waarde"
"""
        phptemplate = """
error_reporting(E_ALL);
$lang['name']  =  'value';
"""
        phpexpected = """
error_reporting(E_ALL);
$lang['name']  =  'waarde';
"""
        phpfile = self.merge2php(phptemplate, posource)
        assert "".join(phpfile) == phpexpected

    def test_not_translated_multiline(self):
        """check that we preserve not translated multiline strings in php files when merging"""
        posource = """#: $lang['name']
msgid "value"
msgstr "waarde"
"""
        phptemplate = """
$lang['name']  =  'value';
$lang['second']  = "
value";
"""
        phpexpected = """
$lang['name']  =  'waarde';
$lang['second']  = "
value";
"""
        phpfile = self.merge2php(phptemplate, posource)
        assert "".join(phpfile) == phpexpected

    def test_merging_blank_entries(self):
        """check that we can correctly merge entries that are blank in the template"""
        posource = r'''#: accesskey-accept
msgid ""
"_: accesskey-accept\n"
""
msgstr ""'''
        phptemplate = """$lang['accesskey-accept'] = '';\n"""
        phpexpected = """$lang['accesskey-accept'] = '';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_merging_fuzzy(self):
        """check merging a fuzzy translation"""
        posource = """#: %24lang%5B+%27name%27+%5D\n#, fuzzy\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang['name']  =  'value';\n"""
        phpexpected = """$lang['name']  =  'value';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_locations_with_spaces(self):
        """check that a location with spaces in php but spaces removed in PO is used correctly"""
        posource = """#: %24lang%5B+%27name%27+%5D\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang[ 'name' ]  =  'value';\n"""
        phpexpected = """$lang[ 'name' ]  =  'waarde';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_inline_comments(self):
        """check that we include inline comments from the template.  Bug 590"""
        posource = """#: %24lang%5B+%27name%27+%5D\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang[ 'name' ]  =  'value'; //inline comment\n"""
        phpexpected = """$lang[ 'name' ]  =  'waarde'; //inline comment\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_block_comments(self):
        """check that we include block comments from the template"""
        posource = """#: %24lang%5B+%27name%27+%5D
msgid "value"
msgstr "waarde"
"""
        phptemplate = """/* some comment */
$lang[ 'name' ]  =  'value';
"""
        phpexpected = """/* some comment */
$lang[ 'name' ]  =  'waarde';
"""
        phpfile = self.merge2php(phptemplate, posource)
        assert "".join(phpfile) == phpexpected

    def test_named_variables(self):
        """check that we convert correctly if using named variables."""
        posource = """#: $dictYear
msgid "Year"
msgstr "Jaar"
"""
        phptemplate = """$dictYear = 'Year';\n"""
        phpexpected = """$dictYear = 'Jaar';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert phpfile == [phpexpected]

    def test_multiline(self):
        """
        Check that we convert multiline strings correctly.

        Bug 1296.
        """
        posource = r"""#: $string['upgradesure']
msgid ""
"Your Moodle files have been changed, and you are\n"
"about to automatically upgrade your server to this version:\n"
"<p><b>$a</b></p>\n"
"<p>Once you do this you can not go back again.</p>\n"
"<p>Are you sure you want to upgrade this server to this version?</p>"
msgstr ""
"""
        phptemplate = """$string['upgradesure'] = 'Your Moodle files have been changed, and you are
about to automatically upgrade your server to this version:
<p><b>$a</b></p>
<p>Once you do this you can not go back again.</p>
<p>Are you sure you want to upgrade this server to this version?</p>';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile[0])
        assert phpfile[0] == phptemplate

    def test_hash_comment(self):
        """check that we convert # comments correctly."""
        posource = """#: $variable
msgid "stringy"
msgstr "stringetjie"
"""
        phptemplate = """# inside alt= stuffies\n$variable = 'stringy';\n"""
        phpexpected = """# inside alt= stuffies\n$variable = 'stringetjie';\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert "".join(phpfile) == phpexpected

    def test_arrays(self):
        """check that we can handle arrays"""
        posource = """#: $lang->'name'\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang = array(\n    'name' => 'value',\n);\n"""
        phpexpected = """$lang = array(\n    'name' => 'waarde',\n);\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert "".join(phpfile) == phpexpected

    def test_named_nested_array(self):
        """check that we can handle nested arrays"""
        posource = """#: $lang->'codes'->'name'\nmsgid "value"\nmsgstr "waarde"\n"""
        phptemplate = """$lang = array(\n    'codes' => array(\n        'name' => 'value',\n),\n);\n"""
        phpexpected = """$lang = array(\n    'codes' => array(\n        'name' => 'waarde',\n),\n);\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert "".join(phpfile) == phpexpected

    def test_unnamed_nested_arrays(self):
        posource = """
#: 'name1'
msgid "source1"
msgstr "target1"

#: 'list1'->'l1'
msgid "source_l1_1"
msgstr "target_l1_1"

#: 'list1'->'list2'->'l1'
msgid "source_l1_l2_l1"
msgstr "target_l1_l2_l1"

#: 'list1'->'l3'
msgid "source_l1_3"
msgstr "target_l1_3"

#: 'name2'
msgid "source2"
msgstr "target2"
"""
        phptemplate = """return array(
            'name1' => 'source1',
            'list1' => array(
                'l1' => 'source_l1_1',
                'list2' => array(
                    'l1' => 'source_l1_l2_l1',
                ),
                'l3' => 'source_l1_3',
            ),
            'name2' => 'source2',
        );"""
        phpexpected = """return array(
            'name1' => 'target1',
            'list1' => array(
                'l1' => 'target_l1_1',
                'list2' => array(
                    'l1' => 'target_l1_l2_l1',
                ),
                'l3' => 'target_l1_3',
            ),
            'name2' => 'target2',
        );\n"""
        phpfile = self.merge2php(phptemplate, posource)
        print(phpfile)
        assert "".join(phpfile) == phpexpected

    @mark.xfail(reason="Need to review if we want this behaviour")
    def test_merging_propertyless_template(self):
        """check that when merging with a template with no property values that we copy the template"""
        posource = ""
        proptemplate = "# A comment\n"
        propexpected = proptemplate
        propfile = self.merge2prop(proptemplate, posource)
        print(propfile)
        assert propfile == [propexpected]


class TestPO2PhpCommand(test_convert.TestConvertCommand, TestPO2Php):
    """Tests running actual po2php commands on files"""

    convertmodule = po2php
    defaultoptions = {"progress": "none"}

    def test_help(self, capsys):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self, capsys)
        options = self.help_check(options, "-t TEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--threshold=PERCENT")
        options = self.help_check(options, "--fuzzy")
        options = self.help_check(options, "--nofuzzy", last=True)
