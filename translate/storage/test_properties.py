
from io import BytesIO

from pytest import raises

from translate.misc.multistring import multistring
from translate.storage import properties, test_monolingual


# Note that DialectJava delimitors are ["=", ":", " "]

def test_find_delimiter_pos_simple():
    """Simple tests to find the various delimiters"""
    assert properties.DialectJava.find_delimiter("key=value") == ('=', 3)
    assert properties.DialectJava.find_delimiter("key:value") == (':', 3)
    assert properties.DialectJava.find_delimiter("key value") == (' ', 3)
    # NOTE this is valid in Java properties, the key is then the empty string
    assert properties.DialectJava.find_delimiter("= value") == ('=', 0)


def test_find_delimiter_pos_multiple():
    """Find delimiters when multiple potential delimiters are involved"""
    assert properties.DialectJava.find_delimiter("key=value:value") == ('=', 3)
    assert properties.DialectJava.find_delimiter("key:value=value") == (':', 3)
    assert properties.DialectJava.find_delimiter("key value=value") == (' ', 3)


def test_find_delimiter_pos_none():
    """Find delimiters when there isn't one"""
    assert properties.DialectJava.find_delimiter("key") == (None, -1)
    assert properties.DialectJava.find_delimiter("key\\=\\:\\ ") == (None, -1)


def test_find_delimiter_pos_whitespace():
    """Find delimiters when whitespace is involved"""
    assert properties.DialectJava.find_delimiter("key = value") == ('=', 4)
    assert properties.DialectJava.find_delimiter("key : value") == (':', 4)
    assert properties.DialectJava.find_delimiter("key   value") == (' ', 3)
    assert properties.DialectJava.find_delimiter("key value = value") == (' ', 3)
    assert properties.DialectJava.find_delimiter("key value value") == (' ', 3)
    assert properties.DialectJava.find_delimiter(" key = value") == ('=', 5)


def test_find_delimiter_pos_escapes():
    """Find delimiters when potential earlier delimiters are escaped"""
    assert properties.DialectJava.find_delimiter("key\\:=value") == ('=', 5)
    assert properties.DialectJava.find_delimiter("key\\=: value") == (':', 5)
    assert properties.DialectJava.find_delimiter("key\\   value") == (' ', 5)
    assert properties.DialectJava.find_delimiter("key\\ key\\ key\\: = value") == ('=', 16)


def test_is_line_continuation():
    assert not properties.is_line_continuation("")
    assert not properties.is_line_continuation("some text")
    assert properties.is_line_continuation("""some text\\""")
    assert not properties.is_line_continuation("""some text\\\\""")  # Escaped \
    assert properties.is_line_continuation("""some text\\\\\\""")  # Odd num. \ is line continuation
    assert properties.is_line_continuation("""\\\\\\""")


def test_key_strip():
    assert properties._key_strip("key") == "key"
    assert properties._key_strip(" key") == "key"
    assert properties._key_strip("\\ key") == "\\ key"
    assert properties._key_strip("key ") == "key"
    assert properties._key_strip("key\\ ") == "key\\ "


def test_is_comment_one_line():
    assert properties.is_comment_one_line("# comment")
    assert properties.is_comment_one_line("! comment")
    assert properties.is_comment_one_line("// comment")
    assert properties.is_comment_one_line("  # comment")
    assert properties.is_comment_one_line("/* comment */")
    assert not properties.is_comment_one_line("not = comment_line /* comment */")
    assert not properties.is_comment_one_line("/* comment ")


def test_is_comment_start():
    assert properties.is_comment_start("/* comment")
    assert not properties.is_comment_start("/* comment */")


def test_is_comment_end():
    assert properties.is_comment_end(" comment */")
    assert not properties.is_comment_end("/* comment */")


class TestPropUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = properties.propunit

    def test_rich_get(self):
        pass

    def test_rich_set(self):
        pass


