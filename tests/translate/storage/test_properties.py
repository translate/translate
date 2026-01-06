import warnings
from io import BytesIO

from pytest import mark, raises

from translate.misc.multistring import multistring
from translate.storage import properties

from . import test_monolingual

# Note that DialectJava delimiters are ["=", ":", " "]


def test_find_delimiter_pos_simple() -> None:
    """Simple tests to find the various delimiters."""
    assert properties.DialectJava.find_delimiter("key=value") == ("=", 3)
    assert properties.DialectJava.find_delimiter("key:value") == (":", 3)
    assert properties.DialectJava.find_delimiter("key value") == (" ", 3)
    # NOTE this is valid in Java properties, the key is then the empty string
    assert properties.DialectJava.find_delimiter("= value") == ("=", 0)


def test_find_delimiter_pos_multiple() -> None:
    """Find delimiters when multiple potential delimiters are involved."""
    assert properties.DialectJava.find_delimiter("key=value:value") == ("=", 3)
    assert properties.DialectJava.find_delimiter("key:value=value") == (":", 3)
    assert properties.DialectJava.find_delimiter("key value=value") == (" ", 3)


def test_find_delimiter_pos_none() -> None:
    """Find delimiters when there isn't one."""
    assert properties.DialectJava.find_delimiter("key") == (None, -1)
    assert properties.DialectJava.find_delimiter("key\\=\\:\\ ") == (None, -1)


def test_find_delimiter_pos_whitespace() -> None:
    """Find delimiters when whitespace is involved."""
    assert properties.DialectJava.find_delimiter("key = value") == ("=", 4)
    assert properties.DialectJava.find_delimiter("key : value") == (":", 4)
    assert properties.DialectJava.find_delimiter("key   value") == (" ", 3)
    assert properties.DialectJava.find_delimiter("key value = value") == (" ", 3)
    assert properties.DialectJava.find_delimiter("key value value") == (" ", 3)
    assert properties.DialectJava.find_delimiter(" key = value") == ("=", 5)


def test_find_delimiter_pos_escapes() -> None:
    """Find delimiters when potential earlier delimiters are escaped."""
    assert properties.DialectJava.find_delimiter("key\\:=value") == ("=", 5)
    assert properties.DialectJava.find_delimiter("key\\=: value") == (":", 5)
    assert properties.DialectJava.find_delimiter("key\\   value") == (" ", 5)
    assert properties.DialectJava.find_delimiter("key\\ key\\ key\\: = value") == (
        "=",
        16,
    )


def test_find_delimiter_pos_empty_and_whitespace() -> None:
    """Test that empty and whitespace-only lines don't cause IndexError."""
    # These should work for DialectJava (no key_wrap_char)
    assert properties.DialectJava.find_delimiter("") == (None, -1)
    assert properties.DialectJava.find_delimiter("   ") == (None, -1)
    assert properties.DialectJava.find_delimiter("\t\t") == (None, -1)

    # These should also work for DialectStrings (has key_wrap_char='"')
    # This was causing IndexError before the fix
    assert properties.DialectStrings.find_delimiter("") == (None, -1)
    assert properties.DialectStrings.find_delimiter("   ") == (None, -1)
    assert properties.DialectStrings.find_delimiter("\t\t") == (None, -1)


def test_is_line_continuation() -> None:
    assert not properties.is_line_continuation("")
    assert not properties.is_line_continuation("some text")
    assert properties.is_line_continuation("""some text\\""")
    assert not properties.is_line_continuation("""some text\\\\""")  # Escaped \
    assert properties.is_line_continuation(
        """some text\\\\\\"""
    )  # Odd num. \ is line continuation
    assert properties.is_line_continuation("""\\\\\\""")


def test_key_strip() -> None:
    assert properties._key_strip("key") == "key"
    assert properties._key_strip(" key") == "key"
    assert properties._key_strip("\\ key") == "\\ key"
    assert properties._key_strip("key ") == "key"
    assert properties._key_strip("key\\ ") == "key\\ "


def test_get_comment_one_line() -> None:
    assert properties.get_comment_one_line("# comment")
    assert properties.get_comment_one_line("! comment")
    assert properties.get_comment_one_line("// comment")
    assert properties.get_comment_one_line("  # comment")
    assert properties.get_comment_one_line("/* comment */")
    assert properties.get_comment_one_line("not = comment_line /* comment */") is None
    assert properties.get_comment_one_line("/* comment ") is None


def test_get_comment_start() -> None:
    assert properties.get_comment_start("/* comment")
    assert properties.get_comment_start("/* comment */") is None


def test_get_comment_end() -> None:
    assert properties.get_comment_end(" comment */")
    assert properties.get_comment_end("/* comment */") is None


class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = properties.propunit

    def test_rich_get(self) -> None:
        pass

    def test_rich_set(self) -> None:
        pass


