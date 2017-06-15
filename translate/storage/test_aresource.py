# -*- coding: utf-8 -*-

from __future__ import print_function

from lxml import etree

from translate.storage import aresource, test_monolingual
from translate.misc.multistring import multistring
from translate.storage.base import TranslationStore


class TestAndroidResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit

    def __check_escape(self, string, xml, target_language=None):
        """Helper that checks that a string is output with the right escape."""
        unit = self.UnitClass("teststring")

        if (target_language is not None):
            store = TranslationStore()
            store.settargetlanguage(target_language)
            unit._store = store

        unit.target = string

        print("unit.target:", repr(unit.target))
        print("xml:", repr(xml))

        assert str(unit) == xml

    def __check_parse(self, string, xml):
        """Helper that checks that a string is parsed correctly."""
        parser = etree.XMLParser(strip_cdata=False)

        translatable = 'translatable="false"' not in xml
        et = etree.fromstring(xml, parser)
        unit = self.UnitClass.createfromxmlElement(et)

        print("unit.target:", repr(unit.target))
        print("string:", string)
        print("translatable:", repr(unit.istranslatable()))

        assert unit.target == string
        assert unit.istranslatable() == translatable

    ############################ Check string escape ##########################

    def test_escape_message_with_newline(self):
        string = 'message\nwith newline'
        xml = '<string name="teststring">message\n\\nwith newline</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_quotes_with_newline(self):
        string = '\'message\'\nwith newline'
        xml = '<string name="teststring">\\\'message\\\'\n\\nwith newline</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_message_with_newline_in_xml(self):
        string = 'message\n\nwith newline in xml\n'
        xml = ('<string name="teststring">message\n\\n\n\\nwith newline in xml\n\\n'
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_twitter(self):
        string = '@twitterescape'
        xml = '<string name="teststring">\\@twitterescape</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_quote(self):
        string = 'quote \'escape\''
        xml = '<string name="teststring">quote \\\'escape\\\'</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_double_space(self):
        string = 'double  space'
        xml = '<string name="teststring">"double  space"</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_leading_space(self):
        string = ' leading space'
        xml = '<string name="teststring">" leading space"</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_tailing_space(self):
        string = 'tailing space '
        xml = '<string name="teststring">"tailing space "</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_xml_entities(self):
        string = '>xml&entities'
        xml = '<string name="teststring">&gt;xml&amp;entities</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_html_code(self):
        string = 'some <b>html code</b> here'
        xml = ('<string name="teststring">some <b>html code</b> here'
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_code_quote(self):
        string = 'some <b>html code</b> \'here\''
        xml = ('<string name="teststring">some <b>html code</b> \\\'here\\\''
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_code_quote_newline(self):
        string = 'some \n<b>html code</b> \'here\''
        xml = ('<string name="teststring">some \n\\n<b>html code</b> \\\'here\\\''
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_arrows(self):
        string = '<<< arrow'
        xml = '<string name="teststring">&lt;&lt;&lt; arrow</string>\n\n'
        self.__check_escape(string, xml)

    def test_escape_link(self):
        string = '<a href="http://example.net">link</a>'
        xml = ('<string name="teststring">\n'
               '  <a href="http://example.net">link</a>\n'
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_link_and_text(self):
        string = '<a href="http://example.net">link</a> and text'
        xml = ('<string name="teststring"><a href="http://example.net">link'
               '</a> and text</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_blank_string(self):
        string = ''
        xml = '<string name="teststring"></string>\n\n'
        self.__check_escape(string, xml)

    def test_plural_escape_message_with_newline(self):
        mString = multistring(['one message\nwith newline', 'other message\nwith newline'])
        xml = ('<plurals name="teststring">\n\t'
               '<item quantity="one">one message\n\\nwith newline</item>\n\t'
               '<item quantity="other">other message\n\\nwith newline</item>\n'
               '</plurals>\n\n')
        self.__check_escape(mString, xml, 'en')

    def test_plural_invalid_lang(self):
        mString = multistring(['one message', 'other message'])
        xml = ('<plurals name="teststring">\n\t'
               '<item quantity="one">one message</item>\n\t'
               '<item quantity="other">other message</item>\n'
               '</plurals>\n\n')
        self.__check_escape(mString, xml, 'invalid')

    def test_escape_html_quote(self):
        string = 'start \'here\' <b>html code \'to escape\'</b> also \'here\''
        xml = ('<string name="teststring">start \\\'here\\\' <b>html code \\\'to escape\\\'</b> also \\\'here\\\''
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_leading_space(self):
        string = ' <b>html code \'to escape\'</b> some \'here\''
        xml = ('<string name="teststring"> <b>html code \\\'to escape\\\'</b> some \\\'here\\\''
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_trailing_space(self):
        string = '<b>html code \'to escape\'</b> some \'here\' '
        xml = ('<string name="teststring"><b>html code \\\'to escape\\\'</b> some \\\'here\\\' '
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_with_ampersand(self):
        string = '<b>html code \'to escape\'</b> some \'here\' with &amp; char'
        xml = ('<string name="teststring"><b>html code \\\'to escape\\\'</b> some \\\'here\\\' with &amp; char'
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_double_space(self):
        string = '<b>html code \'to  escape\'</b> some \'here\''
        xml = ('<string name="teststring"><b>"html code \\\'to  escape\\\'"</b> some \\\'here\\\''
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_html_deep_double_space(self):
        string = '<b>html code \'to  <i>escape</i>\'</b> some \'here\''
        xml = ('<string name="teststring"><b>"html code \\\'to  "<i>escape</i>\\\'</b> some \\\'here\\\''
               '</string>\n\n')
        self.__check_escape(string, xml)

    def test_escape_complex_xml(self):
        string = '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> &amp; outer &gt; <br/>text'
        xml = ('<string name="teststring">'
               '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> &amp; outer &gt; <br/>text'
               '</string>\n\n')
        self.__check_escape(string, xml)

    ############################ Check string parse ###########################

    def test_parse_message_with_newline(self):
        string = 'message\nwith newline'
        xml = '<string name="teststring">message\\nwith newline</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_message_with_newline_in_xml(self):
        string = 'message \nwith\n newline\n in xml'
        xml = ('<string name="teststring">message\n\\nwith\\n\nnewline\\n\nin xml'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_twitter(self):
        string = '@twitterescape'
        xml = '<string name="teststring">\\@twitterescape</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_quote(self):
        string = 'quote \'escape\''
        xml = '<string name="teststring">quote \\\'escape\\\'</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_double_space(self):
        string = 'double  space'
        xml = '<string name="teststring">"double  space"</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_leading_space(self):
        string = ' leading space'
        xml = '<string name="teststring">" leading space"</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_xml_entities(self):
        string = '>xml&entities'
        xml = '<string name="teststring">&gt;xml&amp;entities</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_html_code(self):
        string = 'some <b>html code</b> here'
        xml = ('<string name="teststring">some <b>html code</b> here'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_arrows(self):
        string = '<<< arrow'
        xml = '<string name="teststring">&lt;&lt;&lt; arrow</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_link(self):
        string = '<a href="http://example.net">link</a>'
        xml = ('<string name="teststring"><a href="http://example.net">link'
               '</a></string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_link_and_text(self):
        string = '<a href="http://example.net">link</a> and text'
        xml = ('<string name="teststring"><a href="http://example.net">link'
               '</a> and text</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_blank_string(self):
        string = ''
        xml = '<string name="teststring"></string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_space(self):
        string = 'test'
        xml = '<string name="teststring">test </string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_spaces(self):
        string = 'test'
        xml = '<string name="teststring">test    </string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_leading_spaces(self):
        string = 'test'
        xml = '<string name="teststring">    test</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_newline(self):
        string = 'test'
        xml = '<string name="teststring">test\n</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_many_quotes(self):
        string = 'test'
        xml = '<string name="teststring">""""""""""test"""""""</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_blank_string_again(self):
        string = ''
        xml = '<string name="teststring"/>\n\n'
        self.__check_parse(string, xml)

    def test_parse_double_quotes_string(self):
        """Check that double quotes got removed."""
        string = 'double quoted text'
        xml = '<string name="teststring">"double quoted text"</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_newline_in_string(self):
        """Check that newline is read as space.

        At least it seems to be what Android does.
        """
        string = 'newline\nin string'
        xml = '<string name="teststring">newline\\nin string</string>\n\n'
        self.__check_parse(string, xml)

    def test_parse_not_translatable_string(self):
        string = 'string'
        xml = ('<string name="teststring" translatable="false">string'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_plural_parse_message_with_newline(self):
        mString = multistring(['one message\nwith newline', 'other message\nwith newline'])
        xml = ('<plurals name="teststring">\n\t'
               '<item quantity="one">one message\\nwith newline</item>\n\t'
               '<item quantity="other">other message\\nwith newline</item>\n\n'
               '</plurals>\n\n')
        self.__check_parse(mString, xml)

    def test_parse_html_quote(self):
        string = 'start \'here\' <b>html code \'to escape\'</b> also \'here\''
        xml = ('<string name="teststring">start \\\'here\\\' <b>html code \\\'to escape\\\'</b> also \\\'here\\\''
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_leading_space(self):
        string = ' <b>html code \'to escape\'</b> some \'here\''
        xml = ('<string name="teststring"> <b>html code \\\'to escape\\\'</b> some \\\'here\\\''
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_leading_space_quoted(self):
        string = ' <b>html code \'to escape\'</b> some \'here\''
        xml = ('<string name="teststring">" "<b>"html code \'to escape\'"</b>" some \'here\'"'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_trailing_space(self):
        string = '<b>html code \'to escape\'</b> some \'here\' '
        xml = ('<string name="teststring"><b>html code \\\'to escape\\\'</b> some \\\'here\\\' '
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_trailing_space_quoted(self):
        string = '<b>html code \'to escape\'</b> some \'here\' '
        xml = ('<string name="teststring"><b>"html code \'to escape\'"</b>" some \'here\' "'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_with_ampersand(self):
        string = '<b>html code \'to escape\'</b> some \'here\' with &amp; char'
        xml = ('<string name="teststring"><b>html code \\\'to escape\\\'</b> some \\\'here\\\' with &amp; char'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_double_space_quoted(self):
        string = '<b>html code \'to  escape\'</b> some \'here\''
        xml = ('<string name="teststring"><b>"html code \'to  escape\'"</b>" some \'here\'"'
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_html_deep_double_space_quoted(self):
        string = '<b>html code \'to  <i>  escape</i>\'</b> some \'here\''
        xml = ('<string name="teststring"><b>"html code \'to  "<i>"  escape"</i>\\\'</b> some \\\'here\\\''
               '</string>\n\n')
        self.__check_parse(string, xml)

    def test_parse_complex_xml(self):
        string = '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> outer &amp; text'
        xml = ('<string name="teststring">'
               '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> outer &amp; text'
               '</string>\n\n')
        self.__check_parse(string, xml)


class TestAndroidResourceFile(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.AndroidResourceFile

    def test_targetlanguage_default_handlings(self):
        store = self.StoreClass()

        # Initial value is None
        assert store.gettargetlanguage() is None

        # sourcelanguage shouldn't change the targetlanguage
        store.setsourcelanguage('en')
        assert store.gettargetlanguage() is None

        # targetlanguage setter works correctly
        store.settargetlanguage('de')
        assert store.gettargetlanguage() == 'de'

        # explicit targetlanguage wins over filename
        store.filename = 'dommy/values-it/res.xml'
        assert store.gettargetlanguage() == 'de'

    def test_targetlanguage_auto_detection_filename(self):
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = 'project/values-it/res.xml'
        assert store.gettargetlanguage() == 'it'

    def test_targetlanguage_auto_detection_filename_default_language(self):
        store = self.StoreClass()

        store.setsourcelanguage('en')

        # Check language auto_detection
        store.filename = 'project/values/res.xml'
        assert store.gettargetlanguage() == 'en'

    def test_targetlanguage_auto_detection_invalid_filename(self):
        store = self.StoreClass()

        store.setsourcelanguage('en')

        store.filename = 'project/invalid_directory/res.xml'
        assert store.gettargetlanguage() is None

        store.filename = 'invalid_directory'
        assert store.gettargetlanguage() is None

    def test_namespaces(self):
        content = '''<resources xmlns:tools="http://schemas.android.com/tools">
            <string name="string1" tools:ignore="PluralsCandidate">string1</string>
            <string name="string2">string2</string>
        </resources>'''
        store = self.StoreClass()
        store.parse(content)
        newstore = self.StoreClass()
        newstore.addunit(store.units[0], new=True)
        print(newstore)
        assert b'<resources xmlns:tools="http://schemas.android.com/tools">' in bytes(newstore)
