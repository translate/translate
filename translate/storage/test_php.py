from io import BytesIO

from translate.misc.multistring import multistring
from translate.storage import php, test_monolingual


def test_php_escaping_single_quote():
    """
    Test the helper escaping funtions for 'single quotes'

    The tests are built mostly from examples from the PHP
    `string type definition <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_.
    """
    # Decoding - PHP -> Python
    assert (
        php.phpdecode(r"\'") == r"'"
    )  # To specify a literal single quote, escape it with a backslash (\).
    assert php.phpdecode(r'"') == r'"'
    assert (
        php.phpdecode(r"\\'") == r"\'"
    )  # To specify a literal backslash before a single quote, or at the end of the string, double it (\\)
    assert (
        php.phpdecode(r"\x") == r"\x"
    )  # Note that attempting to escape any other character will print the backslash too.
    assert php.phpdecode(r"\t") == r"\t"
    assert php.phpdecode(r"\n") == r"\n"
    assert php.phpdecode(r"this is a simple string") == r"this is a simple string"
    assert (
        php.phpdecode(
            """You can also have embedded newlines in
strings this way as it is
okay to do"""
        )
        == """You can also have embedded newlines in
strings this way as it is
okay to do"""
    )
    assert (
        php.phpdecode(r"This will not expand: \n a newline")
        == r"This will not expand: \n a newline"
    )
    assert (
        php.phpdecode(r'Arnold once said: "I\'ll be back"')
        == r'''Arnold once said: "I'll be back"'''
    )
    assert php.phpdecode(r"You deleted C:\\*.*?") == r"You deleted C:\*.*?"
    assert php.phpdecode(r"You deleted C:\*.*?") == r"You deleted C:\*.*?"
    assert (
        php.phpdecode(r"\117\143\164\141\154") == r"\117\143\164\141\154"
    )  # We don't handle Octal like " does
    assert php.phpdecode(r"\x48\x65\x78") == r"\x48\x65\x78"  # Don't handle Hex either
    # Should implement for false interpretation of double quoted data.
    # Encoding - Python -> PHP
    assert (
        php.phpencode(r"'") == r"\'"
    )  # To specify a literal single quote, escape it with a backslash (\).
    assert (
        php.phpencode(r"\'") == r"\\'"
    )  # To specify a literal backslash before a single quote, or at the end of the string, double it (\\)
    assert php.phpencode(r'"') == r'"'
    assert (
        php.phpencode(r"\x") == r"\x"
    )  # Note that attempting to escape any other character will print the backslash too.
    assert php.phpencode(r"\t") == r"\t"
    assert php.phpencode(r"\n") == r"\n"
    assert (
        php.phpencode(
            r"""String with
newline"""
        )
        == r"""String with
newline"""
    )
    assert (
        php.phpencode(r"This will not expand: \n a newline")
        == r"This will not expand: \n a newline"
    )
    assert (
        php.phpencode(r'''Arnold once said: "I'll be back"''')
        == r'''Arnold once said: "I\'ll be back"'''
    )
    assert php.phpencode(r"You deleted C:\*.*?") == r"You deleted C:\*.*?"