class TestGwtProp(test_monolingual.TestMonolingualStore):
    StoreClass = properties.gwtfile

    @staticmethod
    def propparse(
        propsource,
        personality="gwt",
        encoding=None,
        sourcelanguage=None,
        targetlanguage=None,
    ):
        """Helper that parses properties source without requiring files."""
        dummyfile = BytesIO(propsource.encode())
        propfile = properties.propfile(None, personality, encoding)
        if sourcelanguage:
            propfile.sourcelanguage = sourcelanguage
        if targetlanguage:
            propfile.targetlanguage = targetlanguage
        propsrc = dummyfile.read()
        dummyfile.close()
        propfile.parse(propsrc)
        propfile.makeindex()
        return propfile

    def propregen(self, propsource):
        """Helper that converts properties source to propfile object and back."""
        return bytes(self.propparse(propsource))

    def test_quotes(self) -> None:
        """Checks that quotes are parsed and saved correctly."""
        propsource = "test_me=I can ''code''!"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can 'code'!"
        propunit.source = "I 'can' code!"
        assert bytes(propfile).decode() == "test_me=I ''can'' code!\n"

    def test_simpledefinition(self) -> None:
        """Checks that a simple properties definition is parsed correctly."""
        propsource = "test_me=I can code!"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"

    def test_doubledefinition(self) -> None:
        """Checks that a double properties definition is parsed correctly."""
        propsource = "test_me=I can code!\ntest_me[one]=I can code single!"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source.strings == ["I can code single!", "I can code!"]
        assert propunit.value == ["I can code!"]
        propunit.value = ["I can code double!", "I can code single!"]
        assert propunit.value == ["I can code double!"]
        assert propunit.source.strings == ["I can code single!", "I can code double!"]
        # propunit.value = ["I can code single!", "I can code!" ]
        # assert propunit.value == ["I can code single!", "I can code!"]

    def test_doubledefinition_source(self) -> None:
        """Checks that a double properties definition can be regenerated as source."""
        propsource = "test_me=I can code!\ntest_me[one]=I can code single!"
        propregen = self.propregen(propsource).decode()
        assert f"{propsource}\n" == propregen

    def test_reduce(self) -> None:
        """Checks that if the target language has less plural form the generated properties file is correct."""
        propsource = "test_me=I can code!\ntest_me[one]=I can code single!"
        propfile = self.propparse(
            propsource, "gwt", None, "en", "ja"
        )  # Only "other" plural form
        print(propfile)
        print(str(propfile))
        assert (bytes(propfile)) == b"test_me=I can code!\n"

    def test_increase(self) -> None:
        """Checks that if the target language has more plural form the generated properties file is correct."""
        propsource = "test_me=I can code!\ntest_me[one]=I can code single!"
        propfile = self.propparse(
            propsource, "gwt", None, "en", "ar"
        )  # All plural forms
        assert len(propfile.units) == 1
        propunit = propfile.units[0]

        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ["", "", "", "", "", ""]
        assert (
            (bytes(propfile))
            == b"test_me=I can code!\ntest_me[none]=\ntest_me[one]=I can code single!\n"
            b"test_me[two]=\ntest_me[few]=\ntest_me[many]=\n"
        )

        propunit.target = {
            "other": "other",
            "one": "one",
            "zero": "zero",
            "few": "few",
            "two": "two",
            "many": "many",
        }
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ["zero", "one", "two", "few", "many", "other"]
        assert (
            (bytes(propfile))
            == b"test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n"
            b"test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n"
        )

        propunit.target = multistring(["zero", "one", "two", "few", "many", "other"])
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ["zero", "one", "two", "few", "many", "other"]
        assert (
            (bytes(propfile))
            == b"test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n"
            b"test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n"
        )

        propunit.target = ["zero", "one", "two", "few", "many", "other"]
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ["zero", "one", "two", "few", "many", "other"]
        assert (
            (bytes(propfile))
            == b"test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n"
            b"test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n"
        )

        propunit.source = ["zero", "one", "two", "few", "many", "other"]
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ["zero", "one", "two", "few", "many", "other"]
        assert (
            (bytes(propfile))
            == b"test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n"
            b"test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n"
        )

    def test_extra_plurals(self) -> None:
        propsource = r"""
userItems.limit = Only {0} items can be added.
userItems.limit[one] = Only one item can be added.
userItems.limit[\=0] = No items can be added.
"""
        propfile = self.propparse(propsource)

        assert len(propfile.units) == 2
        propunit = propfile.units[0]
        assert propunit.name == "userItems.limit"
        assert isinstance(propunit.target, multistring)
        assert propunit.source.strings == [
            "Only one item can be added.",
            "Only {0} items can be added.",
        ]
        propunit = propfile.units[1]
        assert propunit.name == "userItems.limit[\\=0]"
        assert not isinstance(propunit.target, multistring)
        assert propunit.source == "No items can be added."

    def test_non_plurals(self) -> None:
        propsource = r"""Ps[Pd]_unexpected=Test string
PP[]=Other
"""
        propfile = self.propparse(propsource)

        assert len(propfile.units) == 2
        propunit = propfile.units[0]
        assert propunit.name == "Ps[Pd]_unexpected"
        assert propunit.source == "Test string"
        propunit = propfile.units[1]
        assert propunit.name == "PP[]"
        assert propunit.source == "Other"
        assert bytes(propfile).decode() == propsource

    def test_encoding(self) -> None:
        propsource = """test=Zkouška
"""
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test"
        assert propunit.source == "Zkouška"
        assert bytes(propfile).decode() == propsource

        propfile = self.propparse(propsource, encoding="iso-8859-1")
        propfile.encoding = "iso-8859-1"
        propunit = propfile.units[0]
        assert bytes(propfile).decode() == propsource
        propunit.source = "xZkouška"
        assert bytes(propfile).decode() == "test=xZkou\\u0161ka\n"

    def test_other_plurals(self) -> None:
        propsource = r"""userItems.limit=Only X items can be added.
userItems.limit[one]=Only one item can be added.
userItems.limit[few]=Only {0} items can be added.
userItems.limit[many]=Only {0} items can be added.
"""
        propfile = self.propparse(propsource, sourcelanguage="pl", targetlanguage="pl")
        propsource_en = r"""
userItems.test={0} items can be added.
userItems.test[one]=One item can be added.
"""
        propfile_en = self.propparse(
            propsource_en, sourcelanguage="en", targetlanguage="en"
        )

        assert len(propfile_en.units) == 1
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "userItems.limit"
        assert isinstance(propunit.target, multistring)
        assert propunit.source.strings == [
            "Only one item can be added.",
            "Only {0} items can be added.",
            "Only {0} items can be added.",
        ]
        propunit.target = multistring(
            [
                "Only one item can be added.",
                "Only {0} items can be added.",
                "Only many {0} items can be added.",
            ]
        )

        unit = propfile_en.units[0]
        propfile.addunit(unit)
        unit.target = multistring(
            [
                "Only one item can be added.",
                "Only {0} items can be added.",
                "Only many {0} items can be added.",
            ]
        )

        assert (
            bytes(propfile).decode()
            == """userItems.limit=Only many {0} items can be added.
userItems.limit[one]=Only one item can be added.
userItems.limit[few]=Only {0} items can be added.
userItems.limit[many]=Only many {0} items can be added.
userItems.test=Only many {0} items can be added.
userItems.test[one]=Only one item can be added.
userItems.test[few]=Only {0} items can be added.
userItems.test[many]=Only many {0} items can be added.
"""
        )