class TestGwtProp(test_monolingual.TestMonolingualStore):
    StoreClass = properties.gwtfile

    def propparse(self, propsource, personality="gwt", encoding=None, sourcelanguage=None, targetlanguage=None):
        """helper that parses properties source without requiring files"""
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
        """helper that converts properties source to propfile object and back"""
        return self.propparse(propsource).__bytes__()

    def test_simpledefinition(self):
        """checks that a simple properties definition is parsed correctly"""
        propsource = 'test_me=I can code!'
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"

    def test_doubledefinition(self):
        """checks that a double properties definition is parsed correctly"""
        propsource = 'test_me=I can code!\ntest_me[one]=I can code single!'
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source.strings == ["I can code!", "I can code single!"]
        assert propunit.value == ["I can code!", "I can code single!"]
        propunit.value = ["I can code!", "I can code single!"]
        assert propunit.value == ["I can code!", "I can code single!"]

    def test_doubledefinition_source(self):
        """checks that a double properties definition can be regenerated as source"""
        propsource = 'test_me=I can code!\ntest_me[one]=I can code single!'
        propregen = self.propregen(propsource).decode()
        assert propsource + '\n' == propregen

    def test_reduce(self):
        """checks that if the target language has less plural form the generated properties file is correct """
        propsource = 'test_me=I can code!\ntest_me[one]=I can code single!'
        propfile = self.propparse(propsource, "gwt", None, "en", "ja")  # Only "other" plural form
        print(propfile)
        print(str(propfile))
        assert b'test_me=I can code!\n' == propfile.__bytes__()

    def test_increase(self):
        """checks that if the target language has more plural form the generated properties file is correct """
        propsource = 'test_me=I can code!\ntest_me[one]=I can code single!'
        propfile = self.propparse(propsource, "gwt", None, "en", "ar")  # All plural forms
        assert len(propfile.units) == 1
        propunit = propfile.units[0]

        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ['', '', '', '', '', '']
        assert b'test_me=I can code!\ntest_me[none]=\ntest_me[one]=I can code single!\n' + \
               b'test_me[two]=\ntest_me[few]=\ntest_me[many]=\n' == propfile.__bytes__()

        propunit.target = {'other': 'other', 'one': 'one', 'zero': 'zero', 'few': 'few', 'two': 'two', 'many': 'many'}
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ['zero', 'one', 'two', 'few', 'many', 'other']
        assert b'test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n' + \
               b'test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n' == propfile.__bytes__()

        propunit.target = multistring(['zero', 'one', 'two', 'few', 'many', 'other'])
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ['zero', 'one', 'two', 'few', 'many', 'other']
        assert b'test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n' + \
               b'test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n' == propfile.__bytes__()

        propunit.target = ['zero', 'one', 'two', 'few', 'many', 'other']
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ['zero', 'one', 'two', 'few', 'many', 'other']
        assert b'test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n' + \
               b'test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n' == propfile.__bytes__()

        propunit.source = ['zero', 'one', 'two', 'few', 'many', 'other']
        assert isinstance(propunit.target, multistring)
        assert propunit.target.strings == ['zero', 'one', 'two', 'few', 'many', 'other']
        assert b'test_me=other\ntest_me[none]=zero\ntest_me[one]=one\n' + \
               b'test_me[two]=two\ntest_me[few]=few\ntest_me[many]=many\n' == propfile.__bytes__()