def test_php_escaping_double_quote():
    """Test the helper escaping funtions for 'double quotes'"""
    # Decoding - PHP -> Python
    assert php.phpdecode("'", quotechar='"') == "'"  # we do nothing with single quotes
    assert (
        php.phpdecode(r"\n", quotechar='"') == "\n"
    )  # See table of escaped characters
    assert (
        php.phpdecode(r"\r", quotechar='"') == "\r"
    )  # See table of escaped characters
    assert (
        php.phpdecode(r"\t", quotechar='"') == "\t"
    )  # See table of escaped characters
    assert (
        php.phpdecode(r"\v", quotechar='"') == "\v"
    )  # See table of escaped characters
    assert (
        php.phpdecode(r"\f", quotechar='"') == "\f"
    )  # See table of escaped characters
    assert (
        php.phpdecode(r"\\", quotechar='"') == "\\"
    )  # See table of escaped characters
    # assert php.phpdecode(r"\$", quotechar='"') == "$"      # See table of escaped characters - this may cause confusion with actual variables in roundtripping
    assert (
        php.phpdecode(r"\$", quotechar='"') == "\\$"
    )  # Just to check that we don't unescape this
    assert php.phpdecode(r"\"", quotechar='"') == '"'  # See table of escaped characters
    assert (
        php.phpdecode(r"\117\143\164\141\154", quotechar='"') == "Octal"
    )  # Octal: \[0-7]{1,3}
    assert (
        php.phpdecode(r"\x48\x65\x78", quotechar='"') == "Hex"
    )  # Hex: \x[0-9A-Fa-f]{1,2}
    assert php.phpdecode(r"\117\\c\164\141\154", quotechar='"') == r"O\ctal"  # Mixed
    # Decoding - special examples
    assert (
        php.phpdecode(r"Don't escape me here\'s", quotechar='"')
        == r"Don't escape me here\'s"
    )  # See bug #589
    assert (
        php.phpdecode("Line1\nLine2") == "Line1\nLine2"
    )  # Preserve newlines in multiline messages
    assert php.phpdecode("Line1\r\nLine2") == "Line1\r\nLine2"  # DOS PHP files
    # Encoding - Python -> PHP
    assert php.phpencode("'", quotechar='"') == "'"
    assert (
        php.phpencode("\n", quotechar='"') == "\n"
    )  # See table of escaped characters - we leave newlines unescaped so that we can try best to preserve pretty printing. See bug 588
    assert (
        php.phpencode("\r", quotechar='"') == r"\r"
    )  # See table of escaped characters
    assert (
        php.phpencode("\t", quotechar='"') == r"\t"
    )  # See table of escaped characters
    assert (
        php.phpencode("\v", quotechar='"') == r"\v"
    )  # See table of escaped characters
    assert (
        php.phpencode("\f", quotechar='"') == r"\f"
    )  # See table of escaped characters
    assert (
        php.phpencode(r"\\", quotechar='"') == r"\\"
    )  # See table of escaped characters
    # assert php.phpencode("\$", quotechar='"') == "$"      # See table of escaped characters - this may cause confusion with actual variables in roundtripping
    assert (
        php.phpencode(r"\$", quotechar='"') == r"\$"
    )  # Just to check that we don't unescape this
    assert php.phpencode('"', quotechar='"') == r"\""
    assert (
        php.phpencode(r"Don't escape me here\'s", quotechar='"')
        == r"Don't escape me here\'s"
    )  # See bug #589


class TestPhpUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = php.phpunit

    def test_difficult_escapes(self):
        pass


class TestPhpFile(test_monolingual.TestMonolingualStore):
    StoreClass = php.phpfile

    @staticmethod
    def phpparse(phpsource):
        """helper that parses php source without requiring files"""
        dummyfile = BytesIO(phpsource.encode())
        return php.phpfile(dummyfile)

    def phpregen(self, phpsource):
        """helper that converts php source to phpfile object and back"""
        return bytes(self.phpparse(phpsource)).decode("utf-8")

    def test_simpledefinition(self):
        """checks that a simple php definition is parsed correctly"""
        phpsource = """$lang['mediaselect'] = 'Bestand selectie';"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang['mediaselect']"
        assert phpunit.source == "Bestand selectie"

    def test_simpledefinition_source(self):
        """checks that a simple php definition can be regenerated as source"""
        phpsource = """<?php
$lang['mediaselect'] = 'Bestand selectie';"""
        phpregen = self.phpregen(phpsource)
        assert phpsource + "\n" == phpregen

    def test_spaces_in_name(self):
        """check that spaces in the array name doesn't throw us off"""
        phpsource = """$lang[ 'mediaselect' ] = 'Bestand selectie';"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang[ 'mediaselect' ]"
        assert phpunit.source == "Bestand selectie"

    def test_comment_definition(self):
        """check that comments are fully preserved"""
        phpsource = """/*
 * Comment line 1
 * Comment line 2
 */
$foo = "bar";
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$foo"
        assert phpunit.source == "bar"
        assert phpunit._comments == [
            """/*
 * Comment line 1
 * Comment line 2
 */"""
        ]

    def test_comment_blocks(self):
        """check that we don't process name value pairs in comment blocks"""
        phpsource = """/*
 * $lang[0] = "Blah";
 * $lang[1] = "Bluh";
 */
$lang[2] = "Yeah";
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang[2]"
        assert phpunit.source == "Yeah"

    def test_comment_output(self):
        """check that linebreaks and spacing is preserved when comments are output"""
        phpsource = """/*
 * Comment line 1
 * Comment line 2
 */