class TestProp(test_monolingual.TestMonolingualStore):
    StoreClass = properties.propfile

    @staticmethod
    def propparse(propsource, personality="java", encoding=None):
        """Helper that parses properties source without requiring files."""
        dummyfile = BytesIO(
            propsource.encode() if isinstance(propsource, str) else propsource
        )
        return properties.propfile(dummyfile, personality, encoding)

    def propregen(self, propsource, encoding=None):
        """Helper that converts properties source to propfile object and back."""
        return bytes(self.propparse(propsource, encoding=encoding)).decode("utf-8")

    def test_simpledefinition(self) -> None:
        """Checks that a simple properties definition is parsed correctly."""
        propsource = "test_me=I can code!"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"

    def test_simpledefinition_source(self) -> None:
        """Checks that a simple properties definition can be regenerated as source."""
        propsource = "test_me=I can code!"
        propregen = self.propregen(propsource)
        assert f"{propsource}\n" == propregen

    def test_controlutf8_source(self) -> None:
        """Checks that a control characters are parsed correctly."""
        propsource = "test_me=\\\\\\n"
        propregen = self.propregen(propsource, encoding="utf-8")
        assert f"{propsource}\n" == propregen

    def test_control_source(self) -> None:
        """Checks that a control characters are parsed correctly."""
        propsource = "test_me=\\\\\\n"
        propregen = self.propregen(propsource)
        assert f"{propsource}\n" == propregen

    def test_unicode_escaping(self) -> None:
        """Check that escaped unicode is converted properly."""
        propsource = "unicode=\u0411\u0416\u0419\u0428"
        messagevalue = "\u0411\u0416\u0419\u0428".encode()
        propfile = self.propparse(propsource, personality="mozilla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "unicode"
        assert propunit.source == "БЖЙШ"
        regensource = bytes(propfile)
        assert messagevalue in regensource
        assert b"\\" not in regensource

    def test_newlines_startend(self) -> None:
        r"""Check that we preserve \n that appear at start and end of properties."""
        propsource = "newlines=\\ntext\\n"
        propregen = self.propregen(propsource)
        assert f"{propsource}\n" == propregen

    def test_space(self) -> None:
        r"""Check that we preserve \n that appear at start and end of properties."""
        propsource = r"""space=\u0020
endspace=,\u0020
"""
        store = self.propparse(propsource, personality="mozilla")
        assert len(store.units) == 2
        assert store.units[0].source == " "
        assert store.units[1].source == ", "
        store.units[0].source = " "
        store.units[1].source = ", "
        assert bytes(store).decode("utf-8") == propsource

    def test_whitespace_handling(self) -> None:
        """Check that we preserve whitespace in delimiters."""
        whitespaces = (
            (
                # Standard for baseline - whitespace before = is preserved
                "key = value",
                "key",
                "value",
                "key =value\n",
            ),
            (
                # Extra \s before key and value - whitespace before = is preserved
                " key =  value",
                "key",
                "value",
                "key =value\n",
            ),
            (
                # extra space at start and end of key
                "\\ key\\ = value",
                "\\ key\\ ",
                "value",
                "\\ key\\ =value\n",
            ),
            (
                # extra space at start end end of value
                "key = \\ value ",
                "key",
                " value ",
                "key =\\ value \n",
            ),
        )
        for propsource, key, value, expected in whitespaces:
            propfile = self.propparse(propsource)
            propunit = propfile.units[0]
            print(f"{propsource!r}, {propunit.name!r}, {propunit.source!r}")
            assert propunit.name == key
            assert propunit.source == value
            # let's reparse the output to ensure good serialisation->parsing roundtrip:
            propfile = self.propparse(str(propunit))
            propunit = propfile.units[0]
            assert propunit.name == key
            assert propunit.source == value
            propunit.target = value
            assert bytes(propfile).decode() == expected

    def test_key_value_delimiters_simple(self) -> None:
        """
        Test that we can handle colon, equals and space delimiter
        between key and value.  We don't test any space removal or escaping.
        """
        delimiters = [":", "=", " "]
        for delimiter in delimiters:
            propsource = f"key{delimiter}value"
            print(f"source: '{propsource}'\ndelimiter: '{delimiter}'")
            propfile = self.propparse(propsource)
            assert len(propfile.units) == 1
            propunit = propfile.units[0]
            assert propunit.name == "key"
            assert propunit.source == "value"

    def test_tab_delimiters(self) -> None:
        """Test that we handle tab and other whitespace delimiters correctly."""
        # Test tab as delimiter
        propfile = self.propparse("key\tvalue")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.delimiter == "\t"
        assert str(propunit) == "key\tvalue\n"

        # Test tab before equals
        propfile = self.propparse("key\t=   value")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.delimiter == "\t="
        assert str(propunit) == "key\t=value\n"

        # Test multiple tabs
        propfile = self.propparse("key\t\tvalue")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.delimiter == "\t\t"
        assert str(propunit) == "key\t\tvalue\n"

        # Test mixed whitespace
        propfile = self.propparse("key \t value")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.delimiter == " \t "
        assert str(propunit) == "key \t value\n"

    def test_comments(self) -> None:
        """Checks that we handle # and ! comments."""
        markers = ["#", "!"]
        for comment_marker in markers:
            propsource = f"""{comment_marker} A comment
key=value
"""
            propfile = self.propparse(propsource)
            print(repr(propsource))
            print(f"Comment marker: '{comment_marker}'")
            assert len(propfile.units) == 1
            propunit = propfile.units[0]
            assert propunit.comments == [f"{comment_marker} A comment"]

    def test_latin1(self) -> None:
        """Checks that we handle non-escaped latin1 text."""
        prop_source = "key=valú".encode("latin1")
        prop_store = self.propparse(prop_source)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        assert unit.source == "valú"

    def test_fullspec_delimiters(self) -> None:
        """Test the full definition as found in Java docs."""
        proplist = [
            "Truth = Beauty\n",
            "       Truth:Beauty",
            "Truth                  :Beauty",
            "Truth        Beauty",
        ]
        for propsource in proplist:
            propfile = self.propparse(propsource)
            propunit = propfile.units[0]
            print(propunit)
            assert propunit.name == "Truth"
            assert propunit.source == "Beauty"

    def test_fullspec_escaped_key(self) -> None:
        """Escaped delimiters can be in the key."""
        prop_source = "\\:\\="
        prop_store = self.propparse(prop_source)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        print(unit)
        assert unit.name == "\\:\\="

    def test_fullspec_line_continuation(self) -> None:
        """Whitespace delimiter and pre whitespace in line continuation are dropped."""
        prop_source = r"""fruits                           apple, banana, pear, \
                                  cantaloupe, watermelon, \
                                  kiwi, mango
"""
        prop_store = self.propparse(prop_source)
        print(prop_store)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        print(unit)
        assert properties.DialectJava.find_delimiter(prop_source) == (" ", 6)
        assert unit.name == "fruits"
        assert unit.source == "apple, banana, pear, cantaloupe, watermelon, kiwi, mango"

    def test_fullspec_key_without_value(self) -> None:
        """A key can have no value in which case the value is the empty string."""
        prop_source = "cheeses"
        prop_store = self.propparse(prop_source)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        print(unit)
        assert unit.name == "cheeses"
        assert unit.source == ""

    def test_mac_strings(self) -> None:
        """Test various items used in Mac OS X strings files."""
        propsource = r""""I am a \"key\"" = "I am a \"value\"";""".encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'I am a "key"'
        assert propunit.source == 'I am a "value"'

    def test_utf_16_save(self) -> None:
        """Test saving of utf-16 java properties files."""
        propsource = """key=zkouška\n""".encode("utf-16")
        propfile = self.propparse(propsource, personality="java-utf16")
        assert propfile.encoding == "utf-16"
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "zkouška"
        assert bytes(propfile) == propsource

    def test_mac_multiline_strings(self) -> None:
        """Test can read multiline items used in Mac OS X strings files."""
        propsource = (
            """"I am a \\"key\\"" = "I am a \\"value\\" \n nextline";""".encode(
                "utf-16"
            )
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'I am a "key"'
        assert propunit.source == 'I am a "value" nextline'

    def test_mac_strings_unicode(self) -> None:
        """Ensure we can handle Unicode."""
        propsource = """"I am a “key”" = "I am a “value”";""".encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "I am a “key”"
        assert propfile.personality.encode(propunit.source) == "I am a “value”"

    def test_mac_strings_utf8(self) -> None:
        """Ensure we can handle Unicode."""
        propsource = """"I am a “key”" = "I am a “value”";""".encode()
        propfile = self.propparse(propsource, personality="strings-utf8")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "I am a “key”"
        assert propfile.personality.encode(propunit.source) == "I am a “value”"

    def test_mac_strings_newlines(self) -> None:
        r"""Test newlines \n within a strings files."""
        propsource = r""""key" = "value\nvalue";""".encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value\nvalue"
        assert propfile.personality.encode(propunit.source) == r"value\nvalue"

    def test_mac_strings_comments(self) -> None:
        """Test .string comment types."""
        propsource = """/* Comment1 */
// Comment
"key" = "value";""".encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.getnotes() == "Comment1\nComment"

    def test_mac_strings_multilines_comments(self) -> None:
        """Test .string multiline comments."""
        propsource = ("""/* Foo\nBar\nBaz */\n"key" = "value";""").encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.getnotes() == "Foo\nBar\nBaz"

    def test_mac_strings_comments_dropping(self) -> None:
        """.string generic (and unuseful) comments should be dropped."""
        propsource = """/* No comment provided by engineer. */
"key" = "value";""".encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"
        assert propunit.getnotes() == ""

    def test_mac_strings_inline_comments(self) -> None:
        """Test .strings inline comments are parsed correctly."""
        propsource = '"key1"="source_value1"; /*description1*/\n"key2"="source_value2"; /*description2*/\n'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 2

        propunit = propfile.units[0]
        assert propunit.name == "key1"
        assert propunit.source == "source_value1"
        assert propunit.getnotes() == "description1"

        propunit = propfile.units[1]
        assert propunit.name == "key2"
        assert propunit.source == "source_value2"
        assert propunit.getnotes() == "description2"

    def test_mac_strings_inline_comments_nested(self) -> None:
        """Test .strings inline comments with nested /* inside - parsing and round-trip."""
        # Test parsing
        propsource = '"key"="translation"; /* comment with /* in it */\n'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1

        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "translation"
        # Should extract the full comment starting from first /* after semicolon
        assert propunit.getnotes() == "comment with /* in it"

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = '/* comment with /* in it */\n"key" = "translation";\n'
        assert result == expected

    def test_mac_strings_inline_comment_with_spaces(self) -> None:
        """Test .strings inline comments with various spacing - parsing and round-trip."""
        # Test parsing
        propsource = (
            '"key1"="value1";/* no space */\n"key2"="value2";  /* spaces */\n'.encode(
                "utf-16"
            )
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 2

        assert propfile.units[0].source == "value1"
        assert propfile.units[0].getnotes() == "no space"

        assert propfile.units[1].source == "value2"
        assert propfile.units[1].getnotes() == "spaces"

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = (
            '/* no space */\n"key1" = "value1";\n/* spaces */\n"key2" = "value2";\n'
        )
        assert result == expected

    def test_mac_strings_comment_before_entry(self) -> None:
        """Test .strings comment before entry - parsing and round-trip."""
        # Test parsing
        propsource = (
            '/* A comment before the entry */\n"KEY_ONE" = "Value One";\n'.encode(
                "utf-16"
            )
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "KEY_ONE"
        assert propfile.units[0].source == "Value One"
        assert propfile.units[0].getnotes() == "A comment before the entry"

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = '/* A comment before the entry */\n"KEY_ONE" = "Value One";\n'
        assert result == expected

    def test_mac_strings_comment_between_key_and_equals(self) -> None:
        """Test .strings comment between key and equals - parsing and round-trip."""
        # Test parsing
        propsource = '"KEY_TWO" /* A comment between key and equals sign */ = "Value Two";\n'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "KEY_TWO"
        assert propfile.units[0].source == "Value Two"
        assert propfile.units[0].getnotes() == "A comment between key and equals sign"

        # Test round-trip (comment moves to beginning)
        result = bytes(propfile).decode("utf-16")
        expected = (
            '/* A comment between key and equals sign */\n"KEY_TWO" = "Value Two";\n'
        )
        assert result == expected

    def test_mac_strings_comment_between_equals_and_value(self) -> None:
        """Test .strings comment between equals and value - parsing and round-trip."""
        # Test parsing
        propsource = '"KEY_THREE" = /* A comment between equals sign and value */ "Value Three";\n'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "KEY_THREE"
        assert propfile.units[0].source == "Value Three"
        assert propfile.units[0].getnotes() == "A comment between equals sign and value"

        # Test round-trip (comment moves to beginning)
        result = bytes(propfile).decode("utf-16")
        expected = '/* A comment between equals sign and value */\n"KEY_THREE" = "Value Three";\n'
        assert result == expected

    def test_mac_strings_comment_after_value_before_semicolon(self) -> None:
        """Test .strings comment after value before semicolon - parsing and round-trip."""
        # Test parsing
        propsource = '"KEY_FOUR" = "Value Four" /* A comment at the end of the line */;\n'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "KEY_FOUR"
        assert propfile.units[0].source == "Value Four"
        assert propfile.units[0].getnotes() == "A comment at the end of the line"

        # Test round-trip (comment moves to beginning)
        result = bytes(propfile).decode("utf-16")
        expected = (
            '/* A comment at the end of the line */\n"KEY_FOUR" = "Value Four";\n'
        )
        assert result == expected

    def test_mac_strings_multiple_inline_comments(self) -> None:
        """Test .strings multiple entries with inline comments - parsing and round-trip."""
        # Test parsing
        propsource = (
            '"key1" = "value1"; /* comment1 */\n"key2" = "value2"; /* comment2 */\n'
        )
        propfile = self.propparse(propsource.encode("utf-16"), personality="strings")
        assert len(propfile.units) == 2
        assert propfile.units[0].name == "key1"
        assert propfile.units[0].source == "value1"
        assert propfile.units[0].getnotes() == "comment1"
        assert propfile.units[1].name == "key2"
        assert propfile.units[1].source == "value2"
        assert propfile.units[1].getnotes() == "comment2"

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = (
            '/* comment1 */\n"key1" = "value1";\n/* comment2 */\n"key2" = "value2";\n'
        )
        assert result == expected

    def test_mac_strings_nested_comment(self) -> None:
        """Test .strings nested /* in comments - parsing and round-trip."""
        # Test parsing
        propsource = '"key" = "value"; /* comment with /* nested */\n'
        propfile = self.propparse(propsource.encode("utf-16"), personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "key"
        assert propfile.units[0].source == "value"
        assert propfile.units[0].getnotes() == "comment with /* nested"

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = '/* comment with /* nested */\n"key" = "value";\n'
        assert result == expected

    def test_mac_strings_comment_inside_value(self) -> None:
        """Test .strings comment inside quoted value - parsing and round-trip."""
        # Test parsing - comment is part of the value, not a comment
        propsource = '"key" = "value with /* comment */";\n'
        propfile = self.propparse(propsource.encode("utf-16"), personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "key"
        assert propfile.units[0].source == "value with /* comment */"
        assert propfile.units[0].getnotes() == ""

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = '"key" = "value with /* comment */";\n'
        assert result == expected

    def test_mac_strings_trailing_whitespace_after_semicolon(self) -> None:
        """Test .strings with trailing whitespace after semicolon."""
        # Test parsing with trailing spaces after semicolon
        propsource = '"key" = "value";  \n'
        propfile = self.propparse(propsource.encode("utf-16"), personality="strings")
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "key"
        assert propfile.units[0].source == "value"
        assert propfile.units[0].getnotes() == ""

        # Test round-trip
        result = bytes(propfile).decode("utf-16")
        expected = '"key" = "value";\n'
        assert result == expected

    def test_mac_strings_quotes(self) -> None:
        """Test that parser unescapes characters used as wrappers."""
        propsource = r'"key with \"quotes\"" = "value with \"quotes\"";'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        propunit = propfile.units[0]
        assert propunit.name == 'key with "quotes"'
        assert propunit.value == 'value with "quotes"'

    def test_mac_strings_equals(self) -> None:
        """Test that equal signs inside keys/values are not mixed with delimiter."""
        propsource = '"key with = sign" = "value with = sign";'.encode("utf-16")
        propfile = self.propparse(propsource, personality="strings")
        propunit = propfile.units[0]
        assert propunit.name == "key with = sign"
        assert propunit.value == "value with = sign"

    def test_mac_strings_serialization(self) -> None:
        """Test that serializer quotes mac strings properly."""
        propsource = r'"key with \"quotes\"" = "value with \"quotes\"";'.encode(
            "utf-16"
        )
        propfile = self.propparse(propsource, personality="strings")
        # we don't care about leading and trailing newlines and zero bytes
        # in the assert, we just want to make sure that
        # - all quotes are in place
        # - quotes inside are escaped
        # - for the sake of beauty a pair of spaces encloses the equal mark
        # - every line ends with ";"
        assert bytes(propfile).strip(b"\n\x00") == propsource.strip(b"\n\x00")

    def test_mac_strings_double_backslashes(self) -> None:
        """Test that double backslashes are encoded correctly."""
        propsource = (
            r""""key" = "value with \\ signs but also a \n line break";""".encode(
                "utf-16"
            )
        )
        propfile = self.propparse(propsource, personality="strings")
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value with \\ signs but also a \n line break"
        assert (
            propfile.personality.encode(propunit.source)
            == r"value with \\ signs but also a \n line break"
        )

    def test_override_encoding(self) -> None:
        """Test that we can override the encoding of a properties file."""
        propsource = "key = value".encode("cp1252")
        propfile = self.propparse(propsource, personality="strings", encoding="cp1252")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.source == "value"

    def test_trailing_comments(self) -> None:
        """Test that we handle non-unit data at the end of a file."""
        propsource = "key = value\n# END"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 2
        propunit = propfile.units[1]
        assert propunit.name == ""
        assert propunit.source == ""
        assert propunit.getnotes() == "END"

    def test_utf16_byte_order_mark(self) -> None:
        """Test that BOM appears in the resulting text once only."""
        propsource = "key1 = value1\nkey2 = value2\n".encode("utf-16")
        propfile = self.propparse(propsource, encoding="utf-16")
        result = bytes(propfile)
        bom = propsource[:2]
        assert result.startswith(bom)
        assert bom not in result[2:]

    def test_raise_ioerror_if_cannot_detect_encoding(self) -> None:
        """Test that IOError is thrown if file encoding cannot be detected."""
        propsource = "key = ąćęłńóśźż".encode("cp1250")
        with raises(IOError):
            self.propparse(propsource, personality="strings")

    def test_utf8_byte_order_mark(self) -> None:
        """Test that BOM handling works fine with newlines."""
        propsource = "\n\n\nkey1 = value1\n\nkey2 = value2\n".encode("utf-8-sig")
        propfile = self.propparse(propsource, personality="java-utf8")
        bom = propsource[:3]
        result = bytes(propfile)
        assert result.startswith(bom)
        assert bom not in result[3:]
        assert b"None" not in result[3:]

    def test_utf16_bom_no_warning(self) -> None:
        """Test that UTF-16 files with BOM do not trigger encoding warnings."""
        # Test UTF-16 with BOM (typical Mac .strings file)
        propsource = r'"key" = "value";'.encode("utf-16")

        # Parse should not trigger any warnings
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            propfile = self.propparse(propsource, personality="strings")

        # Verify the file was parsed correctly
        assert len(propfile.units) == 1
        assert propfile.units[0].name == "key"
        assert propfile.units[0].source == "value"

    def test_joomla_set_target(self) -> None:
        """Test various items used in Joomla files."""
        propsource = b"""COM_EXAMPLE_FOO="This is a test"\n"""
        proptarget = b"""COM_EXAMPLE_FOO="This is another test"\n"""
        propfile = self.propparse(propsource, personality="joomla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "COM_EXAMPLE_FOO"
        assert propunit.source == "This is a test"
        assert bytes(propfile) == propsource
        propunit.target = "This is another test"
        assert bytes(propfile) == proptarget

    def test_joomla(self) -> None:
        """Test various items used in Joomla files."""
        propsource = b"""; comment\nVALUE="I am a "_QQ_"value"_QQ_""\n"""
        propfile = self.propparse(propsource, personality="joomla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "VALUE"
        assert propunit.source == 'I am a "value"'
        propunit.source = 'I am a "value"'
        assert bytes(propfile) == propsource

    def test_joomla_escape(self) -> None:
        """Test various items used in Joomla files."""
        propsource = b"""; comment\nVALUE="I am a "_QQ_"value"_QQ_"\\n"\n"""
        propfile = self.propparse(propsource, personality="joomla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "VALUE"
        assert propunit.source == 'I am a "value"\n'
        assert bytes(propfile) == propsource

    def test_serialize_missing_delimiter(self) -> None:
        propsource = b"key\n"
        propfile = self.propparse(propsource, personality="java-utf8")
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.value == ""
        assert propunit.delimiter == ""
        assert bytes(propfile) == propsource

    def test_serialize_missing_value(self) -> None:
        propsource = b"key=\n"
        propfile = self.propparse(propsource, personality="java-utf8")
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.value == ""
        assert bytes(propfile) == propsource

    def test_multi_comments(self) -> None:
        propsource = b"""# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.

# This contains the translations of the module in the default language
# (generally English).

job.log.begin=Starting job of type [{0}]
"""
        propfile = self.propparse(propsource, personality="java-utf8")
        assert len(propfile.units) == 2
        propunit = propfile.units[0]
        assert propunit.name == ""
        assert propunit.value == ""
        assert (
            propunit.getnotes()
            == """This is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2.1 of
the License, or (at your option) any later version.
"""
        )
        propunit = propfile.units[1]
        assert propunit.name == "job.log.begin"
        assert propunit.value == "Starting job of type [{0}]"
        print(bytes(propfile))
        print(propsource)
        assert bytes(propfile) == propsource

    def test_serialize_note(self) -> None:
        propsource = b"key=value\n"
        propfile = self.propparse(propsource, personality="java-utf8")
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.value == "value"
        propunit.addnote("note")
        assert (
            bytes(propfile).decode()
            == """// note
key=value
"""
        )
        parsed = self.propparse(bytes(propfile), personality="java-utf8")
        propunit = parsed.units[0]
        assert propunit.name == "key"
        assert propunit.value == "value"
        assert propunit.getnotes() == "note"

    def test_serialize_long_note(self) -> None:
        propsource = b"key=value\n"
        propfile = self.propparse(propsource, personality="java-utf8")
        propunit = propfile.units[0]
        assert propunit.name == "key"
        assert propunit.value == "value"
        propunit.addnote("long\nnote")
        assert (
            bytes(propfile).decode()
            == """/* long
note */
key=value
"""
        )
        parsed = self.propparse(bytes(propfile), personality="java-utf8")
        propunit = parsed.units[0]
        assert propunit.name == "key"
        assert propunit.value == "value"
        assert propunit.getnotes() == "long\nnote"

    def test_trailing_newlines(self) -> None:
        """Ensure we can handle Unicode."""
        propsource = """"I am a “key”" = "I am a “value”";\n"""
        propfile = self.propparse(
            propsource.encode() + b"\n" * 10, personality="strings-utf8"
        )
        assert len(propfile.units) == 1
        assert bytes(propfile).decode() == propsource


class TestXWiki(test_monolingual.TestMonolingualStore):
    StoreClass = properties.xwikifile

    @staticmethod
    def propparse(propsource):
        """Helper that parses properties source without requiring files."""
        dummyfile = BytesIO(
            propsource.encode() if isinstance(propsource, str) else propsource
        )
        return properties.xwikifile(dummyfile)

    def propregen(self, propsource):
        """Helper that converts properties source to propfile object and back."""
        return bytes(self.propparse(propsource)).decode("utf-8")

    def test_simpledefinition(self) -> None:
        """Checks that a simple properties definition is parsed correctly."""
        propsource = "test_me=I can code!"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert not propunit.missing

    def test_missing_definition(self) -> None:
        """Checks that a simple missing properties definition is parsed correctly."""
        propsource = "### Missing: test_me=I can code!"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert propunit.missing
        propunit.target = ""
        assert propunit.missing
        propunit.target = "I can code!"
        assert not propunit.missing
        propunit.target = "Je peux coder"
        assert not propunit.missing
        # Check encoding
        propunit.target = "تىپتىكى خىزمەتنى باشلاش"
        expected_content = (
            "test_me=\\u062A\\u0649\\u067E\\u062A\\u0649\\u0643\\u0649 "
            "\\u062E\\u0649\\u0632\\u0645\\u06D5\\u062A\\u0646\\u0649 "
            "\\u0628\\u0627\\u0634\\u0644\\u0627\\u0634"
        )

        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding)
            == f"{expected_content}\n"
        )

    def test_missing_definition_source(self) -> None:
        propsource = "### Missing: test_me=I can code!"
        propgen = self.propregen(propsource)
        assert f"{propsource}\n" == propgen

    def test_definition_with_simple_quote(self) -> None:
        propsource = "test_me=A 'quoted' translation"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A 'quoted' translation"
        assert not propunit.missing
        assert propunit.getoutput() == f"{propsource}\n"

    def test_definition_with_simple_quote_and_argument(self) -> None:
        propsource = "test_me=A ''quoted'' translation for {0}"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A 'quoted' translation for {0}"
        assert not propunit.missing
        assert propunit.getoutput() == f"{propsource}\n"

    def test_header_preserved(self) -> None:
        propsource = """# -----\n# Header\n# -----\n\ntest_me=I can code"""
        propgen = self.propregen(propsource)
        assert propgen == f"{propsource}\n"

    def test_blank_line_before_comment_preserved(self) -> None:
        propsource = """\n# My comment\ntest_me=I can code"""
        propgen = self.propregen(propsource)
        assert propgen == f"{propsource}\n"

    def test_deprecated_comments_preserved(self) -> None:
        propsource = """# Deprecated keys starts here.
#@deprecatedstart

job.log.label=Job log

#@deprecatedend"""

        propfile = self.propparse(propsource)
        assert len(propfile.units) == 3
        propunit = propfile.units[1]
        assert propunit.name == "job.log.label"
        assert propunit.source == "Job log"
        assert not propunit.missing
        propunit.missing = True
        expected_output = """# Deprecated keys starts here.
#@deprecatedstart

### Missing: job.log.label=Job log

#@deprecatedend
"""
        propgen = bytes(propfile).decode("utf-8")
        assert propgen == expected_output


class TestXWikiPageProperties(test_monolingual.TestMonolingualStore):
    StoreClass = properties.XWikiPageProperties
    FILE_SCHEME = f'{properties.XWikiPageProperties.XML_HEADER}<xwikidoc locale="%(language)s">\n    <translation>1</translation>\n    <language>%(language)s</language>\n    <title/>\n    <content>%(content)s</content>\n</xwikidoc>'

    def getcontent(self, content, language="en"):
        return self.FILE_SCHEME % {"content": f"{content}\n", "language": language}

    @staticmethod
    def propparse(propsource):
        """Helper that parses properties source without requiring files."""
        dummyfile = BytesIO(
            propsource.encode() if isinstance(propsource, str) else propsource
        )
        return properties.XWikiPageProperties(dummyfile)

    def propregen(self, propsource):
        """Helper that converts properties source to propfile object and back."""
        return bytes(self.propparse(propsource)).decode("utf-8")

    def test_simpledefinition(self) -> None:
        """Checks that a simple properties definition is parsed correctly."""
        propsource = self.getcontent("test_me=I can code!")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert not propunit.missing
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{propsource}\n"
        )
        # check translation and language attribute
        propfile.settargetlanguage("fr")
        propunit.target = "Je peux coder"
        expectedcontent = self.getcontent("test_me=Je peux coder", "fr")
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding)
            == f"{expectedcontent}\n"
        )

    def test_missing_definition(self) -> None:
        """Checks that a simple missing properties definition is parsed correctly."""
        propsource = self.getcontent("### Missing: test_me=I can code!")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert propunit.missing
        propunit.target = ""
        assert propunit.missing
        propunit.target = "Je peux coder"
        assert not propunit.missing
        propunit.target = "تىپتىكى خىزمەتنى باشلاش"
        expected_content = self.getcontent("test_me=تىپتىكى خىزمەتنى باشلاش")
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding)
            == f"{expected_content}\n"
        )

    def test_missing_definition_source(self) -> None:
        propsource = self.getcontent("### Missing: test_me=I can code!")
        propgen = self.propregen(propsource)
        assert f"{propsource}\n" == propgen

    def test_definition_with_simple_quote(self) -> None:
        propsource = self.getcontent("test_me=A 'quoted' translation")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A 'quoted' translation"
        assert not propunit.missing
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{propsource}\n"
        )

    def test_definition_with_simple_quote_and_argument(self) -> None:
        propsource = self.getcontent("test_me=A ''quoted'' translation for {0}")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A 'quoted' translation for {0}"
        assert not propunit.missing
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{propsource}\n"
        )

    def test_definition_with_encoded_html(self) -> None:
        propsource = self.getcontent("test_me=A &amp; is represented with &amp;amp;")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A & is represented with &amp;"
        assert not propunit.missing
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{propsource}\n"
        )

    def test_cleaning_attributes(self) -> None:
        """
        Ensure that the XML is correctly formatted during serialization:
        it should not contain objects or attachments tags, and translation should be
        set to 1.
        """
        ## Real XWiki files are containing multiple attributes on xwikidoc tag: we're not testing it there
        ## because ElementTree changed its implementation between Python 3.7 and 3.8 which changed the order of output of the attributes
        ## it makes it more difficult to assert it on multiple versions of Python.
        propsource = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc reference="XWiki.AdminTranslations">
            <web>XWiki</web>
            <name>AdminTranslations</name>
            <language/>
            <defaultLanguage>en</defaultLanguage>
            <translation>0</translation>
            <creator>xwiki:XWiki.Admin</creator>
            <parent>XWiki.WebHome</parent>
            <author>xwiki:XWiki.Admin</author>
            <contentAuthor>xwiki:XWiki.Admin</contentAuthor>
            <version>1.1</version>
            <title>AdminTranslations</title>
            <comment/>
            <minorEdit>false</minorEdit>
            <syntaxId>plain/1.0</syntaxId>
            <hidden>true</hidden>
            <content># Users Section
            test_me=I can code!
            </content>
            <object>
                <name>XWiki.AdminTranslations</name>
                <number>0</number>
                <className>XWiki.TranslationDocumentClass</className>
                <guid>554b2ee4-98dc-48ef-b436-ef0cf7d38c4f</guid>
                <class>
                  <name>XWiki.TranslationDocumentClass</name>
                  <customClass/>
                  <customMapping/>
                  <defaultViewSheet/>
                  <defaultEditSheet/>
                  <defaultWeb/>
                  <nameField/>
                  <validationScript/>
                  <scope>
                    <cache>0</cache>
                    <disabled>0</disabled>
                    <displayType>select</displayType>
                    <freeText>forbidden</freeText>
                    <multiSelect>0</multiSelect>
                    <name>scope</name>
                    <number>1</number>
                    <prettyName>Scope</prettyName>
                    <relationalStorage>0</relationalStorage>
                    <separator> </separator>
                    <separators>|, </separators>
                    <size>1</size>
                    <unmodifiable>0</unmodifiable>
                    <values>GLOBAL|WIKI|USER|ON_DEMAND</values>
                    <classType>com.xpn.xwiki.objects.classes.StaticListClass</classType>
                  </scope>
                </class>
                <property>
                  <scope>WIKI</scope>
                </property>
            </object>
            <attachment>
                <filename>XWikiLogo.png</filename>
                <mimetype>image/png</mimetype>
                <filesize>1390</filesize>
                <author>xwiki:XWiki.Admin</author>
                <version>1.1</version>
                <comment/>
                <content>something=toto</content>
            </attachment>
        </xwikidoc>"""
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        propfile.settargetlanguage("fr")
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert not propunit.missing
        propunit.target = "Je peux coder !"
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        expected_xml = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc reference="XWiki.AdminTranslations" locale="fr">
            <web>XWiki</web>
            <name>AdminTranslations</name>
            <language>fr</language>
            <defaultLanguage>en</defaultLanguage>
            <translation>1</translation>
            <creator>xwiki:XWiki.Admin</creator>
            <parent>XWiki.WebHome</parent>
            <author>xwiki:XWiki.Admin</author>
            <contentAuthor>xwiki:XWiki.Admin</contentAuthor>
            <version>1.1</version>
            <title>AdminTranslations</title>
            <comment/>
            <minorEdit>false</minorEdit>
            <syntaxId>plain/1.0</syntaxId>
            <hidden>true</hidden>
            <content># Users Section
test_me=Je peux coder !
</content>
</xwikidoc>"""
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{expected_xml}\n"
        )
        assert (
            '<?xml version="1.1" encoding="UTF-8"?>\n\n<!--\n * See the NOTICE file distributed with this work for additional'
            in generatedcontent.getvalue().decode(propfile.encoding)
        )

    def test_translate_source(self) -> None:
        """
        Ensure that the XML is correctly formatted during serialization:
        it should not contain objects or attachments tags, and translation should be
        set to 1.
        """
        ## Real XWiki files are containing multiple attributes on xwikidoc tag: we're not testing it there
        ## because ElementTree changed its implementation between Python 3.7 and 3.8 which changed the order of output of the attributes
        ## it makes it more difficult to assert it on multiple versions of Python.
        propsource = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc reference="XWiki.AdminTranslations">
            <web>XWiki</web>
            <name>AdminTranslations</name>
            <language/>
            <defaultLanguage>en</defaultLanguage>
            <translation>0</translation>
            <creator>xwiki:XWiki.Admin</creator>
            <parent>XWiki.WebHome</parent>
            <author>xwiki:XWiki.Admin</author>
            <contentAuthor>xwiki:XWiki.Admin</contentAuthor>
            <version>1.1</version>
            <title>AdminTranslations</title>
            <comment/>
            <minorEdit>false</minorEdit>
            <syntaxId>plain/1.0</syntaxId>
            <hidden>true</hidden>
            <content># Users Section
            test_me=I can code!
            </content>
            <object>
                <name>XWiki.AdminTranslations</name>
                <number>0</number>
                <className>XWiki.TranslationDocumentClass</className>
                <guid>554b2ee4-98dc-48ef-b436-ef0cf7d38c4f</guid>
                <class>
                  <name>XWiki.TranslationDocumentClass</name>
                  <customClass/>
                  <customMapping/>
                  <defaultViewSheet/>
                  <defaultEditSheet/>
                  <defaultWeb/>
                  <nameField/>
                  <validationScript/>
                  <scope>
                    <cache>0</cache>
                    <disabled>0</disabled>
                    <displayType>select</displayType>
                    <freeText>forbidden</freeText>
                    <multiSelect>0</multiSelect>
                    <name>scope</name>
                    <number>1</number>
                    <prettyName>Scope</prettyName>
                    <relationalStorage>0</relationalStorage>
                    <separator> </separator>
                    <separators>|, </separators>
                    <size>1</size>
                    <unmodifiable>0</unmodifiable>
                    <values>GLOBAL|WIKI|USER|ON_DEMAND</values>
                    <classType>com.xpn.xwiki.objects.classes.StaticListClass</classType>
                  </scope>
                </class>
                <property>
                  <scope>WIKI</scope>
                </property>
            </object>
            <attachment>
                <filename>XWikiLogo.png</filename>
                <mimetype>image/png</mimetype>
                <filesize>1390</filesize>
                <author>xwiki:XWiki.Admin</author>
                <version>1.1</version>
                <comment/>
                <content>something=toto</content>
            </attachment>
        </xwikidoc>"""
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        propfile.settargetlanguage("en")
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert not propunit.missing
        propunit.target = "I can change the translation source"
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        expected_xml = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc reference="XWiki.AdminTranslations">
            <web>XWiki</web>
            <name>AdminTranslations</name>
            <language/>
            <defaultLanguage>en</defaultLanguage>
            <translation>0</translation>
            <creator>xwiki:XWiki.Admin</creator>
            <parent>XWiki.WebHome</parent>
            <author>xwiki:XWiki.Admin</author>
            <contentAuthor>xwiki:XWiki.Admin</contentAuthor>
            <version>1.1</version>
            <title>AdminTranslations</title>
            <comment/>
            <minorEdit>false</minorEdit>
            <syntaxId>plain/1.0</syntaxId>
            <hidden>true</hidden>
            <content># Users Section
test_me=I can change the translation source
</content>
            <object>
                <name>XWiki.AdminTranslations</name>
                <number>0</number>
                <className>XWiki.TranslationDocumentClass</className>
                <guid>554b2ee4-98dc-48ef-b436-ef0cf7d38c4f</guid>
                <class>
                  <name>XWiki.TranslationDocumentClass</name>
                  <customClass/>
                  <customMapping/>
                  <defaultViewSheet/>
                  <defaultEditSheet/>
                  <defaultWeb/>
                  <nameField/>
                  <validationScript/>
                  <scope>
                    <cache>0</cache>
                    <disabled>0</disabled>
                    <displayType>select</displayType>
                    <freeText>forbidden</freeText>
                    <multiSelect>0</multiSelect>
                    <name>scope</name>
                    <number>1</number>
                    <prettyName>Scope</prettyName>
                    <relationalStorage>0</relationalStorage>
                    <separator> </separator>
                    <separators>|, </separators>
                    <size>1</size>
                    <unmodifiable>0</unmodifiable>
                    <values>GLOBAL|WIKI|USER|ON_DEMAND</values>
                    <classType>com.xpn.xwiki.objects.classes.StaticListClass</classType>
                  </scope>
                </class>
                <property>
                  <scope>WIKI</scope>
                </property>
            </object>
            <attachment>
                <filename>XWikiLogo.png</filename>
                <mimetype>image/png</mimetype>
                <filesize>1390</filesize>
                <author>xwiki:XWiki.Admin</author>
                <version>1.1</version>
                <comment/>
                <content>something=toto</content>
            </attachment>
        </xwikidoc>"""
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{expected_xml}\n"
        )
        assert (
            '<?xml version="1.1" encoding="UTF-8"?>\n\n<!--\n * See the NOTICE file distributed with this work for additional'
            in generatedcontent.getvalue().decode(propfile.encoding)
        )


