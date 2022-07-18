from copy import deepcopy

import pytest
from lxml import etree

from translate.misc.multistring import multistring
from translate.storage import aresource, test_monolingual
from translate.storage.base import TranslationStore


class TestAndroidResourceUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = aresource.AndroidResourceUnit

    def __check_escape(self, string, xml, target_language=None):
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
        string = "message\nwith newline"
        xml = '<string name="teststring">message\n\\nwith newline</string>\n'
        self.__check_escape(string, xml)

    def test_escape_quotes_with_newline(self):
        string = "'message'\nwith newline"
        xml = "<string name=\"teststring\">\\'message\\'\n\\nwith newline</string>\n"
        self.__check_escape(string, xml)

    def test_escape_message_with_newline_in_xml(self):
        string = "message\n\nwith newline in xml\n"
        xml = (
            '<string name="teststring">message\n\\n\n\\nwith newline in xml\n\\n'
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_twitter(self):
        string = "@twitterescape"
        xml = '<string name="teststring">\\@twitterescape</string>\n'
        self.__check_escape(string, xml)

    def test_escape_quote(self):
        string = "quote 'escape'"
        xml = "<string name=\"teststring\">quote \\'escape\\'</string>\n"
        self.__check_escape(string, xml)

    def test_escape_question(self):
        string = "question?"
        xml = '<string name="teststring">question\\?</string>\n'
        self.__check_escape(string, xml)

    def test_escape_double_space(self):
        string = "double  space"
        xml = '<string name="teststring">"double  space"</string>\n'
        self.__check_escape(string, xml)

    def test_escape_leading_space(self):
        string = " leading space"
        xml = '<string name="teststring">" leading space"</string>\n'
        self.__check_escape(string, xml)

    def test_escape_tailing_space(self):
        string = "tailing space "
        xml = '<string name="teststring">"tailing space "</string>\n'
        self.__check_escape(string, xml)

    def test_escape_xml_entities(self):
        string = ">xml&entities"
        xml = '<string name="teststring">&gt;xml&amp;entities</string>\n'
        self.__check_escape(string, xml)

    def test_escape_html_code(self):
        string = "some <b>html code</b> here"
        xml = '<string name="teststring">some <b>html code</b> here' "</string>\n"
        self.__check_escape(string, xml)

    def test_escape_html_code_quote(self):
        string = "some <b>html code</b> 'here'"
        xml = (
            "<string name=\"teststring\">some <b>html code</b> \\'here\\'" "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_code_quote_newline(self):
        string = "some \n<b>html code</b> 'here'"
        xml = (
            "<string name=\"teststring\">some \n\\n<b>html code</b> \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_arrows(self):
        string = "<<< arrow"
        xml = '<string name="teststring">&lt;&lt;&lt; arrow</string>\n'
        self.__check_escape(string, xml)

    def test_escape_link(self):
        string = '<a href="http://example.net">link</a>'
        xml = (
            '<string name="teststring">\n'
            '  <a href="http://example.net">link</a>\n'
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_link_and_text(self):
        string = '<a href="http://example.net">link</a> and text'
        xml = (
            '<string name="teststring"><a href="http://example.net">link'
            "</a> and text</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_blank_string(self):
        string = ""
        xml = '<string name="teststring"></string>\n'
        self.__check_escape(string, xml)

    def test_plural_escape_message_with_newline(self):
        mString = multistring(
            ["one message\nwith newline", "other message\nwith newline"]
        )
        xml = (
            '<plurals name="teststring">\n'
            '    <item quantity="one">one message\n\\nwith newline</item>'
            '<item quantity="other">other message\n\\nwith newline</item>'
            "</plurals>\n"
        )
        self.__check_escape(mString, xml, "en")

    def test_plural_invalid_lang(self):
        mString = multistring(["one message", "other message"])
        xml = (
            '<plurals name="teststring">\n'
            '    <item quantity="one">one message</item>'
            '<item quantity="other">other message</item>'
            "</plurals>\n"
        )
        self.__check_escape(mString, xml, "invalid")

    def test_escape_html_quote(self):
        string = "start 'here' <b>html code 'to escape'</b> also 'here'"
        xml = (
            "<string name=\"teststring\">start \\'here\\' <b>html code \\'to escape\\'</b> also \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_leading_space(self):
        string = " <b>html code 'to escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"> <b>html code \\'to escape\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_trailing_space(self):
        string = "<b>html code 'to escape'</b> some 'here' "
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' "
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_with_ampersand(self):
        string = "<b>html code 'to escape'</b> some 'here' with &amp; char"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' with &amp; char"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_double_space(self):
        string = "<b>html code 'to  escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to \\u0020escape\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_html_deep_double_space(self):
        string = "<b>html code 'to  <i>escape</i>'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to \\u0020<i>escape</i>\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_complex_xml(self):
        string = '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> &amp; outer &gt; <br/>text'
        xml = (
            '<string name="teststring">'
            '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> &amp; outer &gt; <br/>text'
            "</string>\n"
        )
        self.__check_escape(string, xml)

    def test_escape_quoted_newlines(self):
        self.__check_escape(
            "\n\nstring with newlines",
            r"""<string name="teststring">"
\n
\nstring with newlines"</string>
""",
        )

    ############################ Check string parse ###########################

    def test_parse_message_with_newline(self):
        string = "message\nwith newline"
        xml = '<string name="teststring">message\\nwith newline</string>\n'
        self.__check_parse(string, xml)

    def test_parse_message_with_newline_in_xml(self):
        string = "message\nwith\n newline\n in xml"
        xml = (
            '<string name="teststring">message\n\\nwith\\n\nnewline\\n\nin xml'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_twitter(self):
        string = "@twitterescape"
        xml = '<string name="teststring">\\@twitterescape</string>\n'
        self.__check_parse(string, xml)

    def test_parse_question(self):
        string = "?"
        xml = '<string name="question">\\?</string>'
        self.__check_parse(string, xml)

    def test_parse_quote(self):
        string = "quote 'escape'"
        xml = "<string name=\"teststring\">quote \\'escape\\'</string>\n"
        self.__check_parse(string, xml)

    def test_parse_double_space(self):
        string = "double  space"
        xml = '<string name="teststring">"double  space"</string>\n'
        self.__check_parse(string, xml)

    def test_parse_leading_space(self):
        string = " leading space"
        xml = '<string name="teststring">" leading space"</string>\n'
        self.__check_parse(string, xml)

    def test_parse_quoted_newlines(self):
        self.__check_parse(
            "\n\nstring with newlines",
            r"""<string name="teststring">"
\n
\nstring with newlines"</string>
""",
        )

    def test_parse_xml_entities(self):
        string = ">xml&entities"
        xml = '<string name="teststring">&gt;xml&amp;entities</string>\n'
        self.__check_parse(string, xml)

    def test_parse_html_code(self):
        string = "some <b>html code</b> here"
        xml = '<string name="teststring">some <b>html code</b> here' "</string>\n"
        self.__check_parse(string, xml)

    def test_parse_arrows(self):
        string = "<<< arrow"
        xml = '<string name="teststring">&lt;&lt;&lt; arrow</string>\n'
        self.__check_parse(string, xml)

    def test_parse_link(self):
        string = '<a href="http://example.net">link</a>'
        xml = (
            '<string name="teststring"><a href="http://example.net">link'
            "</a></string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_link_and_text(self):
        string = '<a href="http://example.net">link</a> and text'
        xml = (
            '<string name="teststring"><a href="http://example.net">link'
            "</a> and text</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_blank_string(self):
        string = ""
        xml = '<string name="teststring"></string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_space(self):
        string = "test"
        xml = '<string name="teststring">test </string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_spaces(self):
        string = "test"
        xml = '<string name="teststring">test    </string>\n'
        self.__check_parse(string, xml)

    def test_parse_leading_spaces(self):
        string = "test"
        xml = '<string name="teststring">    test</string>\n'
        self.__check_parse(string, xml)

    def test_parse_trailing_newline(self):
        string = "test"
        xml = '<string name="teststring">test\n</string>\n'
        self.__check_parse(string, xml)

    def test_parse_many_quotes(self):
        string = "test"
        xml = '<string name="teststring">""""""""""test"""""""</string>\n'
        self.__check_parse(string, xml)

    def test_parse_blank_string_again(self):
        string = ""
        xml = '<string name="teststring"/>\n'
        self.__check_parse(string, xml)

    def test_parse_double_quotes_string(self):
        """Check that double quotes got removed."""
        string = "double quoted text"
        xml = '<string name="teststring">"double quoted text"</string>\n'
        self.__check_parse(string, xml)

    def test_parse_newline_in_string(self):
        """Check that newline is read as space.

        At least it seems to be what Android does.
        """
        string = "newline\nin string"
        xml = '<string name="teststring">newline\\nin string</string>\n'
        self.__check_parse(string, xml)

    def test_parse_not_translatable_string(self):
        string = "string"
        xml = '<string name="teststring" translatable="false">string' "</string>\n"
        self.__check_parse(string, xml)

    def test_plural_parse_message_with_newline(self):
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

    def test_plural_parse_message_with_comments(self):
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

    def test_parse_html_quote(self):
        string = "start 'here' <b>html code 'to escape'</b> also 'here'"
        xml = (
            "<string name=\"teststring\">start \\'here\\' <b>html code \\'to escape\\'</b> also \\'here\\'"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_leading_space(self):
        string = " <b>html code 'to escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"> <b>html code \\'to escape\\'</b> some \\'here\\'"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_leading_space_quoted(self):
        string = " <b>html code 'to escape'</b> some 'here'"
        xml = (
            '<string name="teststring">" "<b>"html code \'to escape\'"</b>" some \'here\'"'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_trailing_space(self):
        string = "<b>html code 'to escape'</b> some 'here' "
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' "
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_trailing_space_quoted(self):
        string = "<b>html code 'to escape'</b> some 'here' "
        xml = (
            '<string name="teststring"><b>"html code \'to escape\'"</b>" some \'here\' "'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_with_ampersand(self):
        string = "<b>html code 'to escape'</b> some 'here' with &amp; char"
        xml = (
            "<string name=\"teststring\"><b>html code \\'to escape\\'</b> some \\'here\\' with &amp; char"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_double_space_quoted(self):
        string = "<b>html code 'to  escape'</b> some 'here'"
        xml = (
            "<string name=\"teststring\"><b>html code 'to \\u0020escape'</b> some 'here'"
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_html_deep_double_space_quoted(self):
        string = "<b>html code 'to  <i>  escape</i>'</b> some 'here'"
        xml = (
            '<string name="teststring"><b>"html code \'to  "<i>"  escape"</i>\\\'</b> some \\\'here\\\''
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_complex_xml(self):
        string = '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> outer &amp; text'
        xml = (
            '<string name="teststring">'
            '<g:test xmlns:g="ttt" g:somevalue="aaaa  &quot;  aaa">value</g:test> outer &amp; text'
            "</string>\n"
        )
        self.__check_parse(string, xml)

    def test_parse_unicode(self):
        with pytest.raises(ValueError):
            self.__check_parse("", r'<string name="test">\utest</string>')
        self.__check_parse("\u0230", r'<string name="test">\u0230</string>')


class TestAndroidResourceFile(test_monolingual.TestMonolingualStore):
    StoreClass = aresource.AndroidResourceFile

    def test_targetlanguage_default_handlings(self):
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

    def test_targetlanguage_auto_detection_filename(self):
        store = self.StoreClass()

        # Check language auto_detection
        store.filename = "project/values-it/res.xml"
        assert store.gettargetlanguage() == "it"

    def test_targetlanguage_auto_detection_filename_default_language(self):
        store = self.StoreClass()

        store.setsourcelanguage("en")

        # Check language auto_detection
        store.filename = "project/values/res.xml"
        assert store.gettargetlanguage() == "en"

    def test_targetlanguage_auto_detection_invalid_filename(self):
        store = self.StoreClass()

        store.setsourcelanguage("en")

        store.filename = "project/invalid_directory/res.xml"
        assert store.gettargetlanguage() is None

        store.filename = "invalid_directory"
        assert store.gettargetlanguage() is None

    def test_namespaces(self):
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

    def test_serialize(self):
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="test">Test</string>
</resources>"""
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content

    def test_add_formatting(self):
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
</resources>"""
        store = self.StoreClass()
        store.parse(content)
        otherstore = self.StoreClass()
        otherstore.parse(other)
        store.addunit(otherstore.units[0], True)
        assert bytes(store) == expected

    def test_entity(self):
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY appName "Linphone">
]>
<resources>
    <string name="app_name">&appName;</string>
    <string name="app_core">&appName; Core</string>
</resources>"""
        store = self.StoreClass()
        store.parse(content)
        assert store.units[0].source == "&appName;"
        store.units[0].target = "&appName;"
        assert store.units[1].source == "&appName; Core"
        store.units[1].target = "&appName; Core"
        assert bytes(store) == content

    def test_invalid_entity(self):
        content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY appName "Linphone">
]>
<resources>
    <string name="app_name">&appName;</string>
    <string name="app_core">&appName; Core</string>
</resources>"""
        store = self.StoreClass()
        store.parse(content.encode())
        store.units[0].target = "&appName;"
        store.units[1].target = "&otherName; Core"
        assert bytes(store).decode() == content.replace(
            "&appName; Core", "&amp;otherName; Core"
        )

    def test_indent(self):
        content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY url_privacy_policy "http://example.com/">
]>
<resources>
    <string name="privacy_policy"><u><a href="&url_privacy_policy;">Datenschutzerklärung</a></u></string>
</resources>""".encode()
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content

    def test_edit_plural_markup(self):
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den</item>
        <item quantity="few"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny</item>
        <item quantity="other"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
    </plurals>
</resources>"""
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
        assert bytes(store) == content

    def test_entity_add(self, edit=True):
        content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE resources [
<!ENTITY appName "Zkouška">
]>
<resources>
    <string name="app_name">&appName;</string>
    <string name="app_core">&appName; Core</string>
</resources>"""
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

    def test_entity_add_noedit(self):
        self.test_entity_add(edit=False)

    def test_markup_remove(self):
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="privacy_policy"><u>Datenschutzerklärung</u></string>
</resources>"""
        content = template.encode("utf-8")
        newcontent = template.replace("<u>", "").replace("</u>", "").encode("utf-8")
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content
        store.units[0].target = "Datenschutzerklärung"
        assert bytes(store) == newcontent

    def test_markup_set(self):
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!--Multimedia tab-->
    <string name="id">Multimedia tab</string>
</resources>"""
        content = template.encode("utf-8")
        newcontent = template.replace(">Multimedia tab<", ">Other <b>tab</b><").encode(
            "utf-8"
        )
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content
        store.units[0].target = "Other <b>tab</b>"
        assert bytes(store) == newcontent

    def test_edit_plural_others(self):
        content = b"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="teststring">
        <item quantity="one"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> den</item>
        <item quantity="few"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dny</item>
        <item quantity="many"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
        <item quantity="other"><xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2" id="count">%d</xliff:g> dnu</item>
    </plurals>
</resources>"""
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

    def test_markup_quotes_set(self):
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Test</string>
</resources>"""
        content = template.encode()
        newcontent = template.replace(
            ">Test<", ">Test <b>string</b> with \\u0020space<"
        )
        store = self.StoreClass()
        store.parse(content)
        assert bytes(store) == content
        store.units[0].target = "Test <b>string</b> with  space"
        assert bytes(store).decode() == newcontent

    def test_xliff_g(self):
        template = """<?xml version="1.0" encoding="utf-8"?>
<resources>
</resources>"""
        original = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Test: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g></string>
</resources>"""
        expected = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="id">Other: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g></string>
</resources>"""
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

    def test_xliff_namespace(self):
        original = """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <string name="id">Test</string>
</resources>"""
        expected = """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    <string name="id">Test: <xliff:g>%s</xliff:g></string>
</resources>"""
        store = self.StoreClass()
        store.parse(original.encode())
        assert bytes(store).decode() == original
        store.units[
            0
        ].target = """Test: <xliff:g xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">%s</xliff:g>"""
        # The namespace should be flattened as it is defined in the toplevel element
        assert bytes(store).decode() == expected

    def test_edit_plural_zh_hk(self):
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>"""
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
</resources>"""
        )

    def test_edit_plural_b_zh_hk(self):
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>"""
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
</resources>"""
        )

    def test_missing_plural(self):
        content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="vms_num_visitors">
        <item quantity="one">%d visitor</item>
        <item quantity="other">%d visitors</item>
    </plurals>
</resources>"""
        store = self.StoreClass()
        store.targetlanguage = "fr"
        store.parse(content.encode())
        assert store.units[0].target == multistring(["%d visitor", "", "%d visitors"])