$foo = 'bar';
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert str(phpunit) == phpsource

    def test_comment_add(self):
        """check that comments are actually added"""
        phpsource = """/* NOTE 1 */
$foo = 'bar';
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$foo"
        assert phpunit.source == "bar"
        assert phpunit._comments == ["/* NOTE 1 */"]
        # Replace existing notes
        phpunit.addnote("/* NOTE 2 */", None, "replace")
        # Set unknown note
        phpunit.addnote("/* NOTE 2 */", "unknown")
        assert phpunit._comments == ["/* NOTE 2 */"]
        assert str(phpunit) == phpsource.replace("NOTE 1", "NOTE 2")

    def test_multiline(self):
        """check that we preserve newlines in a multiline message"""
        phpsource = """$lang['multiline'] = "Line1%sLine2";"""
        # Try DOS and Unix and make sure the output has the same
        for lineending in ("\n", "\r\n"):
            phpfile = self.phpparse(phpsource % lineending)
            assert len(phpfile.units) == 1
            phpunit = phpfile.units[0]
            assert phpunit.name == "$lang['multiline']"
            assert phpunit.source == "Line1%sLine2" % lineending

    def test_parsing_arrays(self):
        """parse the array syntax"""
        phpsource = """$lang = %s(
         'item1' => 'value1',
         'item2' => 'value2',
      );"""
        for arrayfn in ["array", "Array", "ARRAY"]:
            phpfile = self.phpparse(phpsource % arrayfn)
            assert len(phpfile.units) == 2
            phpunit = phpfile.units[0]
            assert phpunit.name == "$lang->'item1'"
            assert phpunit.source == "value1"

    def test_parsing_array_no_array_syntax(self):
        """parse the array syntax"""
        phpsource = """global $_LANGPDF;
        $_LANGPDF = array();
        $_LANGPDF['PDF065ab3a28ca4f16f55f103adc7d0226f'] = 'Delivery';
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$_LANGPDF['PDF065ab3a28ca4f16f55f103adc7d0226f']"
        assert phpunit.source == "Delivery"

    def test_parsing_arrays_keys_with_spaces(self):
        """Ensure that our identifiers can have spaces. Bug #1683"""
        phpsource = """$lang = array(
         'item 1' => 'value1',
         'item 2' => 'value2',
      );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item 1'"
        assert phpunit.source == "value1"

    def test_parsing_arrays_non_textual(self):
        """Don't break on non-textual data. Bug #1684"""
        phpsource = """$lang = array(
         'item 1' => 'value1',
         'item 2' => false,
         'item 3' => 'value3',
      );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'item 3'"
        assert phpunit.source == "value3"

    def test_parsing_simple_define(self):
        """Parse simple define syntax"""
        phpsource = """define("_FINISH", "Rematar");
define('_POSTEDON', 'Enviado o');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_FINISH"'
        assert phpunit.source == "Rematar"
        phpunit = phpfile.units[1]
        assert phpunit.name == "define('_POSTEDON'"
        assert phpunit.source == "Enviado o"

    def test_parsing_simple_define_with_spaces_before_key(self):
        """Parse simple define syntax with spaces before key"""
        phpsource = """define( "_FINISH", "Rematar");
define( '_CM_POSTED', 'Enviado');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define( "_FINISH"'
        assert phpunit.source == "Rematar"
        phpunit = phpfile.units[1]
        assert phpunit.name == "define( '_CM_POSTED'"
        assert phpunit.source == "Enviado"

    def test_parsing_define_spaces_after_equal_delimiter(self):
        """Parse define syntax with spaces after the equal delimiter"""
        phpsource = """define("_RELOAD",       "Recargar");
define('_CM_POSTED',    'Enviado');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_RELOAD"'
        assert phpunit.source == "Recargar"
        phpunit = phpfile.units[1]
        assert phpunit.name == "define('_CM_POSTED'"
        assert phpunit.source == "Enviado"

    def test_parsing_define_spaces_after_equal_delimiter_and_before_key(self):
        """
        Parse define syntax with spaces after the equal delimiter as well
        before the key
        """
        phpsource = """define( "_FINISH",       "Rematar");
define(  '_UPGRADE_CHARSET',    'Upgrade charset');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define( "_FINISH"'
        assert phpunit.source == "Rematar"
        phpunit = phpfile.units[1]
        assert phpunit.name == "define(  '_UPGRADE_CHARSET'"
        assert phpunit.source == "Upgrade charset"

    def test_parsing_define_no_spaces_after_equal_delimiter(self):
        """Parse define syntax without spaces after the equal delimiter"""
        phpsource = """define("_POSTEDON","Enviado o");