class TestXWikiFullPage(test_monolingual.TestMonolingualStore):
    StoreClass = properties.XWikiFullPage
    FILE_SCHEME = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc locale="%(language)s">
    <translation>1</translation>
    <language>%(language)s</language>
    <title>%(title)s</title>
    <content>%(content)s</content>
    </xwikidoc>"""

    def getcontent(self, content, title, language="en"):
        return self.FILE_SCHEME % {
            "content": content,
            "title": title,
            "language": language,
        }

    @staticmethod
    def propparse(propsource):
        """Helper that parses properties source without requiring files."""
        dummyfile = BytesIO(
            propsource.encode() if isinstance(propsource, str) else propsource
        )
        propfile = properties.XWikiFullPage(dummyfile)
        propfile.settargetlanguage("en")
        return propfile

    def propregen(self, propsource):
        """Helper that converts properties source to propfile object and back."""
        return bytes(self.propparse(propsource)).decode("utf-8")

    def test_simpledefinition(self) -> None:
        """Checks that a simple properties definition is parsed correctly."""
        propsource = self.getcontent("I can code!", "This is a title")
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 2
        propunit = propfile.units[0]
        assert propunit.name == "content"
        assert propunit.source == "I can code!"
        assert not propunit.missing
        propunit.target = "A new code!"
        propunit = propfile.units[1]
        assert propunit.name == "title"
        assert propunit.source == "This is a title"
        assert not propunit.missing
        # Check encoding and language attribute
        propfile.settargetlanguage("fr")
        propunit.target = "تىپتىكى خىزمەتنى باشلاش"
        expected_content = self.getcontent(
            "A new code!", "تىپتىكى خىزمەتنى باشلاش", "fr"
        )
        generatedcontent = BytesIO()
        propfile.serialize(generatedcontent)
        assert (
            generatedcontent.getvalue().decode(propfile.encoding)
            == f"{expected_content}\n"
        )

    def test_parse(self) -> None:
        """
        Tests converting to a string and parsing the resulting string.

        In case of an XWiki Full Page new units are ignored
        unless they are using 'content' or 'title' ids.
        """
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        newstore = self.reparse(store)
        assert len(newstore.units) == 0
        unit3 = properties.xwikiunit("Some content")
        unit3.name = "content"
        unit3.target = "Some content"
        store.addunit(unit3)
        unit4 = properties.xwikiunit("A title")
        unit4.name = "title"
        unit4.target = "Specific title"
        store.addunit(unit4)
        store.makeindex()
        newstore = self.reparse(store)
        assert len(newstore.units) == 2
        assert newstore.units[0]._get_source_unit().name == store.units[2].name
        assert newstore.units[0]._get_source_unit().source == store.units[2].target
        assert newstore.units[1]._get_source_unit().name == store.units[3].name
        assert newstore.units[1]._get_source_unit().source == store.units[3].target

    def test_files(self) -> None:
        """
        Tests saving to and loading from files.

        In case of an XWiki Full Page new units are ignored.
        """
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        store.savefile(self.filename)
        newstore = self.StoreClass.parsefile(self.filename)
        assert len(newstore.units) == 0
        unit3 = properties.xwikiunit("Some content")
        unit3.name = "content"
        unit3.target = "Some content"
        store.addunit(unit3)
        unit4 = properties.xwikiunit("A title")
        unit4.name = "title"
        unit4.target = "Specific title"
        store.addunit(unit4)
        store.makeindex()
        store.savefile(self.filename)
        newstore = self.StoreClass.parsefile(self.filename)
        assert len(newstore.units) == 2
        assert newstore.units[0]._get_source_unit().name == store.units[2].name
        assert newstore.units[0]._get_source_unit().source == store.units[2].target
        assert newstore.units[1]._get_source_unit().name == store.units[3].name
        assert newstore.units[1]._get_source_unit().source == store.units[3].target

    def test_save(self) -> None:
        """
        Tests that we can save directly back to the original file.
        In case of an XWiki Full Page new units are ignored.
        """
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit1.target = "Test String"
        unit2 = store.addsourceunit("Test String 2")
        unit2.target = "Test String 2"
        store.savefile(self.filename)
        store.save()
        newstore = self.StoreClass.parsefile(self.filename)
        assert len(newstore.units) == 0
        unit3 = properties.xwikiunit("Some content")
        unit3.name = "content"
        unit3.target = "Some content"
        store.addunit(unit3)
        unit4 = properties.xwikiunit("A title")
        unit4.name = "title"
        unit4.target = "Specific title"
        store.addunit(unit4)
        store.makeindex()
        store.savefile(self.filename)
        store.save()
        newstore = self.StoreClass.parsefile(self.filename)
        assert len(newstore.units) == 2
        assert newstore.units[0]._get_source_unit().name == store.units[2].name
        assert newstore.units[0]._get_source_unit().source == store.units[2].target
        assert newstore.units[1]._get_source_unit().name == store.units[3].name
        assert newstore.units[1]._get_source_unit().source == store.units[3].target

    def test_cleaning_attributes(self) -> None:
        """
        Ensure that the XML is correctly formatted during serialization:
        it should not contain objects or attachments tags, and translation should be
        set to 1.
        """
        ## Real XWiki files are containing multiple attributes on xwikidoc tag: we're not testing it there
        ## because ElementTree changed its implementation between Python 3.7 and 3.8 which changed the order of output of the attributes
        ## it makes it more difficult to assert it on multiple versions of Python.
        propsource = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc reference="XWiki.AdminTranslations">
            <web>XWiki</web>
            <name>AdminTranslations</name>
            <language/>
            <defaultLanguage>en</defaultLanguage>
            <translation>0</translation>
            <creator>xwiki:XWiki.Admin</creator>
            <parent>XWiki.WebHome</parent>
            <author>xwiki:XWiki.Admin</author>
            <contentAuthor>xwiki:XWiki.Admin</contentAuthor>
            <version>1.1</version>
            <title>Some page title</title>
            <comment/>
            <minorEdit>false</minorEdit>
            <syntaxId>plain/1.0</syntaxId>
            <hidden>true</hidden>
            <content>A Lorem Ipsum or whatever might be contained there.

            == A wiki title ==

            Some other stuff.
            </content>
            <object>
                <name>XWiki.AdminTranslations</name>
                <number>0</number>
                <className>XWiki.TranslationDocumentClass</className>
                <guid>554b2ee4-98dc-48ef-b436-ef0cf7d38c4f</guid>
                <class>
                  <name>XWiki.TranslationDocumentClass</name>
                  <customClass/>
                  <customMapping/>
                  <defaultViewSheet/>
                  <defaultEditSheet/>
                  <defaultWeb/>
                  <nameField/>
                  <validationScript/>
                  <scope>
                    <cache>0</cache>
                    <disabled>0</disabled>
                    <displayType>select</displayType>
                    <freeText>forbidden</freeText>
                    <multiSelect>0</multiSelect>
                    <name>scope</name>
                    <number>1</number>
                    <prettyName>Scope</prettyName>
                    <relationalStorage>0</relationalStorage>
                    <separator> </separator>
                    <separators>|, </separators>
                    <size>1</size>
                    <unmodifiable>0</unmodifiable>
                    <values>GLOBAL|WIKI|USER|ON_DEMAND</values>
                    <classType>com.xpn.xwiki.objects.classes.StaticListClass</classType>
                  </scope>
                </class>
                <property>
                  <scope>WIKI</scope>
                </property>
            </object>
            <attachment>
                <filename>XWikiLogo.png</filename>
                <mimetype>image/png</mimetype>
                <filesize>1390</filesize>
                <author>xwiki:XWiki.Admin</author>
                <version>1.1</version>
                <comment/>
                <content>something=toto</content>
            </attachment>
        </xwikidoc>"""
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 2
        propunit = propfile.units[0]
        assert propunit.name == "content"
        assert (
            propunit.source
            == """A Lorem Ipsum or whatever might be contained there.

            == A wiki title ==

            Some other stuff.
            """
        )
        assert not propunit.missing
        propunit.target = """Un Lorem Ipsum ou quoi que ce soit qui puisse être là.

            == Un titre de wiki ==

            D'autres trucs.
            """
        propunit = propfile.units[1]
        assert propunit.name == "title"
        assert propunit.source == "Some page title"
        assert not propunit.missing
        propunit.target = "Un titre de page"

        generatedcontent = BytesIO()
        propfile.settargetlanguage("fr")
        propfile.serialize(generatedcontent)

        expected_xml = f"""{properties.XWikiPageProperties.XML_HEADER}<xwikidoc reference="XWiki.AdminTranslations" locale="fr">
            <web>XWiki</web>
            <name>AdminTranslations</name>
            <language>fr</language>
            <defaultLanguage>en</defaultLanguage>
            <translation>1</translation>
            <creator>xwiki:XWiki.Admin</creator>
            <parent>XWiki.WebHome</parent>
            <author>xwiki:XWiki.Admin</author>
            <contentAuthor>xwiki:XWiki.Admin</contentAuthor>
            <version>1.1</version>
            <title>Un titre de page</title>
            <comment/>
            <minorEdit>false</minorEdit>
            <syntaxId>plain/1.0</syntaxId>
            <hidden>true</hidden>
            <content>Un Lorem Ipsum ou quoi que ce soit qui puisse être là.

            == Un titre de wiki ==

            D'autres trucs.
            </content>
            </xwikidoc>"""
        assert (
            generatedcontent.getvalue().decode(propfile.encoding) == f"{expected_xml}\n"
        )

    @mark.xfail(reason="removal not working in full page")
    def test_remove(self) -> None:
        super().test_remove()
