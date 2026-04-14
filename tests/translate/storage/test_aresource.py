from copy import copy, deepcopy

import pytest
from lxml import etree

from translate.misc.multistring import multistring
from translate.storage import aresource
from translate.storage.base import TranslationStore

from . import test_monolingual


class TestAndroidResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit

    def __check_escape(self, string, xml, target_language=None) -> None:
        """Helper that checks that a string is output with the right escape."""
        unit = self.UnitClass("teststring")

        if target_language is not None:
            store = TranslationStore()
            store.settargetlanguage(target_language)
            unit._store = store

        unit.target = string

        print("unit.target:", repr(unit.target))
        print("xml:", repr(xml))

        assert str(unit) == xml

    def __check_parse(self, string, xml) -> None:
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

    def test_escape_message_with_newline(self) -> None:
        string = "message\nwith newline"
        xml = '<string name="teststring">message\\nwith newline</string>\n'
        self.__check_escape(string, xml)

    def test_escape_quotes_with_newline(self) -> None:
        string = "'message'\nwith newline"
        xml = "<string name=\"teststring\">\\'message\\'\\nwith newline</string>\n"
        self.__check_escape(string, xml)

    def test_escape_message_with_newline_in_xml(self) -> None:
        string = "message\n\nwith newline in xml\n"
        xml = '<string name="teststring">message\\n\\nwith newline in xml\\n</string>\n'
        self.__check_escape(string, xml)

    def test_escape_twitter(self) -> None:
        string = "@twitterescape"
        xml = '<string name="teststring">\\@twitterescape</string>\n'
        self.__check_escape(string, xml)

    def test_escape_quote(self) -> None:
        string = "quote 'escape'"
        xml = "<string name=\"teststring\">quote \\'escape\\'</string>\n"
        self.__check_escape(string, xml)

    def test_escape_question(self) -> None:
        string = "?question?"
        xml = '<string name="teststring">\\?question?</string>\n'
        self.__check_escape(string, xml)

    def test_escape_double_space(self) -> None:
        string = "double  space"
        xml = '<string name="teststring">"double  space"</string>\n'
        self.__check_escape(string, xml)

    def test_escape_leading_space(self) -> None:
        string = " leading space"
        xml = '<string name="teststring">" leading space"</string>\n'
        self.__check_escape(string, xml)

    def test_escape_tailing_space(self) -> None:
        string = "tailing space "
        xml = '<string name="teststring">"tailing space "</string>\n'
        self.__check_escape(string, xml)

    def test_escape_xml_entities(self) -> None:
        string = ">xml&entities"
        xml = '<string name="teststring">&gt;xml&amp;entities</string>\n'
        self.__check_escape(string, xml)

    def test_escape_html_code(self) -> None:
        string = "some <b>html code</b> here"
        xml = '<string name="teststring">some <b>html code</b> here</string>\n'
        self.__check_escape(string, xml)

    def test_escape_html_code_quote(self) -> None:
        string = "some <b>html code</b> 'here'"
        xml = "<string name=\"teststring\">some <b>html code</b> \\'here\\'</string>\n"
        self.__check_escape(string, xml)

    def test_escape_html_code_quote_newline(self) -> None:
        string = "some \n<b>html code</b> 'here'"
        xml = (
            "<string name=\"teststring\">some \\n<b>html code</b> \\'here\\'</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_arrows(self) -> None:
        string = "<<< arrow"
        xml = '<string name="teststring">&lt;&lt;&lt; arrow</string>\n'
        self.__check_escape(string, xml)

    def test_escape_link(self) -> None:
        string = '<a href="http://example.net">link</a>'
        xml = (
            '<string name="teststring">\n'
            '  <a href="http://example.net">link</a>\n'
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_link_and_text(self) -> None:
        string = '<a href="http://example.net">link</a> and text'
        xml = (
            '<string name="teststring"><a href="http://example.net">link'
            "</a> and text</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_blank_string(self) -> None:
        string = ""
        xml = '<string name="teststring"></string>\n'
        self.__check_escape(string, xml)

    def test_plural_escape_message_with_newline(self) -> None:
        mString = multistring(
            ["one message\nwith newline", "other message\nwith newline"]
        )
        xml = (
            '<plurals name="teststring">\n'
            '    <item quantity="one">one message\\nwith newline</item>'
            '<item quantity="other">other message\\nwith newline</item>'
            "</plurals>\n"
        )
        self.__check_escape(mString, xml, "en")

    def test_plural_invalid_lang(self) -> None:
        mString = multistring(["one message", "other message"])
        xml = (
            '<plurals name="teststring">\n'
            '    <item quantity="one">one message</item>'
            '<item quantity="other">other message</item>'
            "</plurals>\n"
        )
        self.__check_escape(mString, xml, "invalid")

    def test_escape_html_quote(self) -> None:
        string = "start 'here' <b>html code 'to escape'</b> also 'here'"
        xml = (
            "<string name=\"teststring\">start \\'here\\' <b>html code \\'to escape\\'</b> also \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_leading_space(self) -> None:
        string = " <b>html code 'to escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"> <b>html code \\'to escape\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_trailing_space(self) -> None:
        string = "<b>html code 'to escape'</b> some 'here' "
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' "
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_with_ampersand(self) -> None:
        string = "<b>html code 'to escape'</b> some 'here' with &amp; char"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' with &amp; char"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_double_space(self) -> None:
        string = "<b>html code 'to  escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to \\u0020escape\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_deep_double_space(self) -> None:
        string = "<b>html code 'to  <i>escape</i>'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to \\u0020<i>escape</i>\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_complex_xml(self) -> None:
        string = '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> &amp; outer &gt; <br/>text'
        xml = (
            '<string name="teststring">'
            '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> &amp; outer &gt; <br/>text'
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_quoted_newlines(self) -> None:
        self.__check_escape(
            "\n\nstring with newlines",
            r"""<string name="teststring">\n\nstring with newlines</string>
""",
        )

    ############################ Check string parse ###########################

    def test_parse_message_with_newline(self) -> None:
        string = "message\nwith newline"
        xml = '<string name="teststring">message\\nwith newline</string>\n'
        self.__check_parse(string, xml)

    def test_parse_message_with_newline_in_xml(self) -> None:
        string = "message \nwith\n newline\n in xml"
        xml = (
            '<string name="teststring">message\n\\nwith\\n\nnewline\\n\nin xml'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_twitter(self) -> None:
        string = "@twitterescape"
        xml = '<string name="teststring">\\@twitterescape</string>\n'
        self.__check_parse(string, xml)

    def test_parse_question(self) -> None:
        string = "?"
        xml = '<string name="question">\\?</string>'
        self.__check_parse(string, xml)

    def test_parse_quote(self) -> None:
        string = "quote 'escape'"
        xml = "<string name=\"teststring\">quote \\'escape\\'</string>\n"
        self.__check_parse(string, xml)

    def test_parse_double_space(self) -> None:
        string = "double  space"
        xml = '<string name="teststring">"double  space"</string>\n'
        self.__check_parse(string, xml)

    def test_parse_leading_space(self) -> None:
        string = " leading space"
        xml = '<string name="teststring">" leading space"</string>\n'
        self.__check_parse(string, xml)

    def test_parse_quoted_newlines(self) -> None:
        self.__check_parse(
            "\n\n\n\nstring with newlines",
            r"""<string name="teststring">"
\n
\nstring with newlines"</string>
""",
        )

    def test_parse_xml_entities(self) -> None:
        string = ">xml&entities"
        xml = '<string name="teststring">&gt;xml&amp;entities</string>\n'
        self.__check_parse(string, xml)

    def test_parse_html_code(self) -> None:
        string = "some <b>html code</b> here"
        xml = '<string name="teststring">some <b>html code</b> here</string>\n'
        self.__check_parse(string, xml)

    def test_parse_escaped_html_code_flag(self) -> None:
        xml = '<string name="teststring">some &lt;b&gt;html code&lt;/b&gt; here</string>\n'
        parser = etree.XMLParser(strip_cdata=False)
        unit = self.UnitClass.createfromxmlElement(etree.fromstring(xml, parser))

        assert unit.target == "some <b>html code</b> here"
        assert unit.target_markup_mode == unit.TARGET_MARKUP_ESCAPED

    def test_parse_escaped_angle_text_flag(self) -> None:
        xml = '<string name="teststring">&lt;not set&gt;</string>\n'
        parser = etree.XMLParser(strip_cdata=False)
        unit = self.UnitClass.createfromxmlElement(etree.fromstring(xml, parser))

        assert unit.target == "<not set>"
        assert unit.target_markup_mode == unit.TARGET_MARKUP_PLAIN

    def test_parse_nested_html_code_flag(self) -> None:
        xml = '<string name="teststring">some <b>html code</b> here</string>\n'
        parser = etree.XMLParser(strip_cdata=False)
        unit = self.UnitClass.createfromxmlElement(etree.fromstring(xml, parser))

        assert unit.target == "some <b>html code</b> here"
        assert unit.target_markup_mode == unit.TARGET_MARKUP_XML

    def test_parse_cdata_flag(self) -> None:
        xml = (
            '<string name="teststring"><![CDATA[<a href="%1$s">Terms</a>]]></string>\n'
        )
        parser = etree.XMLParser(strip_cdata=False)
        unit = self.UnitClass.createfromxmlElement(etree.fromstring(xml, parser))

        assert unit.target == '<a href="%1$s">Terms</a>'
        assert unit.target_markup_mode == unit.TARGET_MARKUP_CDATA

    def test_parse_arrows(self) -> None:
        string = "<<< arrow"
        xml = '<string name="teststring">&lt;&lt;&lt; arrow</string>\n'
        self.__check_parse(string, xml)

    def test_parse_link(self) -> None:
        string = '<a href="http://example.net">link</a>'
        xml = (
            '<string name="teststring"><a href="http://example.net">link</a></string>\n'
        )
        self.__check_parse(string, xml)

    def test_parse_link_and_text(self) -> None:
        string = '<a href="http://example.net">link</a> and text'
        xml = (
            '<string name="teststring"><a href="http://example.net">link'
            "</a> and text</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_blank_string(self) -> None:
        string = ""
        xml = '<string name="teststring"></string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_space(self) -> None:
        string = "test"
        xml = '<string name="teststring">test </string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_spaces(self) -> None:
        string = "test"
        xml = '<string name="teststring">test    </string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_escaped_newline(self) -> None:
        string = "test\n"
        xml = '<string name="teststring">test\\n</string>\n'
        self.__check_parse(string, xml)

    def test_parse_leading_escaped_newline(self) -> None:
        string = "\ntest"
        xml = '<string name="teststring">\\ntest</string>\n'
        self.__check_parse(string, xml)

    def test_parse_leading_spaces(self) -> None:
        string = "test"
        xml = '<string name="teststring">    test</string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_newline(self) -> None:
        string = "test"
        xml = '<string name="teststring">test\n</string>\n'
        self.__check_parse(string, xml)

    def test_parse_many_quotes(self) -> None:
        string = "test"
        xml = '<string name="teststring">""""""""""test"""""""</string>\n'
        self.__check_parse(string, xml)

    def test_parse_blank_string_again(self) -> None:
        string = ""
        xml = '<string name="teststring"/>\n'
        self.__check_parse(string, xml)

    def test_parse_double_quotes_string(self) -> None:
        """Check that double quotes got removed."""
        string = "double quoted text"
        xml = '<string name="teststring">"double quoted text"</string>\n'
        self.__check_parse(string, xml)

    def test_parse_newline_in_string(self) -> None:
        """
        Check that newline is read as space.

        At least it seems to be what Android does.
        """
        string = "newline\nin string"
        xml = '<string name="teststring">newline\\nin string</string>\n'
        self.__check_parse(string, xml)

    def test_parse_not_translatable_string(self) -> None:
        string = "string"
        xml = '<string name="teststring" translatable="false">string</string>\n'
        self.__check_parse(string, xml)

    def test_plural_parse_message_with_newline(self) -> None:
        mString = multistring(
            ["one message\nwith newline", "other message\nwith newline"]
        )
        xml = (
            '<plurals name="teststring">\n'
            '    <item quantity="one">one message\\nwith newline</item>\n'
            '    <item quantity="other">other message\\nwith newline</item>\n'
            "</plurals>\n"
        )
        self.__check_parse(mString, xml)

    def test_plural_parse_message_with_comments(self) -> None:
        mString = multistring(["one message", "other message"])
        xml = (
            '<plurals name="teststring">\n'
            "    <!-- comment of one string -->\n"
            '    <item quantity="one">one message</item>\n'
            "    <!-- comment of other string -->\n"
            '    <item quantity="other">other message</item>\n'
            "</plurals>\n"
        )
        self.__check_parse(mString, xml)

    def test_parse_html_quote(self) -> None:
        string = "start 'here' <b>html code 'to escape'</b> also 'here'"
        xml = (
            "<string name=\"teststring\">start \\'here\\' <b>html code \\'to escape\\'</b> also \\'here\\'"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_leading_space(self) -> None:
        string = "<b>html code 'to escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"> <b>html code \\'to escape\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_leading_space_quoted(self) -> None:
        string = " <b>html code 'to escape'</b> some 'here'"
        xml = (
            '<string name="teststring">" "<b>"html code \'to escape\'"</b>" some \'here\'"'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_trailing_space(self) -> None:
        string = "<b>html code 'to escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' "
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_trailing_space_quoted(self) -> None:
        string = "<b>html code 'to escape'</b> some 'here' "
        xml = (
            '<string name="teststring"><b>"html code \'to escape\'"</b>" some \'here\' "'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_with_ampersand(self) -> None:
        string = "<b>html code 'to escape'</b> some 'here' with &amp; char"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' with &amp; char"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_double_space_quoted(self) -> None:
        string = "<b>html code 'to  escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code 'to \\u0020escape'</b> some 'here'"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_deep_double_space_quoted(self) -> None:
        string = "<b>html code 'to  <i>  escape</i>'</b> some 'here'"
        xml = (
            '<string name="teststring"><b>"html code \'to  "<i>"  escape"</i>\\\'</b> some \\\'here\\\''
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_complex_xml(self) -> None:
        string = '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> outer &amp; text'
        xml = (
            '<string name="teststring">'
            '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> outer &amp; text'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_unicode(self) -> None:
        self.__check_parse("test", r'<string name="test">\utest</string>')
        self.__check_parse("\u0230", r'<string name="test">\u0230</string>')

    def test_single_unescaped(self) -> None:
        string = "a b c d"
        xml = '<string name="teststring">a\nb\tc d</string>'
        self.__check_parse(string, xml)

    def test_single_escaped_alone(self) -> None:
        string = "a\nb\tc d"
        xml = '<string name="teststring">a"\n"b"\t"c" "d</string>'
        self.__check_parse(string, xml)

    def test_single_escaped_full(self) -> None:
        string = "a\nb\tc d"
        xml = '<string name="teststring">"a\nb\tc d"</string>'
        self.__check_parse(string, xml)

    def test_parse_quoted_escaped_percent(self) -> None:
        self.__check_parse(
            """You are about to remove "%s" from your library""",
            r"""<string name="remove_manga">You are about to remove \"%s\" from your library</string>""",
        )

    def test_parse_quoted_percent(self) -> None:
        self.__check_parse(
            """You are about to remove %s from your library""",
            """<string name="remove_manga">You are about to remove "%s" from your library</string>""",
        )

    def test_parse_quoted_quote(self) -> None:
        self.__check_parse(
            """You are about to remove "%s" from your library""",
            r"""<string name="remove_manga">You are about to "remove \"%s\" from" your library</string>""",
        )

    def test_parse_unparied_quote(self) -> None:
        self.__check_parse(
            "You can view it here soon: %s",
            """<string name="cmd_camera_response_success">"You can view it here soon: %s</string>""",
        )
        self.__check_parse(
            "You can view it here soon: %s",
            """<string name="cmd_camera_response_success">You can view it here soon: %s"</string>""",
        )

    def test_parse_escape_slash(self) -> None:
        self.__check_parse(
            """Přechod na novější verzi databáze účtu \\<g id="account">%s</g>\\""",
            r"""<string name="upgrade_database_format">Přechod na novější verzi databáze účtu \\<g id="account">%s</g>\\</string>""",
        )

    def test_parse_escape_ignored(self) -> None:
        self.__check_parse(
            """Přechod na novější verzi databáze účtu \\<g id="account">%s</g>""",
            r"""<string name="upgrade_database_format">Přechod na novější verzi databáze účtu \\<g id="account">%s</g>\x</string>""",
        )

    def test_parse_escaped_quote_end(self) -> None:
        self.__check_parse(
            'No file %1$s found in archive "%2$s"',
            r"""<string name="restore_backup_file_not_found">No file %1$s found in archive \"%2$s\"</string>""",
        )

    def test_parse_quoted_xml(self) -> None:
        self.__check_parse(
            """Your phone needs to use Bluetooth to securely collect and share IDs with other phones that are nearby.

<g example="Corona-Warn">%1$s</g> can notify you if you were exposed to someone who reported to be diagnosed positive.

The date, duration, and signal strength associated with an exposure will be shared with the app.""",
            """<string name="exposure_confirm_start_summary">"Your phone needs to use Bluetooth to securely collect and share IDs with other phones that are nearby.

<g example="Corona-Warn">%1$s</g> can notify you if you were exposed to someone who reported to be diagnosed positive.

The date, duration, and signal strength associated with an exposure will be shared with the app."</string>""",
        )


class TestAndroidResourceFile(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.AndroidResourceFile

    def test_targetlanguage_default_handlings(self) -> None:
        store = self.StoreClass()

        # Initial value is None
        assert store.gettargetlanguage() is None

        # sourcelanguage shouldn't change the targetlanguage
        store.setsourcelanguage("en")
        assert store.gettargetlanguage() is None

        # targetlanguage setter works correctly
        store.settargetlanguage("de")
        assert store.gettargetlanguage() == "de"

        # explicit targetlanguage wins over filename
        store.filename = "dommy/values-it/res.xml"
        assert store.gettargetlanguage() == "de"

    def test_targetlanguage_auto_detection_filename(self) -> None:
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = "project/values-it/res.xml"
        assert store.gettargetlanguage() == "it"

    def test_targetlanguage_auto_detection_filename_default_language(self) -> None:
        store = self.StoreClass()

        store.setsourcelanguage("en")

        # Check language auto_detection
        store.filename = "project/values/res.xml"
        assert store.gettargetlanguage() == "en"

    def test_targetlanguage_auto_detection_invalid_filename(self) -> None:
        store = self.StoreClass()

        store.setsourcelanguage("en")

        store.filename = "project/invalid_directory/res.xml"
        assert store.gettargetlanguage() is None

        store.filename = "invalid_directory"
        assert store.gettargetlanguage() is None

    def test_namespaces(self) -> None:
        content = """<resources xmlns:tools="http://schemas.android.com/tools">
            <string name="string1" tools:ignore="PluralsCandidate">string1</string>
            <string name="string2">string2</string>
        </resources>"""
        store = self.StoreClass()
        store.parse(content)
        newstore = self.StoreClass()
        newstore.addunit(store.units[0], new=True)
        print(newstore)
        assert b'<resources xmlns:tools="http://schemas.android.com/tools">' in bytes(
            newstore
        )

    def test_serialize(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="test">Test</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content

    def test_add_formatting(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="test">Test</string>
</resources>"""
        other = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="other">Test</string>
    <string name="other2">Test</string>
</resources>"""
        expected = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="test">Test</string>
    <string name="other">Test</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)
        otherstore = self.StoreClass()
        otherstore.parse(other)
        store.addunit(otherstore.units[0], True)
        assert bytes(store) == expected

    def test_entity(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY appName "Linphone">
]>
<resources>
    <string name="app_name">&appName;</string>
    <string name="app_core">&appName; Core</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)
        assert store.units[0].source == "&appName;"
        store.units[0].target = "&appName;"
        assert store.units[1].source == "&appName; Core"
        store.units[1].target = "&appName; Core"
        assert bytes(store) == content

    def test_invalid_entity(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY appName "Linphone">
]>
<resources>
    <string name="app_name">&appName;</string>
    <string name="app_core">&appName; Core</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        store.units[0].target = "&appName;"
        store.units[1].target = "&otherName; Core"
        assert bytes(store).decode() == content.replace(
            "&appName; Core", "&amp;otherName; Core"
        )

    def test_quoted_entity_doctype_preserved(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY quoted "a&quot;b&#10;c">
]>
<resources>
    <string name="quoted_value">&quoted;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)
        store.units[0].target = "&quoted;"
        assert bytes(store) == content

    def test_indent(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY url_privacy_policy "http://example.com/">
]>
<resources>
    <string name="privacy_policy"><u><a href="&url_privacy_policy;">Datenschutzerklärung</a></u></string>
</resources>
""".encode()
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content

    def test_edit_plural_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den</item>
        <item quantity="few"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny</item>
        <item quantity="other"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "cs"
        store.parse(content)
        store.units[0].target = multistring(
            [
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den',
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny',
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu',
            ]
        )
        # Additional entry for many (decimal) is present
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den</item>
        <item quantity="few"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny</item>
        <item quantity="many"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
        <item quantity="other"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
    </plurals>
</resources>
"""
        )

    def test_parse_decimal_plurals(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den</item>
        <item quantity="few"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny</item>
        <item quantity="many"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dni</item>
        <item quantity="other"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
    </plurals>
</resources>
"""
        # Resulting parsed plurals are still the same
        store = self.StoreClass()
        store.targetlanguage = "cs"
        store.parse(content)
        assert store.units[0].target == multistring(
            [
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den',
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny',
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu',
            ]
        )

    def test_edit_to_plurals(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="teststring">Test %d string</string>
</resources>
"""
        # Resulting parsed plurals are still the same
        store = self.StoreClass()
        store.targetlanguage = "cs"
        store.parse(content.encode())
        assert store.units[0].target == "Test %d string"
        store.units[0].target = multistring(
            [
                "Test %d string",
                "Test %d strings",
                "Test %d strings",
            ]
        )
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Test %d string</item>
        <item quantity="few">Test %d strings</item>
        <item quantity="many">Test %d strings</item>
        <item quantity="other">Test %d strings</item>
    </plurals>
</resources>
"""
        )

    def entity_add(self, *, edit: bool) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY appName "Zkouška">
]>
<resources>
    <string name="app_name">&appName;</string>
    <string name="app_core">&appName; Core</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        second = self.StoreClass()
        newunit = deepcopy(store.units[0])
        second.addunit(newunit, True)
        if edit:
            newunit.target = "&appName;"
        newunit = deepcopy(store.units[1])
        second.addunit(newunit, True)
        if edit:
            newunit.target = "&appName; Core"
        # The original store should be unchanged
        assert bytes(store).decode() == content
        # The new store should have same content
        assert bytes(second).decode() == content

    def test_entity_add_edit(self) -> None:
        self.entity_add(edit=True)

    def test_entity_add_noedit(self) -> None:
        self.entity_add(edit=False)

    def test_markup_remove(self) -> None:
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="privacy_policy"><u>Datenschutzerklärung</u></string>
</resources>
"""
        content = template.encode("utf-8")
        newcontent = template.replace("<u>", "").replace("</u>", "").encode("utf-8")
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content
        store.units[0].target = "Datenschutzerklärung"
        assert bytes(store) == newcontent

    def test_markup_set(self) -> None:
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!--Multimedia tab-->
    <string name="id">Multimedia tab</string>
</resources>
"""
        content = template.encode("utf-8")
        newcontent = template.replace(">Multimedia tab<", ">Other <b>tab</b><").encode(
            "utf-8"
        )
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content
        store.units[0].target = "Other <b>tab</b>"
        assert bytes(store) == newcontent

    def test_markup_roundtrip_preserves_escaped_html(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        assert store.units[0].target == "Other <b>tab</b>"
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED

        store.units[0].target = "Next <b>tab</b>"
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Next &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        )

    def test_namespaced_markup_roundtrip_preserves_escaped_xml(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <string name="id">&lt;xliff:g&gt;%s&lt;/xliff:g&gt; den</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        assert store.units[0].target == "<xliff:g>%s</xliff:g> den"
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED

        store.units[0].target = store.units[0].target
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <string name="id">&lt;xliff:g&gt;%s&lt;/xliff:g&gt; den</string>
</resources>
"""
        )

    def test_plain_angle_text_noop_edit_roundtrip(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;not set&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        assert store.units[0].target == "<not set>"
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN

        store.units[0].target = store.units[0].target
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;not set&gt;</string>
</resources>
"""
        )

    def test_plain_angle_text_literal_entities_do_not_double_escape(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;not set&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_XML
        store.units[0].target = "&lt;not set&gt;"
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;not set&gt;</string>
</resources>
"""
        )

    def test_plain_angle_text_edit_stays_plain(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;not set&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target = "<b>x</b>"

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;b&gt;x&lt;/b&gt;</string>
</resources>
"""
        )

    def test_target_markup_mode_setter_overrides_to_xml_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_XML
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        store.units[0].target = "Next <b>tab</b>"

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Next <b>tab</b></string>
</resources>
"""
        )

    def test_target_markup_mode_setter_overrides_to_plain(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other <b>tab</b></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_PLAIN
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN
        store.units[0].target = "Next <b>tab</b>"

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Next &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        )

    def test_target_markup_deprecated_getter_alias(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        with pytest.deprecated_call(match="target_markup"):
            assert store.units[0].target_markup is True

        store = self.StoreClass()
        store.parse(
            b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other <b>tab</b></string>
</resources>
"""
        )

        with pytest.deprecated_call(match="target_markup"):
            assert store.units[0].target_markup is False

    def test_target_markup_deprecated_setter_alias_to_xml_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        with pytest.deprecated_call(match="target_markup"):
            store.units[0].target_markup = False
        store.units[0].target = "Next <b>tab</b>"

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Next <b>tab</b></string>
</resources>
"""
        )

    def test_target_markup_deprecated_setter_alias_to_escaped_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other <b>tab</b></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        with pytest.deprecated_call(match="target_markup"):
            store.units[0].target_markup = True
        store.units[0].target = "Next <b>tab</b>"

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Next &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        )

    def test_target_markup_mode_setter_overrides_to_escaped_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other <b>tab</b></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_ESCAPED
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED
        store.units[0].target = "Next <b>tab</b>"

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Next &lt;b&gt;tab&lt;/b&gt;</string>
</resources>
"""
        )

    def test_cdata_roundtrip_preserves_existing_sections(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">By continuing <![CDATA[<a href="%1$s">Terms</a>]]> and <![CDATA[<a href="%2$s">Privacy</a>]]></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA

        store.units[0].target = store.units[0].target
        assert bytes(store) == content

    def test_cdata_roundtrip_decodes_android_escapes(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id"><![CDATA[\\@twitterescape\\nwith newline]]></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        assert store.units[0].target == "@twitterescape\nwith newline"
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA

        store.units[0].target = store.units[0].target
        assert bytes(store) == content

    def test_target_markup_mode_setter_overrides_to_cdata(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other tab</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_CDATA
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA
        store.units[0].target = 'Next <a href="%1$s">tab</a>'

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA
        assert store.units[0].target == 'Next <a href="%1$s">tab</a>'
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id"><![CDATA[Next <a href="%1$s">tab</a>]]></string>
</resources>
"""
        )

    def test_target_markup_mode_setter_to_cdata_applies_android_escaping(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other tab</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_CDATA
        store.units[0].target = "?attr/foo"

        assert store.units[0].target == "?attr/foo"
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id"><![CDATA[\\?attr/foo]]></string>
</resources>
"""
        )

    def test_cdata_mode_setter_overrides_to_plain(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id"><![CDATA[<a href="%1$s">Terms</a>]]></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_PLAIN
        store.units[0].target = '<a href="%1$s">Terms</a>'

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">&lt;a href=\\"%1$s\\"&gt;Terms&lt;/a&gt;</string>
</resources>
"""
        )

    def test_cdata_mode_setter_overrides_to_xml_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id"><![CDATA[<a href="%1$s">Terms</a>]]></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_XML
        store.units[0].target = '<a href="%1$s">Terms</a>'

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id"><a href="%1$s">Terms</a></string>
</resources>
"""
        )

    def test_plural_markup_roundtrip_preserves_escaped_html(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Other &lt;b&gt;tab&lt;/b&gt;</item>
        <item quantity="other">Other &lt;b&gt;tabs&lt;/b&gt;</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        assert store.units[0].target == multistring(
            ["Other <b>tab</b>", "Other <b>tabs</b>"]
        )
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED

        store.units[0].target = multistring(["Next <b>tab</b>", "Next <b>tabs</b>"])
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Next &lt;b&gt;tab&lt;/b&gt;</item>
        <item quantity="other">Next &lt;b&gt;tabs&lt;/b&gt;</item>
    </plurals>
</resources>
"""
        )

    def test_plural_target_markup_mode_setter_overrides_to_xml_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Other &lt;b&gt;tab&lt;/b&gt;</item>
        <item quantity="other">Other &lt;b&gt;tabs&lt;/b&gt;</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_XML
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        store.units[0].target = multistring(["Next <b>tab</b>", "Next <b>tabs</b>"])

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Next <b>tab</b></item>
        <item quantity="other">Next <b>tabs</b></item>
    </plurals>
</resources>
"""
        )

    def test_plural_target_markup_mode_setter_overrides_to_escaped_markup(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Other <b>tab</b></item>
        <item quantity="other">Other <b>tabs</b></item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_ESCAPED
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED
        store.units[0].target = multistring(["Next <b>tab</b>", "Next <b>tabs</b>"])

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_ESCAPED
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Next &lt;b&gt;tab&lt;/b&gt;</item>
        <item quantity="other">Next &lt;b&gt;tabs&lt;/b&gt;</item>
    </plurals>
</resources>
"""
        )

    def test_plural_markup_roundtrip_preserves_cdata(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><![CDATA[<a href="%1$s">Tab</a>]]></item>
        <item quantity="other"><![CDATA[<a href="%1$s">Tabs</a>]]></item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        assert store.units[0].target == multistring(
            ['<a href="%1$s">Tab</a>', '<a href="%1$s">Tabs</a>']
        )
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA

        store.units[0].target = store.units[0].target
        assert bytes(store) == content

    def test_plural_target_markup_mode_setter_overrides_to_cdata(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Other tab</item>
        <item quantity="other">Other tabs</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        store.units[0].target_markup_mode = store.units[0].TARGET_MARKUP_CDATA
        store.units[0].target = multistring(
            ['<a href="%1$s">Tab</a>', '<a href="%1$s">Tabs</a>']
        )

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><![CDATA[<a href="%1$s">Tab</a>]]></item>
        <item quantity="other"><![CDATA[<a href="%1$s">Tabs</a>]]></item>
    </plurals>
</resources>
"""
        )

    def test_mixed_plural_cdata_noop_edit_keeps_target_values(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><![CDATA[<a href="%1$s">Tab</a>]]></item>
        <item quantity="other">Other tabs</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        expected = multistring(['<a href="%1$s">Tab</a>', "Other tabs"])
        assert store.units[0].target == expected
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA

        store.units[0].target = store.units[0].target

        assert store.units[0].target == expected
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><![CDATA[<a href="%1$s">Tab</a>]]></item>
        <item quantity="other"><![CDATA[Other tabs]]></item>
    </plurals>
</resources>
"""
        )

    def test_plural_xml_markup_downgrades_to_plain(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Other <b>tab</b></item>
        <item quantity="other">Other <b>tabs</b></item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "en"
        store.parse(content)

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML

        store.units[0].target = multistring(["Next tab", "Next tabs"])

        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_PLAIN
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one">Next tab</item>
        <item quantity="other">Next tabs</item>
    </plurals>
</resources>
"""
        )

    def test_target_markup_mode_setter_rejects_invalid_value(self) -> None:
        store = self.StoreClass()
        store.parse(
            b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Value</string>
</resources>
"""
        )

        with pytest.raises(ValueError, match="Unsupported target markup mode"):
            store.units[0].target_markup_mode = "unsupported"

    def test_edit_plural_others(self) -> None:
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den</item>
        <item quantity="few"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny</item>
        <item quantity="many"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
        <item quantity="other"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "ru"
        store.parse(content)
        store.units[0].target = multistring(
            [
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den',
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny',
                '<xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu',
            ]
        )
        assert bytes(store) == content

    def test_markup_quotes_set(self) -> None:
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Test</string>
</resources>
"""
        content = template.encode()
        newcontent = template.replace(
            ">Test<", ">Test <b>string</b> with \\u0020space<"
        )
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content
        store.units[0].target = "Test <b>string</b> with  space"
        assert bytes(store).decode() == newcontent

    def test_xliff_g(self) -> None:
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
</resources>"""
        original = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Test: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g></string>
</resources>
"""
        expected = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g></string>
</resources>
"""
        origstore = self.StoreClass()
        origstore.parse(original.encode())
        store = self.StoreClass()
        store.parse(template.encode())
        store.addunit(origstore.units[0], new=True)
        assert bytes(store).decode() == original
        store.units[
            0
        ].target = """Other: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g>"""
        assert bytes(store).decode() == expected

    def test_xliff_namespace(self) -> None:
        original = """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <string name="id">Test</string>
</resources>
"""
        expected = """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <string name="id">Test: <xliff:g>%s</xliff:g></string>
</resources>
"""
        store = self.StoreClass()
        store.parse(original.encode())
        assert bytes(store).decode() == original
        store.units[
            0
        ].target = """Test: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g>"""
        # The namespace should be flattened as it is defined in the toplevel element
        assert bytes(store).decode() == expected

    def test_edit_plural_zh_hk(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "zh-rHK"
        store.parse(content.encode())
        store.units[0].target = "%d 訪客"
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="other">%d 訪客</item>
    </plurals>
</resources>
"""
        )

    def test_edit_plural_b_zh_hk(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "b+zh+Hant+HK"
        store.parse(content.encode())
        store.units[0].target = "%d 訪客"
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="other">%d 訪客</item>
    </plurals>
</resources>
"""
        )

    def test_missing_plural(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "fr"
        store.parse(content.encode())
        assert store.units[0].target == multistring(["%d visitor", "", "%d visitors"])

    def test_partial_plural_roundtrip(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "fr"
        store.parse(content.encode())

        assert store.units[0].target == multistring(["%d visitor", "", "%d visitors"])

        store.units[0].target = store.units[0].target

        assert bytes(store).decode() == content

    def test_partial_plural_setter_omits_empty_translations(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="vms_num_visitors">%d visitors</string>
</resources>
"""
        store = self.StoreClass()
        store.targetlanguage = "fr"
        store.parse(content.encode())

        store.units[0].target = multistring(["%d visiteur", "", "%d visiteurs"])

        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visiteur</item>
        <item quantity="other">%d visiteurs</item>
    </plurals>
</resources>
"""
        )

    def test_empty_missing_plural_tag(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="1" />
    <plurals name="2">
      <item quantity="other">%1$d tiles left in pool.</item>
    </plurals>
    <plurals name="3">
      <item quantity="other">%1$d tiles left in pool.</item>
      <item quantity="one">%1$d tile left in pool.</item>
    </plurals>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert store.units[0].target == multistring(["", ""])
        assert store.units[1].target == multistring(["", "%1$d tiles left in pool."])
        assert store.units[2].target == multistring(
            ["%1$d tile left in pool.", "%1$d tiles left in pool."]
        )

    def test_removeunit(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- First -->
    <string name="test1">Test</string>
    <!-- Second -->
    <string name="test2">Test</string>
    <!-- Third -->
    <string name="test3">Test2</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 3
        assert bytes(store).decode() == content
        store.removeunit(store.units[1])
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- First -->
    <string name="test1">Test</string>
    <!-- Third -->
    <string name="test3">Test2</string>
</resources>
"""
        )

    def test_cdata(self) -> None:
        body = r"""<Data>XXX<b>x</b><![CDATA[
    <html><head>
      <style type=\"text/css\">
        body { margin: 0px; }
      </style></head><body>
      <div style=\"background-color: transparent; color: %1$s; padding:
%2$dpx;\">
        <p>This app requires <strong>permission to access all
files</strong> on the storage.</p>
      </div>
    </body></html>
    ]]></Data>"""
        content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="dialog_storage_permission_info" formatted="false">{body}</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 1
        assert store.units[0].target == body
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_XML
        assert bytes(store).decode() == content
        store.units[0].target = body
        assert bytes(store).decode() == content

    def test_cdata_text(self) -> None:
        body = """By continuing you accept our <![CDATA[<a href="%1$s">Terms of Use</a>]]> and <![CDATA[<a href="%2$s">Privacy Policy</a>]]>"""
        content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="service_terms_agreement_notice">{body}</string>
</resources>
"""

        # Verify round trip
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 1
        assert store.units[0].target == body
        assert store.units[0].target_markup_mode == store.units[0].TARGET_MARKUP_CDATA
        assert bytes(store).decode() == content
        store.units[0].target = body
        assert bytes(store).decode() == content

        # Verify copying unit to new store
        newstore = self.StoreClass()
        newstore.addunit(copy(store.units[0]), new=True)
        assert bytes(newstore).decode() == content
        assert (
            newstore.units[0].target_markup_mode
            == newstore.units[0].TARGET_MARKUP_CDATA
        )
        newstore.units[0].target = body
        assert bytes(newstore).decode() == content

        # Verify creating unit from scratch
        addstore = self.StoreClass()
        unit = addstore.UnitClass(body)
        unit.setid("service_terms_agreement_notice")
        unit.target = body
        addstore.addunit(unit, new=True)
        assert len(addstore.units) == 1
        assert addstore.units[0].target == body
        assert (
            addstore.units[0].target_markup_mode == addstore.units[0].TARGET_MARKUP_XML
        )
        assert bytes(addstore).decode() == content
        addstore.units[0].target = body
        assert bytes(addstore).decode() == content

    def test_prefix(self) -> None:
        body = "&lt; <b>body</b>"
        content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="test">{body}</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 1
        assert store.units[0].target == body
        assert bytes(store).decode() == content

    def test_rtl(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="calendar_permission_required"><i>{app_name}</i> צרכה רשות לגשת ליומן שלך, על מנת ליצור תוכניות עבור עסקאות עתידיות חוזרות.</string>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 1
        assert (
            store.units[0].target
            == "<i>{app_name}</i> צרכה רשות לגשת ליומן שלך, על מנת ליצור תוכניות עבור עסקאות עתידיות חוזרות."
        )

    def test_tail(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="one"><b>One</b></string>in
    <string name="two"><b>Two</b></string>
</resources>"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 2
        assert store.units[0].target == "<b>One</b>"
        assert store.units[1].target == "<b>Two</b>"

    def test_translatable_marking(self) -> None:
        data = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- First -->
    <string name="test1" translateble="true">Test</string>
    <!-- Second -->
    <string name="test2">Test</string>
    <!-- Third -->
    <string name="test3" translatable="false">Test2</string>
</resources>"""
        store = self.StoreClass()
        store.parse(data.encode())
        store.units[1].marktranslatable(False)
        assert store.units[1].getid() == "test2"
        assert not store.units[1].istranslatable()
        store.units[1].marktranslatable(True)
        assert store.units[1].istranslatable()

        store.units[2].marktranslatable(True)
        assert store.units[2].getid() == "test3"
        assert store.units[2].istranslatable()

        store.units[0].marktranslatable(False)
        assert store.units[0].getid() == "test1"
        assert not store.units[0].istranslatable()

    def test_escaping(self) -> None:
        content = r"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<resources>
<string name="hello" weblate-flags="c-format, max-length:100">Hello, world!\n</string>
</resources>"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert len(store.units) == 1
        assert store.units[0].target == "Hello, world!\n"


class TestMOKOResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.MOKOResourceUnit

    def test_escape_quote(self) -> None:
        """Helper that checks that a string is output with the right escape."""
        unit = self.UnitClass("teststring")
        unit.target = '''quoted 'string' and "string"'''

        assert (
            str(unit)
            == """<string name="teststring">quoted 'string' and "string"</string>\n"""
        )


class TestMOKOResourceFile(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.MOKOResourceFile

    def test_plural(self) -> None:
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plural name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plural>
</resources>
"""
        store = self.StoreClass()
        store.parse(content.encode())
        assert store.units[0].target == multistring(["%d visitor", "%d visitors"])
        store = self.StoreClass()
        store.targetlanguage = "zh-rHK"
        store.parse(content.encode())
        store.units[0].target = "%d 訪客"
        assert (
            bytes(store).decode()
            == """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plural name="vms_num_visitors">
        <item quantity="other">%d 訪客</item>
    </plural>
</resources>
"""
        )


class TestCMPResourceUnit(TestMOKOResourceUnit):
    UnitClass = aresource.CMPResourceUnit


class TestCMPResourceFile(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.CMPResourceFile

    def test_quote_escape(self) -> None:
        store = self.StoreClass()

        # Test parsing
        store.parse(
            r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="cloud_changelogScreen_title">Bienvenue dans la version préliminaire de l\'application Efento Cloud</string>
</resources>
""".encode()
        )
        assert len(store.units) == 1
        assert (
            store.units[0].target
            == r"Bienvenue dans la version préliminaire de l\'application Efento Cloud"
        )

        # Test updating
        store.units[
            0
        ].target = "Bienvenue dans la version préliminaire de l'application"
        assert (
            bytes(store).decode()
            == r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="cloud_changelogScreen_title">Bienvenue dans la version préliminaire de l'application</string>
</resources>
"""
        )
        store.units[
            0
        ].target = r"Bienvenue dans la version préliminaire de l\'application"
        assert (
            bytes(store).decode()
            == r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="cloud_changelogScreen_title">Bienvenue dans la version préliminaire de l\\'application</string>
</resources>
"""
        )