define('_UPGRADE_CHARSET','Upgrade charset');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_POSTEDON"'
        assert phpunit.source == "Enviado o"
        phpunit = phpfile.units[1]
        assert phpunit.name == "define('_UPGRADE_CHARSET'"
        assert phpunit.source == "Upgrade charset"

    def test_parsing_define_no_spaces_after_equaldel_but_before_key(self):
        """
        Parse define syntax without spaces after the equal delimiter but
        with spaces before the key
        """
        phpsource = """define( "_FINISH","Rematar");
define( '_CM_POSTED','Enviado');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define( "_FINISH"'
        assert phpunit.source == "Rematar"
        phpunit = phpfile.units[1]
        assert phpunit.name == "define( '_CM_POSTED'"
        assert phpunit.source == "Enviado"

    def test_parsing_define_entries_with_quotes(self):
        """Parse define syntax for entries with quotes"""
        phpsource = r"""define('_SETTINGS_COOKIEPREFIX', 'Prefixo da "cookie"');
define('_YOUR_USERNAME', 'O seu nome de usuario: "cookie"');
define("_REGISTER", "Register <a href=\"register.php\">here</a>");"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == "define('_SETTINGS_COOKIEPREFIX'"
        assert phpunit.source == 'Prefixo da "cookie"'
        phpunit = phpfile.units[1]
        assert phpunit.name == "define('_YOUR_USERNAME'"
        assert phpunit.source == 'O seu nome de usuario: "cookie"'
        phpunit = phpfile.units[2]
        assert phpunit.name == 'define("_REGISTER"'
        assert phpunit.source == 'Register <a href="register.php">here</a>'

    def test_parsing_define_comments_at_entry_line_end(self):
        """Parse define syntax with comments at the end of the entry line"""
        phpsource = """define("_POSTEDON", "Enviado o");// Keep this short
define('_CM_POSTED', 'Enviado'); // Posted date"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_POSTEDON"'
        assert phpunit.source == "Enviado o"
        assert phpunit._comments == ["// Keep this short"]
        phpunit = phpfile.units[1]
        assert phpunit.name == "define('_CM_POSTED'"
        assert phpunit.source == "Enviado"
        assert phpunit._comments == ["// Posted date"]

    def test_parsing_define_double_slash_comments_before_entries(self):
        """Parse define syntax with double slash comments before the entries"""
        phpsource = """// Keep this short
define("_FINISH", "Rematar");

// This means it was published
// It appears besides posts
define('_CM_POSTED', 'Enviado');"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_FINISH"'
        assert phpunit.source == "Rematar"
        assert phpunit._comments == ["// Keep this short"]
        phpunit = phpfile.units[1]
        assert phpunit.name == "define('_CM_POSTED'"
        assert phpunit.source == "Enviado"
        assert phpunit._comments == [
            "// This means it was published",
            "// It appears besides posts",
        ]

    def test_parsing_define_spaces_before_end_delimiter(self):
        """Parse define syntax with spaces before the end delimiter"""
        phpsource = """define("_POSTEDON", "Enviado o");
define("_FINISH", "Rematar"     );
define("_RELOAD", "Recargar");"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_POSTEDON"'
        assert phpunit.source == "Enviado o"
        phpunit = phpfile.units[1]
        assert phpunit.name == 'define("_FINISH"'
        assert phpunit.source == "Rematar"
        phpunit = phpfile.units[2]
        assert phpunit.name == 'define("_RELOAD"'
        assert phpunit.source == "Recargar"

    def test_parsing_simpledefinition_spaces_before_end_delimiter(self):
        """Parse simple definition syntax with spaces before the end delimiter"""
        phpsource = """$month_jan = 'Jan';
$month_feb = 'Feb'  ;
$month_mar = 'Mar';"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == "$month_jan"
        assert phpunit.source == "Jan"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$month_feb"
        assert phpunit.source == "Feb"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$month_mar"
        assert phpunit.source == "Mar"

    def test_parsing_arrays_no_trailing_comma(self):
        """
        Parse the array syntax where we don't have a trailing comma.

        Bug #1685
        """
        phpsource = """$lang = array(
         'item1' => 'value1',
         'item2' => 'value2'
      );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"

    def test_parsing_arrays_space_before_comma(self):
        """
        parse the array syntax with spaces before the comma.

        Bug #1898
        """
        phpsource = """$lang = array(
         'item1' => 'value1',
         'item2' => 'value2' ,
        );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"

    def test_parsing_arrays_with_space_before_array_declaration(self):
        """
        parse the array syntax with spaces before the array declaration.

        Bug #2646
        """
        phpsource = """$lang = array   (
         'item1' => 'value1',
         'item2' => 'value2',
        );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"

    def test_parsing_arrays_declared_in_a_single_line(self):
        """
        parse an array declared in a single line.

        Bug #3629
        """
        phpsource = """$lang = array( 'item1' => 'value1', 'item2' => 'value2', 'item3' => 'value3' );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$lang->'item3'"
        assert phpunit.source == "value3"

    def test_parsing_arrays_with_no_keys(self):
        """Parse an array with no keys."""
        phpsource = """<?php
$days = array(
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    "Saturday",
);
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 7
        phpunit = phpfile.units[0]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Sunday"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Monday"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Tuesday"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Wednesday"
        phpunit = phpfile.units[4]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Thursday"
        phpunit = phpfile.units[5]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Friday"
        phpunit = phpfile.units[6]
        assert phpunit.name == "$days->[]"
        assert phpunit.source == "Saturday"
        assert bytes(phpfile).decode() == phpsource

    def test_parsing_arrays_with_no_keys_assigned_to_array(self):
        """Parse an array with no keys assigned to another array."""
        phpsource = """<?php
$messages['days_short'] = array(
    'Sun',
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    "Fri",
    'Sat',
);
"""
        phpfile = self.phpparse(phpsource)
        assert bytes(phpfile).decode() == phpsource
        assert len(phpfile.units) == 7
        phpunit = phpfile.units[0]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Sun"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Mon"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Tue"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Wed"
        phpunit = phpfile.units[4]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Thu"
        phpunit = phpfile.units[5]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Fri"
        phpunit = phpfile.units[6]
        assert phpunit.name == "$messages['days_short']->[]"
        assert phpunit.source == "Sat"

    def test_parsing_nested_arrays_with_no_keys(self):
        """Parse a nested array with no keys."""
        phpsource = """$lang = array(array("key" => "value"));"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->[]->'key'"
        assert phpunit.source == "value"

    def test_assignment_in_line_where_multiline_comment_ends(self):
        """Check parsing assignment in same line a multiline comment ends."""
        phpsource = """<?php
/*
   Multi-line
   comment
*/ $messages['help'] = 'Help';
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$messages['help']"
        assert phpunit.source == "Help"

    def test_parsing_arrays_using_short_array_syntax(self):
        """parse short array syntax.  Bug #3626"""
        phpsource = """<?php
$lang = [
    'item1' => 'value1',
    'item2' => 'value2',
];
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang[]->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang[]->'item2'"
        assert phpunit.source == "value2"
        assert bytes(phpfile).decode() == phpsource

    def test_parsing_nested_arrays(self):
        """parse the nested array syntax. Bug #2240"""
        phpsource = """$app_list_strings = array(
            'Mailbox' => 'Mailbox',
            'moduleList' => array(
                'Home' => 'Home',
                'Contacts' => 'Contacts',
                'Accounts' => 'Accounts',
            ),
            'FAQ' => 'FAQ',
        );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 5
        phpunit = phpfile.units[0]
        assert phpunit.name == "$app_list_strings->'Mailbox'"
        assert phpunit.source == "Mailbox"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$app_list_strings->'moduleList'->'Home'"
        assert phpunit.source == "Home"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$app_list_strings->'moduleList'->'Contacts'"
        assert phpunit.source == "Contacts"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$app_list_strings->'moduleList'->'Accounts'"
        assert phpunit.source == "Accounts"
        phpunit = phpfile.units[4]
        assert phpunit.name == "$app_list_strings->'FAQ'"
        assert phpunit.source == "FAQ"

    def test_parsing_nested_arrays_with_space_before_array_declaration(self):
        """parse the nested array syntax with whitespace before the array declaration."""
        phpsource = """$app_list_strings = array  (
            'Mailbox' => 'Mailbox',
            'moduleList' => array  (
                'Home' => 'Home',
                'Contacts' => 'Contacts',
                'Accounts' => 'Accounts',
            ),
            'tools' => array  (
                'Pen' => 'Pen',
                'Brush' => 'Brush',
                'Pencil' => 'Pencil',
            ),
            'FAQ' => 'FAQ',
        );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 8
        phpunit = phpfile.units[0]
        assert phpunit.name == "$app_list_strings->'Mailbox'"
        assert phpunit.source == "Mailbox"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$app_list_strings->'moduleList'->'Home'"
        assert phpunit.source == "Home"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$app_list_strings->'moduleList'->'Contacts'"
        assert phpunit.source == "Contacts"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$app_list_strings->'moduleList'->'Accounts'"
        assert phpunit.source == "Accounts"
        phpunit = phpfile.units[4]
        assert phpunit.name == "$app_list_strings->'tools'->'Pen'"
        assert phpunit.source == "Pen"
        phpunit = phpfile.units[5]
        assert phpunit.name == "$app_list_strings->'tools'->'Brush'"
        assert phpunit.source == "Brush"
        phpunit = phpfile.units[6]
        assert phpunit.name == "$app_list_strings->'tools'->'Pencil'"
        assert phpunit.source == "Pencil"
        phpunit = phpfile.units[7]
        assert phpunit.name == "$app_list_strings->'FAQ'"
        assert phpunit.source == "FAQ"

    def test_parsing_unnamed_nested_arrays(self):
        """parse the unnamed nested array."""

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
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 8
        phpunit = phpfile.units[0]
        assert phpunit.name == "return->'name1'"
        assert phpunit.source == "target1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "return->'list1'->'l1'"
        assert phpunit.source == "target_l1_1"
        phpunit = phpfile.units[2]
        assert phpunit.name == "return->'list1'->'l2'"
        assert phpunit.source == "target_l1_2"
        phpunit = phpfile.units[3]
        assert phpunit.name == "return->'list1'->'l3'"
        assert phpunit.source == "target_l1_3"
        phpunit = phpfile.units[4]
        assert phpunit.name == "return->'list2'->'l1'"
        assert phpunit.source == "target_l2_1"

    def test_parsing_nested_arrays_with_array_declaration_in_next_line(self):
        """
        parse the nested array syntax with array declaration in the next line.

        Bug #2647
        """
        phpsource = """$lang = array(
            'item1' => 'value1',
            'newsletter_frequency_dom' =>
                array(
                    'Weekly' => 'Weekly',
                ),
            'item2' => 'value2',
        );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'newsletter_frequency_dom'->'Weekly'"
        assert phpunit.source == "Weekly"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"

    def test_parsing_array_with_newline_after_delimiter(self):
        """
        Parse array with newline between key and value.

        Bug #3628.
        """
        phpsource = """$lang = array(
            'item1' => 'value1',
            'frequency' =>
                'Weekly',
            'item2' => 'value2',
        );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'frequency'"
        assert phpunit.source == "Weekly"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"

    def test_parsing_nested_arrays_with_blank_entries(self):
        """parse the nested array syntax with blank entries. Bug #2648"""
        phpsource = """<?php
$lang = array(
    'item1' => 'value1',
    'newsletter_frequency_dom' => array(
        '' => '',
        'Weekly' => 'Weekly',
    ),
    'item2' => 'value2',
);
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 4
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang->'item1'"
        assert phpunit.source == "value1"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'newsletter_frequency_dom'->''"
        assert phpunit.source == ""
        phpunit = phpfile.units[2]
        assert phpunit.name == "$lang->'newsletter_frequency_dom'->'Weekly'"
        assert phpunit.source == "Weekly"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$lang->'item2'"
        assert phpunit.source == "value2"
        assert bytes(phpfile).decode() == phpsource

    def test_slashstar_in_string(self):
        """ignore the /* comment delimiter when it is part of a string.  Bug #3627"""
        phpsource = """$definition['key'] = 'Value /* value continued';
      $lang = array(
         'somekey' => 'Some value',
         'otherkey' => 'Other value /* continued',
         'thirdkey' => 'Third value',
      );"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 4
        phpunit = phpfile.units[0]
        assert phpunit.name == "$definition['key']"
        assert phpunit.source == "Value /* value continued"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang->'somekey'"
        assert phpunit.source == "Some value"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$lang->'otherkey'"
        assert phpunit.source == "Other value /* continued"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$lang->'thirdkey'"
        assert phpunit.source == "Third value"

    def test_parsing_simple_heredoc_syntax(self):
        """parse the heredoc syntax. Bug #2611"""
        phpsource = """$month_jan = 'Jan';
$lang_register_approve_email = <<<EOT
A new user with the username "{USER_NAME}" has registered in your gallery.

In order to activate the account, you need to click on the link below.

<a href="{ACT_LINK}">{ACT_LINK}</a>
EOT;

$foobar = <<<FOOBAR
Simple example
FOOBAR;

$month_mar = 'Mar';
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 4
        phpunit = phpfile.units[0]
        assert phpunit.name == "$month_jan"
        assert phpunit.source == "Jan"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang_register_approve_email"
        assert (
            phpunit.source
            == 'A new user with the username "{USER_NAME}" has registered in your gallery.\n\nIn order to activate the account, you need to click on the link below.\n\n<a href="{ACT_LINK}">{ACT_LINK}</a>'
        )
        phpunit = phpfile.units[2]
        assert phpunit.name == "$foobar"
        assert phpunit.source == "Simple example"
        phpunit = phpfile.units[3]
        assert phpunit.name == "$month_mar"
        assert phpunit.source == "Mar"

    def test_simpledefinition_after_define(self):
        """Check that a simple definition after define is parsed correctly."""
        phpsource = """define("_FINISH", "Rematar");
$lang['mediaselect'] = 'Bestand selectie';"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == 'define("_FINISH"'
        assert phpunit.source == "Rematar"
        phpunit = phpfile.units[1]
        assert phpunit.name == "$lang['mediaselect']"
        assert phpunit.source == "Bestand selectie"

    def test_quotes(self):
        phpsource = """<?php
$txt[\'DISPLAYEDINFOS\'] = "<a href=\\"__PARAM2__\\">Modificar...</a>";
"""
        phpfile = self.phpparse(phpsource)
        assert bytes(phpfile).decode() == phpsource

    def test_concatenation(self):
        """Check that concatenating strings and variables is parsed correctly."""
        phpsource = """
$lang['mediaselect'] = "Really \\\"something\\\"" . $variable . "\\\"something else\\\"";
$messages['welcome'] = 'Welcome ' . $name . '!';
$messages['greeting'] = 'Hi ' . $name;
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        phpunit = phpfile.units[0]
        assert phpunit.name == "$lang['mediaselect']"
        assert phpunit.source == 'Really "something"$variable"something else"'
        phpunit = phpfile.units[1]
        assert phpunit.name == "$messages['welcome']"
        assert phpunit.source == "Welcome $name!"
        phpunit = phpfile.units[2]
        assert phpunit.name == "$messages['greeting']"
        assert phpunit.source == "Hi $name"

    def test_serialize(self):
        phpsource = """<?php
# Comment 1
define("_FINISH", 'Rematar');
// Comment 2
define("_START", "Zacni");
/* Comment 3 */
$lang['mediaselect'] = 'Bestand selectie';
$texts = array(
    /*
     * Multiline comment 4
     */
    'other' => 'Andere',
    'nested' => array(
        'and' => 'Und',
        'second' => 'Zweite',
    ),
);
"""
        phpfile = self.phpparse(phpsource)
        assert bytes(phpfile).decode() == phpsource

    def test_space_before_comma(self):
        """
        check that spacing before comma or semicolon doesn't break parser

        See #1898
        """
        phpsource = """
        $english = array(
            'item:site'  =>  "Sítios",
            'login'  =>  "Entrar" ,
            'loginok'  =>  "Entrou com sucesso." ,
        );
        $month_jan = 'Jan';
        $month_feb = 'Feb'  ;
        $month_mar = 'Mar';
        define("_SEARCH","Search");
        define("_LOGIN","Login"  );
        define("_POLLS","Polls");
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 9

    def test_equals_in_id(self):
        """
        Check that equals in id doesn't break parser.

        See #1929
        """
        phpsource = """
        $strings['key = value'] = 'Message';
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        assert phpfile.units[0].source == "Message"
        assert phpfile.units[0].name == "$strings['key = value']"

    def test_comma_in_string(self):
        """
        Check that comma in string doesn't break parser.

        See #3608
        """
        phpsource = """
        $t = array(
            'key' => ' text (comment **),**',
        );
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        assert phpfile.units[0].source == " text (comment **),**"
        assert phpfile.units[0].name == "$t->'key'"

    def test_nowdoc(self):
        """check parsing nowdoc strings"""
        phpsource = """$str = <<<'EOD'
Example of string
spanning multiple lines
using nowdoc syntax.
EOD;
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        assert (
            phpfile.units[0].source
            == """Example of string
spanning multiple lines
using nowdoc syntax."""
        )
        assert phpfile.units[0].name == "$str"

    def test_plain_concatenation(self):
        """check parsing concatenated strings"""
        phpsource = """$str = 'Concatenated' . ' ' . 'string';
        $arr['x'] = 'Concatenated' . ' ' . 'string';
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        assert phpfile.units[0].source == "Concatenated string"
        assert phpfile.units[0].name == "$str"
        assert phpfile.units[1].source == "Concatenated string"
        assert phpfile.units[1].name == "$arr['x']"

    def test_array_keys(self):
        """check parsing different array keys"""
        phpsource = """
        $arr = [
            '1234' => 'First',
            1234 => 'Second',
            '12' . '45' => 'Third',
        ];
        """
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 3
        assert phpfile.units[0].source == "First"
        assert phpfile.units[0].name == "$arr[]->'1234'"
        assert phpfile.units[1].source == "Second"
        assert phpfile.units[1].name == "$arr[]->1234"
        assert phpfile.units[2].source == "Third"
        assert phpfile.units[2].name == "$arr[]->'1245'"

    def test_double_var(self):
        """checks that a double $ is handled correctly"""
        phpsource = """$$lang['mediaselect'] = 'Bestand selectie';"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "$$lang['mediaselect']"
        assert phpunit.source == "Bestand selectie"

    def test_return_array(self):
        phpsource = """<?php
return array(
    'peach' => 'pesca',
);
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "return->'peach'"
        assert phpunit.source == "pesca"
        assert bytes(phpfile).decode() == phpsource

    def test_return_array_short(self):
        phpsource = """<?php
return [
    'peach' => 'pesca',
];
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.name == "return[]->'peach'"
        assert phpunit.source == "pesca"
        assert bytes(phpfile).decode() == phpsource
        phpunit.source = "ryba"
        assert bytes(phpfile).decode() != phpsource
        phpunit.source = "pesca"
        assert bytes(phpfile).decode() == phpsource

    def test_return_array_short_quotes(self):
        phpsource = r"""<?php
return [
    'peach' => "foo \"pesca\"",
];
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 1
        phpunit = phpfile.units[0]
        assert phpunit.escape_type == '"'
        assert phpunit.name == "return[]->'peach'"
        assert phpunit.source == 'foo "pesca"'
        assert bytes(phpfile).decode() == phpsource
        phpunit.source = "ryba"
        assert bytes(phpfile) != phpsource
        phpunit.source = 'foo "pesca"'
        assert bytes(phpfile).decode() == phpsource

    def test_addunit(self):
        expected = """<?php
$key = 'first';
$sec = 'second';
"""
        store = self.StoreClass()

        unit = self.StoreClass.UnitClass("first")
        unit.setid("key")
        store.addunit(unit)
        unit = self.StoreClass.UnitClass("second")
        unit.setid("$sec")
        store.addunit(unit)
        assert bytes(store).decode() == expected


class TestLaravelPhpUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = php.LaravelPHPUnit


class TestLaravelPhpFile(test_monolingual.TestMonolingualStore):
    StoreClass = php.LaravelPHPFile

    def phpparse(self, phpsource):
        """helper that parses php source without requiring files"""
        dummyfile = BytesIO(phpsource.encode())
        return self.StoreClass(dummyfile)

    def test_plurals(self):
        phpsource = r"""<?php
return [
    'welcome' => 'Welcome to our application',
    'apples' => 'There is one apple|There are many apples',
];
"""
        phpfile = self.phpparse(phpsource)
        assert len(phpfile.units) == 2
        phpunit = phpfile.units[0]
        assert phpunit.name == "return[]->'welcome'"
        assert phpunit.source == "Welcome to our application"
        phpunit = phpfile.units[1]
        assert phpunit.name == "return[]->'apples'"
        assert phpunit.source == multistring(
            ["There is one apple", "There are many apples"]
        )
        assert bytes(phpfile).decode() == phpsource
        phpunit.source = multistring(["There is an apple", "There are many apples"])
        assert bytes(phpfile).decode() == phpsource.replace("one apple", "an apple")