class TestProp(test_monolingual.TestMonolingualStore):
    StoreClass = properties.propfile

    def propparse(self, propsource, personality="java", encoding=None):
        """helper that parses properties source without requiring files"""
        dummyfile = BytesIO(propsource.encode() if isinstance(propsource, str) else propsource)
        propfile = properties.propfile(dummyfile, personality, encoding)
        return propfile

    def propregen(self, propsource, encoding=None):
        """helper that converts properties source to propfile object and back"""
        return bytes(self.propparse(propsource, encoding=encoding)).decode('utf-8')

    def test_simpledefinition(self):
        """checks that a simple properties definition is parsed correctly"""
        propsource = 'test_me=I can code!'
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"

    def test_simpledefinition_source(self):
        """checks that a simple properties definition can be regenerated as source"""
        propsource = 'test_me=I can code!'
        propregen = self.propregen(propsource)
        assert propsource + '\n' == propregen

    def test_controlutf8_source(self):
        """checks that a control characters are parsed correctly"""
        propsource = 'test_me=\\\\\\n'
        propregen = self.propregen(propsource, encoding='utf-8')
        assert propsource + '\n' == propregen

    def test_control_source(self):
        """checks that a control characters are parsed correctly"""
        propsource = 'test_me=\\\\\\n'
        propregen = self.propregen(propsource)
        assert propsource + '\n' == propregen

    def test_unicode_escaping(self):
        """check that escaped unicode is converted properly"""
        propsource = "unicode=\u0411\u0416\u0419\u0428"
        messagevalue = '\u0411\u0416\u0419\u0428'.encode("UTF-8")
        propfile = self.propparse(propsource, personality="mozilla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "unicode"
        assert propunit.source == "БЖЙШ"
        regensource = bytes(propfile)
        assert messagevalue in regensource
        assert b"\\" not in regensource

    def test_newlines_startend(self):
        """check that we preserve \n that appear at start and end of properties"""
        propsource = "newlines=\\ntext\\n"
        propregen = self.propregen(propsource)
        assert propsource + '\n' == propregen

    def test_whitespace_handling(self):
        """check that we remove extra whitespace around property"""
        whitespaces = (
            ('key = value', 'key', 'value'),      # Standard for baseline
            (' key =  value', 'key', 'value'),    # Extra \s before key and value
            ('\\ key\\ = value', '\\ key\\ ', 'value'),  # extra space at start and end of key
            ('key = \\ value ', 'key', ' value '),  # extra space at start end end of value
        )
        for propsource, key, value in whitespaces:
            propfile = self.propparse(propsource)
            propunit = propfile.units[0]
            print(repr(propsource), repr(propunit.name), repr(propunit.source))
            assert propunit.name == key
            assert propunit.source == value
            # let's reparse the output to ensure good serialisation->parsing roundtrip:
            propfile = self.propparse(str(propunit))
            propunit = propfile.units[0]
            assert propunit.name == key
            assert propunit.source == value

    def test_key_value_delimiters_simple(self):
        """test that we can handle colon, equals and space delimiter
        between key and value.  We don't test any space removal or escaping"""
        delimiters = [":", "=", " "]
        for delimiter in delimiters:
            propsource = "key%svalue" % delimiter
            print("source: '%s'\ndelimiter: '%s'" % (propsource, delimiter))
            propfile = self.propparse(propsource)
            assert len(propfile.units) == 1
            propunit = propfile.units[0]
            assert propunit.name == "key"
            assert propunit.source == "value"

    def test_comments(self):
        """checks that we handle # and ! comments"""
        markers = ['#', '!']
        for comment_marker in markers:
            propsource = '''%s A comment
key=value
''' % comment_marker
            propfile = self.propparse(propsource)
            print(repr(propsource))
            print("Comment marker: '%s'" % comment_marker)
            assert len(propfile.units) == 1
            propunit = propfile.units[0]
            assert propunit.comments == ['%s A comment' % comment_marker]

    def test_latin1(self):
        """checks that we handle non-escaped latin1 text"""
        prop_source = "key=valú".encode('latin1')
        prop_store = self.propparse(prop_source)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        assert unit.source == "valú"

    def test_fullspec_delimiters(self):
        """test the full definiation as found in Java docs"""
        proplist = ['Truth = Beauty\n', '       Truth:Beauty', 'Truth                  :Beauty', 'Truth        Beauty']
        for propsource in proplist:
            propfile = self.propparse(propsource)
            propunit = propfile.units[0]
            print(propunit)
            assert propunit.name == "Truth"
            assert propunit.source == "Beauty"

    def test_fullspec_escaped_key(self):
        """Escaped delimeters can be in the key"""
        prop_source = "\\:\\="
        prop_store = self.propparse(prop_source)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        print(unit)
        assert unit.name == "\\:\\="

    def test_fullspec_line_continuation(self):
        """Whitespace delimiter and pre whitespace in line continuation are dropped"""
        prop_source = r"""fruits                           apple, banana, pear, \
                                  cantaloupe, watermelon, \
                                  kiwi, mango
"""
        prop_store = self.propparse(prop_source)
        print(prop_store)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        print(unit)
        assert properties.DialectJava.find_delimiter(prop_source) == (' ', 6)
        assert unit.name == "fruits"
        assert unit.source == "apple, banana, pear, cantaloupe, watermelon, kiwi, mango"

    def test_fullspec_key_without_value(self):
        """A key can have no value in which case the value is the empty string"""
        prop_source = "cheeses"
        prop_store = self.propparse(prop_source)
        assert len(prop_store.units) == 1
        unit = prop_store.units[0]
        print(unit)
        assert unit.name == "cheeses"
        assert unit.source == ""

    def test_mac_strings(self):
        """test various items used in Mac OS X strings files"""
        propsource = r'''"I am a \"key\"" = "I am a \"value\"";'''.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'I am a "key"'
        assert propunit.source == 'I am a "value"'

    def test_utf_16_save(self):
        """test saving of utf-16 java properties files"""
        propsource = '''key=zkouška\n'''.encode('utf-16')
        propfile = self.propparse(propsource, personality="java-utf16")
        assert propfile.encoding == 'utf-16'
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.source == 'zkouška'
        assert bytes(propfile) == propsource

    def test_mac_multiline_strings(self):
        """test can read multiline items used in Mac OS X strings files"""
        propsource = (r'''"I am a \"key\"" = "I am a \"value\" ''' +
                      '\n nextline";').encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'I am a "key"'
        assert propunit.source == "I am a \"value\" nextline"

    def test_mac_strings_unicode(self):
        """Ensure we can handle Unicode"""
        propsource = '''"I am a “key”" = "I am a “value”";'''.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'I am a “key”'
        assert propfile.personality.encode(propunit.source) == 'I am a “value”'

    def test_mac_strings_utf8(self):
        """Ensure we can handle Unicode"""
        propsource = '''"I am a “key”" = "I am a “value”";'''.encode('utf-8')
        propfile = self.propparse(propsource, personality="strings-utf8")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'I am a “key”'
        assert propfile.personality.encode(propunit.source) == 'I am a “value”'

    def test_mac_strings_newlines(self):
        """test newlines \n within a strings files"""
        propsource = r'''"key" = "value\nvalue";'''.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.source == 'value\nvalue'
        assert propfile.personality.encode(propunit.source) == r'value\nvalue'

    def test_mac_strings_comments(self):
        """test .string comment types"""
        propsource = '''/* Comment */
// Comment
"key" = "value";'''.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.source == 'value'
        assert propunit.getnotes() == "/* Comment */\n// Comment"

    def test_mac_strings_multilines_comments(self):
        """test .string multiline comments"""
        propsource = ('/* Foo\n'
                      'Bar\n'
                      'Baz */\n'
                      '"key" = "value";').encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.source == 'value'
        assert propunit.getnotes() == "/* Foo\nBar\nBaz */"

    def test_mac_strings_comments_dropping(self):
        """.string generic (and unuseful) comments should be dropped"""
        propsource = '''/* No comment provided by engineer. */
"key" = "value";'''.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.source == 'value'
        assert propunit.getnotes() == ""

    def test_mac_strings_quotes(self):
        """test that parser unescapes characters used as wrappers"""
        propsource = r'"key with \"quotes\"" = "value with \"quotes\"";'.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        propunit = propfile.units[0]
        assert propunit.name == 'key with "quotes"'
        assert propunit.value == 'value with "quotes"'

    def test_mac_strings_equals(self):
        """test that equal signs inside keys/values are not mixed with delimiter"""
        propsource = '"key with = sign" = "value with = sign";'.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        propunit = propfile.units[0]
        assert propunit.name == 'key with = sign'
        assert propunit.value == 'value with = sign'

    def test_mac_strings_serialization(self):
        """test that serializer quotes mac strings properly"""
        propsource = r'"key with \"quotes\"" = "value with \"quotes\"";'.encode('utf-16')
        propfile = self.propparse(propsource, personality="strings")
        # we don't care about leading and trailing newlines and zero bytes
        # in the assert, we just want to make sure that
        # - all quotes are in place
        # - quotes inside are escaped
        # - for the sake of beauty a pair of spaces encloses the equal mark
        # - every line ends with ";"
        assert bytes(propfile).strip(b'\n\x00') == propsource.strip(b'\n\x00')

    def test_override_encoding(self):
        """test that we can override the encoding of a properties file"""
        propsource = "key = value".encode("cp1252")
        propfile = self.propparse(propsource, personality="strings", encoding="cp1252")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.source == 'value'

    def test_trailing_comments(self):
        """test that we handle non-unit data at the end of a file"""
        propsource = "key = value\n# END"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 2
        propunit = propfile.units[1]
        assert propunit.name == ''
        assert propunit.source == ''
        assert propunit.getnotes() == "# END"

    def test_utf16_byte_order_mark(self):
        """test that BOM appears in the resulting text once only"""
        propsource = "key1 = value1\nkey2 = value2\n".encode('utf-16')
        propfile = self.propparse(propsource, encoding='utf-16')
        result = bytes(propfile)
        bom = propsource[:2]
        assert result.startswith(bom)
        assert bom not in result[2:]

    def test_raise_ioerror_if_cannot_detect_encoding(self):
        """Test that IOError is thrown if file encoding cannot be detected."""
        propsource = "key = ąćęłńóśźż".encode("cp1250")
        with raises(IOError):
            self.propparse(propsource, personality="strings")

    def test_utf8_byte_order_mark(self):
        """test that BOM handling works fine with newlines"""
        propsource = "\n\n\nkey1 = value1\n\nkey2 = value2\n".encode('utf-8-sig')
        propfile = self.propparse(propsource, personality='java-utf8')
        bom = propsource[:3]
        result = bytes(propfile)
        assert result.startswith(bom)
        assert bom not in result[3:]
        assert b'None' not in result[3:]

    def test_joomla_set_target(self):
        """test various items used in Joomla files"""
        propsource = '''COM_EXAMPLE_FOO="This is a test"\n'''.encode('utf-8')
        proptarget = '''COM_EXAMPLE_FOO="This is another test"\n'''.encode('utf-8')
        propfile = self.propparse(propsource, personality="joomla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'COM_EXAMPLE_FOO'
        assert propunit.source == 'This is a test'
        assert bytes(propfile) == propsource
        propunit.target = 'This is another test'
        assert bytes(propfile) == proptarget

    def test_joomla(self):
        """test various items used in Joomla files"""
        propsource = '''; comment\nVALUE="I am a "_QQ_"value"_QQ_""\n'''.encode('utf-8')
        propfile = self.propparse(propsource, personality="joomla")
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == 'VALUE'
        assert propunit.source == 'I am a "value"'
        assert bytes(propfile) == propsource

    def test_serialize_missing_delimiter(self):
        propsource = 'key\n'.encode('utf-8')
        propfile = self.propparse(propsource, personality="java-utf8")
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.value == ''
        assert propunit.delimiter == ''
        assert bytes(propfile) == propsource

    def test_serialize_missing_value(self):
        propsource = 'key=\n'.encode('utf-8')
        propfile = self.propparse(propsource, personality="java-utf8")
        propunit = propfile.units[0]
        assert propunit.name == 'key'
        assert propunit.value == ''
        assert bytes(propfile) == propsource

    def test_multi_comments(self):
        propsource = """# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.

# This contains the translations of the module in the default language
# (generally English).

job.log.begin=Starting job of type [{0}]
""".encode('utf-8')
        propfile = self.propparse(propsource, personality="java-utf8")
        assert len(propfile.units) == 2
        propunit = propfile.units[0]
        assert propunit.name == ''
        assert propunit.value == ''
        assert propunit.getnotes() == """# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version."""
        propunit = propfile.units[1]
        assert propunit.name == 'job.log.begin'
        assert propunit.value == 'Starting job of type [{0}]'
        print(bytes(propfile))
        print(propsource)
        assert bytes(propfile) == propsource


class TestXWiki(test_monolingual.TestMonolingualStore):
    StoreClass = properties.xwikifile

    def propparse(self, propsource):
        """helper that parses properties source without requiring files"""
        dummyfile = BytesIO(propsource.encode() if isinstance(propsource, str) else propsource)
        propfile = properties.xwikifile(dummyfile)
        return propfile

    def propregen(self, propsource):
        """helper that converts properties source to propfile object and back"""
        return bytes(self.propparse(propsource)).decode('utf-8')

    def test_simpledefinition(self):
        """checks that a simple properties definition is parsed correctly"""
        propsource = 'test_me=I can code!'
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "I can code!"
        assert not propunit.missing

    def test_missing_definition(self):
        """checks that a simple missing properties definition is parsed correctly"""
        propsource = '### Missing: test_me=I can code!'
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

    def test_missing_definition_source(self):
        propsource = '### Missing: test_me=I can code!'
        propgen = self.propregen(propsource)
        assert propsource + '\n' == propgen

    def test_definition_with_simple_quote(self):
        propsource = 'test_me=A \'quoted\' translation'
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A 'quoted' translation"
        assert not propunit.missing
        assert propunit.getoutput() == propsource + "\n"

    def test_definition_with_simple_quote_and_argument(self):
        propsource = "test_me=A ''quoted'' translation for {0}"
        propfile = self.propparse(propsource)
        assert len(propfile.units) == 1
        propunit = propfile.units[0]
        assert propunit.name == "test_me"
        assert propunit.source == "A 'quoted' translation for {0}"
        assert not propunit.missing
        assert propunit.getoutput() == propsource + "\n"
